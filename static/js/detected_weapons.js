let previousDetectionCount = -1; // Keep track of how many items we have

async function fetchDetections() {
  try {
    const res = await fetch('/api/detections');
    const detections = await res.json();
    const container = document.getElementById('detections');
    if (!container) return;

    // UX FIX: Only rebuild the DOM if detection count has changed
    if (detections.length === previousDetectionCount) {
        return;
    }
    
    previousDetectionCount = detections.length;
    container.innerHTML = '';

    if (detections.length === 0) {
      container.innerHTML = '<div class="empty-state"><i class="fas fa-shield-alt"></i><p>No detected weapons yet.</p></div>';
      return;
    }

    detections.slice().reverse().forEach(det => {
      const card = document.createElement('div');
      card.classList.add('detection-card');

      const rawImageName = det.file;
      const rawVideoName = det.video_file;
      const imageUrl = `/media/output/${rawImageName}`; 
      
      let cardHTML = `
      <div class="detection-info">
        <h3><i class="fas fa-exclamation-triangle"></i> ${det.weapon_name || 'Weapon'} Detected</h3>
        <p><strong>Confidence:</strong> <span class="highlight">${det.confidence || 'N/A'}</span></p>
        <p><strong>Time:</strong> <span>${det.time || 'N/A'}</span></p>
        <p><strong>Camera:</strong> <span>${det.camera || 'Main Camera'}</span></p>
      </div>
      <div class="detection-media-group">
        <div class="detection-media">
          <p class="media-label">Image:</p>
          <img src="${imageUrl}" alt="Detected Weapon Image" class="detection-image" loading="lazy">
        </div>
      `;

      if (rawVideoName && rawVideoName !== "null" && rawVideoName !== "None") {
          const videoUrl = `/media/output/${rawVideoName}`;
          cardHTML += `
          <div class="detection-media">
            <p class="media-label">Video Clip:</p>
            <video controls class="detection-video" preload="metadata">
              <source src="${videoUrl}" type="video/webm">
              Your browser does not support the video tag.
            </video>
          </div>
          `;
      }

      cardHTML += `</div>`;
      card.innerHTML = cardHTML;
      container.appendChild(card);
    });
    
  } catch (error) {
    console.error('Error loading detections:', error);
  }
}

// Fetch immediately, then every 3 seconds
fetchDetections();
setInterval(fetchDetections, 3000);