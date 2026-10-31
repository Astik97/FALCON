        function updateSystemTime() {
        const timeElement = document.getElementById('system-time');
        const now = new Date();
        
        // This formats the time to look like "10:30 AM" instead of a long messy string
        const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        timeElement.innerText = `Last Checked: ${timeString}`;
    }

    // Run the function immediately when the page loads
    updateSystemTime();

    // ==========================================
    // === 1. THIS IS THE NEW FUNCTION YOU NEED ===
    // ==========================================
    async function updateDashboardStats() {
        try {
            // 1. Fetch data from your API
            const response = await fetch('/api/detections');
            const detections = await response.json();

            // 2. Update the overview cards
            document.getElementById('total-incidents').innerText = detections.length;
            document.getElementById('detected-weapons').innerText = detections.length;
            
            // NOTE: This counts all detections as "active". 
            // We can improve this logic later if you want.
            document.getElementById('active-alerts').innerText = detections.length;

            // 3. Update the "Recent Alerts" table
            const tbody = document.querySelector('.recent-alerts tbody');
            tbody.innerHTML = ''; // Clear the old static rows from your HTML

            // Get just the top 5 most recent alerts
            const recentDetections = detections.slice(0, 5); 

            if (recentDetections.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">No recent alerts.</td></tr>';
            } else {
                recentDetections.forEach(det => {
                    const tr = document.createElement('tr');
                    
                    // Format the timestamp to be more readable
                    const timestamp = new Date(det.time).toLocaleString(); 
                    
                    tr.innerHTML = `
                        <td>${timestamp}</td>
                        <td>${det.location || 'N/A'}</td>
                        <td>${det.weapon || 'N/A'}</td>
                        <td><span class="status-new" style="color: #ffc107; font-weight: bold;">New</span></td> 
                        <td><a href="#">View</a></td>
                    `;
                    tbody.appendChild(tr);
                });
            }

        } catch (error) {
            console.error("Error updating dashboard stats:", error);
        }
    }
    
    // ==========================================
    // === (This is your existing code below) ===
    // ==========================================

    async function startDetection() {
        const btn = document.getElementById("detectBtn");
        btn.innerText = "Starting...";
        btn.disabled = true;

        const response = await fetch("/start-detection");
        const data = await response.json();
        alert(data.message);

        btn.innerText = "Start Detection";
        btn.disabled = false;
    }

    let page = 0;
    const pageSize = 12;
    let allFiles = [];

    // Fetch all files from backend
    async function loadFiles() {
        const res = await fetch('/api/files');
        allFiles = await res.json();
        showMore();
    }

    // Render files chunk by chunk as you scroll
    function showMore() {
        const grid = document.querySelector('.image-grid');
        const start = page * pageSize;
        const end = start + pageSize;
        const files = allFiles.slice(start, end);

        files.forEach(file => {
            const item = document.createElement('div');
            item.classList.add('weapon-image-item');

            if (file.type === 'video') {
                item.innerHTML = `
                    <video controls width="100" height="100" class="thumb-video">
                    <source src = "${file.url}" type="video/webm">
                    Your browser doesnot support the video tag
                    </video>
                    <div class="image-overlay">
                        <span class="timestamp">${file.name}</span>
                        <button class="overlay-btn"><i class="fas fa-play"></i></button>
                    </div>`;
            } else {
                item.innerHTML = `
                    <img src="${file.url}" alt="Weapon Image" width="100" height="100">
                    <div class="image-overlay">
                        <span class="timestamp">${file.name}</span>
                        <button class="overlay-btn"><i class="fas fa-eye"></i></button>
                    </div>`;
            }

            grid.appendChild(item);
        });

        page++;
    }

    // Auto load more when scrolling
    window.addEventListener('scroll', () => {
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 100) {
            showMore();
        }
    });

    // ========================================================
    // === 2. THESE ARE THE NEW LINES TO CALL THE FUNCTION ===
    // ========================================================
    
    // This was your existing line
    setInterval(loadFiles, 3000);

    // Add this new line to update stats
    setInterval(updateDashboardStats, 3000); 

    // This was your existing line
    loadFiles();

    // Add this new line to load stats on page load
    updateDashboardStats(); 