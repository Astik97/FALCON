  let previousDetectionCount = -1; // Keep track of how many items we have

    async function fetchDetections() {
      try {
        const res = await fetch('/api/detections');
        const detections = await res.json();
        const container = document.getElementById('detections');

        // UX FIX: Only rebuild the DOM if new detections arrived!
        if (detections.length === previousDetectionCount) {
            return; // Exit early if nothing has changed
        }
        
        previousDetectionCount = detections.length;
        container.innerHTML = ''; // Only clear when we have new data to show

        if (detections.length === 0) {
          container.innerHTML = '<p>No detected weapons yet.</p>';
          return;
        }

      detections.slice().reverse().forEach(det=> {
          const card = document.createElement('div');
          card.classList.add('detection-card');

          // BUG 1 FIX: Prepend the correct Flask route to the filename
          const rawImageName = det.file;
          const rawVideoName = det.video_file;
          
          const imageUrl = `/media/output/${rawImageName}`; 
          
          // Start building the HTML card
          let cardHTML = `
          <div class="detection-info">
            <h3> ${det.weapon_name} Detected</h3>
            <p><strong>Confidence:</strong><span class="highlight"> ${det.confidence}</span></p>
            <p><strong>Time:</strong> ${det.time}</p>
            <p><strong>Camera:</strong> ${det.camera}</p>
          </div>
          <div class="detection-media">
            <p class="media-label">Image:</p>
            <img src="${imageUrl}" alt="Detected Weapon Image" class="detection-image" height="240px" width="320px">
          </div>
          `;

          // BUG 2 FIX: Safely check for video, and prepend the route ONLY if it exists
          if (rawVideoName && rawVideoName !== "null" && rawVideoName !== "None") {

              const videoUrl = `/media/output/${rawVideoName}`;

              cardHTML += `
              <div class="detection-media">
                <p class="media-label">Video:</p>
                <video controls class="detection-video" height="240px" width="320px">
                  <source src="${videoUrl}" type="video/webm">
                  Your browser does not support the video tag.
                </video>
              </div>
              `;
          }

          // Inject the combined HTML into the card
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