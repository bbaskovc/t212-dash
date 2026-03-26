
#!/usr/bin/env python3

"""
Flask-based website module for Homer template application.

Provides a Website class to create, configure, and run a Flask app
with options for debug mode, configuration modes, logging, and
threaded execution.

Author: Blaz Baskovc
Version: 1.0.0
"""

import os
import sys
import time
import logging
import utils
from flask import Flask
from threading import Thread
from flask_migrate import Migrate
from flask_minify import Minify
from pathlib import Path

# Add website folder to sys.path so relative imports work
sys.path.append(str(Path(__file__).parent))

try:
    from apps.config import config_dict
    from apps import create_app, db
except ImportError as e:
    raise ImportError(f"Failed to import required modules: {e}. Make sure you're running from the correct directory.") from e


class FlaskHomer:
    """
    Flask-based website for Homer template application.

    Attributes:
        app (Flask): The Flask application instance.
        app_config (object): Configuration object for the Flask app.
        DEBUG (bool): Debug mode flag.
        logger (Logger): Logger instance for logging.
        migrate (Migrate): Flask-Migrate instance for database migrations.
    """

    def __init__(
        self,
        debug: bool | None = None,
        config_mode: str | None = None,
        log_level: str | None = None,
    ):
        """
        Initialize the Website instance.

        Args:
            debug (bool, optional):         Override debug mode. If None, uses DEBUG environment variable.
            config_mode (str, optional):    Configuration mode ('Debug' or 'Production'). If None, determined by debug setting.
            log_level (str, optional):      Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR').

        Raises:
            ValueError: If an invalid config_mode is provided.
            RuntimeError: If there are issues creating the Flask app.

        Returns:
            None
        """

        # WARNING: Don't run with debug turned on in production!
        if debug is not None:
            self.DEBUG = debug
        else:
            self.DEBUG = os.getenv("DEBUG", "False") == "True"

        # Setup logging
        self._setup_logging(log_level)

        if config_mode is not None:
            get_config_mode = config_mode
        else:
            get_config_mode = "Debug" if self.DEBUG else "Production"

        # Load the configuration using the default values
        try:
            self.app_config = config_dict[get_config_mode.capitalize()]
        except KeyError as e:
            raise ValueError(f"Invalid config_mode '{config_mode}'. Expected values [Debug, Production]") from e
        except Exception as e:
            raise RuntimeError(f"Failed to load configuration: {e}") from e

        # Create Flask app
        try:
            self.app = create_app(self.app_config)
            self.migrate = Migrate(self.app, db)
        except Exception as e:
            raise RuntimeError(f"Failed to create Flask app: {e}") from e

        # Apply minification in production
        if not self.DEBUG:
            try:
                Minify(app=self.app, html=True, js=False, cssless=False)
            except Exception:
                pass
                # logging.warning(f"Failed to setup minification: {e}")

        # Log configuration info
        if self.DEBUG:
            self.logger.info("DEBUG            = " + str(self.DEBUG))
            self.logger.info("Page Compression = " + ("FALSE" if self.DEBUG else "TRUE"))
            self.logger.info("DBMS             = " + self.app_config.SQLALCHEMY_DATABASE_URI)
            self.logger.info("ASSETS_ROOT      = " + self.app_config.ASSETS_ROOT)

        self._running_thread = None

    def _setup_logging(self, log_level: int | str = logging.INFO) -> None:
        """
        Setup logging configuration for the logger.

        Args:
            log_level (int): Logging level (e.g., logging.DEBUG, logging.INFO).

        Returns:
            None
        """
        if log_level is None:
            log_level = "DEBUG" if self.DEBUG else "INFO"

        if isinstance(log_level, str):
            log_level = getattr(logging, log_level.upper(), logging.INFO)

        # Get the existing logger (configured in __main__) or create a simple one
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)

    def set_log_level(self, level: int = logging.INFO) -> None:
        """
        Set the logging level for the logger.

        Args:
            level (int): Logging level (e.g., logging.DEBUG, logging.INFO).

        Returns:
            None
        """
        self.logger.setLevel(level)
        pass

    def run_threaded(self, host="127.0.0.1", port=8080) -> Thread:
        """
        Start Flask app in a separate thread.

        Args:
            host (str): Host to bind to.
            port (int): Port to bind to.

        Raises:
            Exception: If the Flask app fails to start.

        Returns:
            Thread: The thread running the Flask app.
        """
        if self._running_thread and self._running_thread.is_alive():
            self.logger.warning("Website is already running in a thread")
            return self._running_thread

        try:
            self._running_thread = Thread(
                target=self.app.run,
                kwargs={
                    "host": host,
                    "port": port,
                    "debug": self.DEBUG,
                    "use_reloader": False,
                },
            )
            self._running_thread.daemon = True  # Allow program to exit even if thread is running.
            self._running_thread.start()
            self.logger.error(f"Website started on {host}:{port} in background thread.")
            self.logger.debug(f"Website configuration: {self.get_config()}")
            return self._running_thread
        except Exception as e:
            self.logger.error(f"Failed to start website in thread: {e}")
            raise

    def run(self, host="127.0.0.1", port=8080) -> None:
        """
        Start Flask app in the main thread (blocking).

        Args:
            host (str): Host to bind to.
            port (int): Port to bind to.

        Raises:
            Exception: If the Flask app fails to start.

        Returns:
            None
        """
        try:
            self.logger.info(f"Starting website on {host}:{port}")
            self.app.run(host=host, port=port, debug=self.DEBUG)
        except Exception as e:
            self.logger.error(f"Failed to start website: {e}")
            raise

    def get_app(self) -> Flask:
        """
        Return the Flask app instance for external use.

        Returns:
            Flask: The Flask application instance.
        """
        return self.app

    def is_running(self) -> bool:
        """
        Check if the website is running in a thread

        Returns:
            bool: True if running in a thread, False otherwise.
        """

        return self._running_thread is not None and self._running_thread.is_alive()

    def stop(self) -> bool:
        """
        Stop the website if running in a thread.

        Returns:
            bool: True if stopped successfully or not running, False otherwise.
        """
        if self._running_thread and self._running_thread.is_alive():
            self.logger.info("Stopping website...")
            # Note: Flask doesn't have a clean way to stop from another thread
            # This is a limitation of Flask's built-in server
            self.logger.warning("Cannot cleanly stop Flask dev server from another thread.")
            return False
        return True

    def get_config(self) -> dict:
        """
        Return the current configuration

        Returns:
            dict: Current configuration details.
        """
        return {
            "debug": self.DEBUG,
            "config_mode": "Debug" if self.DEBUG else "Production",
            "database_uri": self.app_config.SQLALCHEMY_DATABASE_URI,
            "assets_root": self.app_config.ASSETS_ROOT,
            "running": self.is_running(),
        }


