// static/js/alerts.js
async function fetchHistory() {
  try {
    const res = await fetch('/api/alerts_history');
    const data = await res.json();
    const body = document.getElementById('historyBody');
    body.innerHTML = '';
    data.forEach(a => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${a.time}</td>
        <td>${a.phone}</td>
        <td>${a.method}</td>
        <td class="small">${a.message}</td>
        <td>${a.sid || ''}</td>
      `;
      body.appendChild(tr);
    });
  } catch (e) {
    console.error('History fetch error', e);
  }
}

document.addEventListener('DOMContentLoaded', function () {
  // initial fetch and interval
  fetchHistory();
  setInterval(fetchHistory, 3000); // refresh every 3s

  // manual send
  document.getElementById('sendBtn').addEventListener('click', async () => {
    const phone = document.getElementById('phone').value.trim();
    let message = document.getElementById('message').value.trim();
    if (!phone) { alert('Enter phone'); return; }
    if (!message) {
      // set default manual message
      message = `HELP NEEDED: Please check the monitored location. Time: ${new Date().toLocaleString()}`;
    }
    document.getElementById('sendStatus').textContent = 'Sending...';

    try {
      const res = await fetch('/send_alert', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({phone, message})
      });
      const result = await res.json();
      if (result.status === 'ok') {
        document.getElementById('sendStatus').textContent = 'Sent ✔';
        // Clear inputs after successful send:
        document.getElementById('phone').value = ''; // UNCOMMENTED
        document.getElementById('message').value = ''; // UNCOMMENTED
      } else {
        document.getElementById('sendStatus').textContent = 'Error: ' + (result.message || 'send failed');
      }
    } catch (err) {
      document.getElementById('sendStatus').textContent = 'Network error';
    }
    // refresh history quickly
    fetchHistory();
  });
});
