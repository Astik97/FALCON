// static/js/alerts.js
async function fetchHistory() {
  try {
    const res = await fetch('/api/alerts_history');
    const data = await res.json();
    const body = document.getElementById('historyBody');
    if (!body) return;
    body.innerHTML = '';

    if (!data || data.length === 0) {
      body.innerHTML = '<tr><td colspan="5" style="text-align:center; color: var(--text-muted); padding: 1.5rem;">No alert history found.</td></tr>';
      return;
    }

    data.forEach(a => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${a.time || ''}</td>
        <td>${a.phone || ''}</td>
        <td>${a.method || ''}</td>
        <td class="small">${a.message || ''}</td>
        <td style="font-family: monospace; font-size: 0.8rem;">${a.sid || ''}</td>
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

  // manual send (safely guarded if elements exist)
  const sendBtn = document.getElementById('sendBtn');
  if (sendBtn) {
    sendBtn.addEventListener('click', async () => {
      const phoneInput = document.getElementById('phone');
      const msgInput = document.getElementById('message');
      const statusEl = document.getElementById('sendStatus');
      
      const phone = phoneInput ? phoneInput.value.trim() : '';
      let message = msgInput ? msgInput.value.trim() : '';

      if (!phone) {
        alert('Please enter a phone number'); 
        return; 
      }

      if (!message) {
        message = `HELP NEEDED: Please check the monitored location. Time: ${new Date().toLocaleString()}`;
      }

      if (statusEl) statusEl.textContent = 'Sending...';
      
      try {
        const res = await fetch('/send_alert', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({phone, message})
        });

        const result = await res.json();
        if (result.status === 'ok') {
          if (statusEl) statusEl.textContent = 'Sent ✔';
          if (phoneInput) phoneInput.value = '';
          if (msgInput) msgInput.value = '';
        } else {
          if (statusEl) statusEl.textContent = 'Error: ' + (result.message || 'send failed');
        }
      } catch (err) {
        if (statusEl) statusEl.textContent = 'Network error';
      }

      fetchHistory();
    });
  }
});