def create_website(debug=None, config_mode=None, log_level=None) -> FlaskHomer:
    """
    Factory function to create a Website instance.

    Args:
        debug (bool, optional): Override debug mode. If None, uses DEBUG environment variable.
        config_mode (str, optional): Configuration mode ('Debug' or 'Production').
                                   If None, determined by debug setting.
        log_level (str, optional): Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR').

    Returns:
        FlaskHomer: Configured FlaskHomer instance
    """
    return FlaskHomer(debug=debug, config_mode=config_mode, log_level=log_level)


def main_thread():
    """
    Main application thread doing other work.
    """

    try:
        while True:
            print(f"Main thread is running at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"Main thread is running at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting application.")
        web.stop()


# Example usage when run as a script.
if __name__ == "__main__":
    # Setup logging
    logger = utils.setup_logging(log_level=logging.INFO, logger_name=__name__, console=False)

    logger.info("🌍 Starting website...")

    # Create website instance and run threaded.
    web = FlaskHomer(log_level="DEBUG")
    thread = web.run_threaded(host="0.0.0.0", port=5000)

    logger.info("🚀 Starting application...")

    # Expose app for Gunicorn (Render)
    app = FlaskHomer().app

    # Main application can continue here.
    main_thread()

    # Exit application
    sys.exit(0)
