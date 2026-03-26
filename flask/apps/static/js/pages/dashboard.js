// Show Bootstrap Toast after 2 seconds
function showToast() {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = 1100;
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = 'toast text-bg-primary border-0 fade';
  toast.setAttribute('role', 'alert');
  toast.setAttribute('aria-live', 'assertive');
  toast.setAttribute('aria-atomic', 'true');

  toast.innerHTML = `
    <div class="toast-header bg-white bg-opacity-10 text-white border-0">
      <strong class="me-auto text-white">New Updates!</strong>
      <small>Now</small>
      <button type="button" class="ms-2 btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
    <div class="toast-body">
      Welcome to <strong>HOMER</strong> Bootstrap 5 Admin Dashboard Template.
    </div>
  `;

  container.appendChild(toast);

  const bsToast = new bootstrap.Toast(toast, { delay: 5000 });
  bsToast.show();

  toast.addEventListener('hidden.bs.toast', () => {
    toast.remove();
  });
}

setTimeout(showToast, 2000);


const activeUsersChart = new CustomChartJs({
  selector: '#activeUsersChart',
  options: () => ({
    type: 'line',
    data: {
      labels: ['0', '1', '2', '3', '4', '5', '6', '7'],
      datasets: [
        {
          label: 'Current Month',
          data: [50, 42, 38, 35, 40, 50, 48, 47],
          fill: true,
          borderColor: ins('chart-secondary'),
          backgroundColor: ins('chart-secondary-rgb', 0.2),
          tension: 0.4,
          pointRadius: 0,
          borderWidth: 1
        },
        {
          label: 'Past Month',
          data: [60, 55, 50, 45, 50, 58, 55, 53],
          fill: true,
          borderColor: ins('chart-gray'),
          backgroundColor: ins('chart-gray-rgb', 0.2),
          tension: 0.4,
          pointRadius: 0,
          borderWidth: 1
        }
      ]
    }
  })
});



// Income Chart (Line Chart)
const incomeChart = new CustomChartJs({
  selector: '#incomeChart',
  options: () => {
    return {
      type: 'line',
      data: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [{
          data: [0, 15, 10, 20, 18, 25, 30],
          backgroundColor: ins('chart-primary-rgb', 0.6),
          borderColor: ins('chart-primary'),
          tension: 0.4,
          fill: true,
          pointRadius: 0,
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: { enabled: false }
        },
        scales: {
          x: {
            display: false,
            grid: { display: false }
          },
          y: {
            display: false,
            grid: { display: false }
          }
        }
      }
    };
  }
});
