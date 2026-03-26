"""
Utils.py

Collection of utility functions for common project tasks.
"""

import logging
import sys
import json
import utils
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from typing import Dict, Any, Union


def get_timezone_short_name(timezone: str | ZoneInfo | None = None) -> str:
    """Return a short timezone name like CET, CEST, UTC, GMT… safely on all OS.

    Args:
        timezone: Optional timezone as string (e.g., 'Europe/Paris') or ZoneInfo object.
                  If None, uses local timezone.

    Returns:
        Short timezone name.
    """
    if timezone is None:
        now = datetime.now().astimezone()
    elif isinstance(timezone, str):
        now = datetime.now(ZoneInfo(timezone))
    else:
        now = datetime.now(timezone)

    # Try direct abbreviation
    abbrev = now.tzname()
    if abbrev:
        # Extract uppercase letters only (e.g., "Central European Time" -> "CET")
        short = "".join(c for c in abbrev if c.isupper())
        if short:
            return short

    # Fallback: use %Z formatting which often gives shorter codes
    short = now.strftime("%Z")
    if short and short != abbrev:
        return short

    # Final fallback: compute GMT offset
    utc_offset = now.utcoffset()
    if utc_offset is None:
        return "GMT+00:00"
    
    offset_sec = utc_offset.total_seconds()
    hours = int(offset_sec // 3600)
    minutes = int((offset_sec % 3600) // 60)
    
    return f"GMT{hours:+03d}:{minutes:02d}"


def setup_logging(
    log_level: int = logging.INFO, 
    log_file: Union[str, Path, None] = None,
    console: bool = True,
    logger_name: str = None
) -> logging.Logger:
    """
    Setup logging with colored output, relative paths, and timezone offset (+01:00).

    Args:
        log_level: Logging level (e.g., logging.DEBUG, logging.INFO).
        log_file: Optional path to log file. If provided, logs will be written to file.
        console: Whether to log to console/terminal. Default True.
        logger_name: Name for the logger. If None, uses __name__.

    Returns:
        Configured logger instance.
    """

    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[35m",
        "RESET": "\033[0m",
        "TIME": "\033[90m",
        "FILE": "\033[33m",
    }

    LOGGING_FORMAT = "{asctime} | {levelname} | {filename} | {message}"
    PROJECT_ROOT = Path.cwd().resolve()

    class ColoredFormatter(logging.Formatter):
        def formatTime(self, record, datefmt=None):
            dt = datetime.fromtimestamp(record.created).astimezone()
            offset = dt.strftime("%z")  # e.g. +0100
            offsetFmt = offset[:3] + ":" + offset[3:]  # +01:00
            ms = int((record.created - int(record.created)) * 1000)
            return f"{dt.strftime('%Y-%m-%d %H:%M:%S')}.{ms:03d}{offsetFmt}"

        def format(self, record):
            record.asctime = self.formatTime(record, self.datefmt)
            # Add color to timestamp
            colored_asctime = f"{COLORS['TIME']}{record.asctime}{COLORS['RESET']}"
            record.asctime = colored_asctime

            origLevel = record.levelname
            origFilename = record.filename

            record.levelname = (
                f"{COLORS.get(origLevel, '')}{origLevel}{COLORS['RESET']}"
            )

            fullpath = Path(record.pathname).resolve()
            try:
                relpath = fullpath.relative_to(PROJECT_ROOT)
                record.filename = (
                    f"{COLORS['FILE']}{relpath}:{record.lineno}{COLORS['RESET']}"
                )
            except ValueError:
                # File is outside project directory, show package/module info
                if 'site-packages' in str(fullpath):
                    # Extract package name from site-packages path
                    parts = fullpath.parts
                    if 'site-packages' in parts:
                        pkg_idx = parts.index('site-packages') + 1
                        if pkg_idx < len(parts):
                            pkg_name = parts[pkg_idx]
                            record.filename = (
                                f"{COLORS['FILE']}{pkg_name}/{origFilename}:{record.lineno}{COLORS['RESET']}"
                            )
                        else:
                            record.filename = (
                                f"{COLORS['FILE']}{origFilename}:{record.lineno}{COLORS['RESET']}"
                            )
                    else:
                        record.filename = (
                            f"{COLORS['FILE']}{origFilename}:{record.lineno}{COLORS['RESET']}"
                        )
                else:
                    # For stdlib or other external files
                    record.filename = (
                        f"{COLORS['FILE']}{origFilename}:{record.lineno}{COLORS['RESET']}"
                    )

            formatted = super().format(record)

            record.levelname = origLevel
            record.filename = origFilename

            return formatted

    # Create a specific named logger (doesn't affect root logger or Flask)
    actual_logger_name = logger_name or __name__
    logger = logging.getLogger(actual_logger_name)
    logger.setLevel(log_level)
    
    # Clear any existing handlers to avoid duplicates  
    logger.handlers.clear()
    
    # Add console handler if requested
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(ColoredFormatter(LOGGING_FORMAT, style="{"))
        logger.addHandler(console_handler)
    
    # Add file handler if log_file is provided
    if log_file:
        log_path = Path(log_file)
        # Create directory if it doesn't exist
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Custom formatter for file that handles time formatting
        class FileFormatter(logging.Formatter):
            def formatTime(self, record, datefmt=None):
                dt = datetime.fromtimestamp(record.created).astimezone()
                offset = dt.strftime("%z")  # e.g. +0100
                offsetFmt = offset[:3] + ":" + offset[3:]  # +01:00
                ms = int((record.created - int(record.created)) * 1000)
                return f"{dt.strftime('%Y-%m-%d %H:%M:%S')}.{ms:03d}{offsetFmt}"
            
            def format(self, record):
                record.asctime = self.formatTime(record, self.datefmt)
                
                # For file logging, show full path relative to project root
                fullpath = Path(record.pathname).resolve()
                try:
                    relpath = fullpath.relative_to(PROJECT_ROOT)
                    record.pathname = str(relpath)
                except ValueError:
                    # File is outside project directory, use original path
                    pass
                
                return super().format(record)
        
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setFormatter(FileFormatter(
            "{asctime} | {levelname} | {pathname}:{lineno} | {message}",
            style="{"
        ))
        logger.addHandler(file_handler)
    
    # Prevent propagation to avoid interfering with Flask logging
    logger.propagate = False
    
    # Return the configured logger
    return logger


def read_json_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Read JSON file and return its content as a dictionary.

    Args:
        file_path: Path to the JSON file as string or Path object.

    Returns:
        Dictionary containing the JSON data.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        json.JSONDecodeError: If the file contains invalid JSON.
        PermissionError: If the file cannot be read due to permissions.
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")
    
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in file {path}: {str(e)}", e.doc, e.pos)
    except PermissionError:
        raise PermissionError(f"Permission denied reading file: {path}")
