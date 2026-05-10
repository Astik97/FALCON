document.addEventListener("DOMContentLoaded", () => {
    // 1. Find the button and icon on whatever page we are currently on
    const themeToggleBtn = document.getElementById("theme-toggle");
    const themeIcon = themeToggleBtn ? themeToggleBtn.querySelector("i") : null;
    const body = document.body;

    // 2. This function actually does the work of changing the colors and the icon
    function applyTheme(theme) {
        if (theme === "light") {
            body.classList.add("light-theme");
            if (themeIcon) {
                themeIcon.classList.remove("fa-sun");
                themeIcon.classList.add("fa-moon");
            }
        } else {
            body.classList.remove("light-theme");
            if (themeIcon) {
                themeIcon.classList.remove("fa-moon");
                themeIcon.classList.add("fa-sun");
            }
        }
    }

    // 3. When the page first loads, check browser memory for the saved theme
    const currentTheme = localStorage.getItem("theme") || "dark"; 
    applyTheme(currentTheme);

    // 4. If the page has a toggle button, listen for clicks
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener("click", () => {
            // Figure out what the *new* theme should be
            const newTheme = body.classList.contains("light-theme") ? "dark" : "light";
            
            // Save it to memory and apply it
            localStorage.setItem("theme", newTheme); 
            applyTheme(newTheme); 
        });
    }

    // 5. MAGIC TRICK: Keep multiple browser tabs perfectly synced instantly
    window.addEventListener('storage', (event) => {
        if (event.key === 'theme') {
            applyTheme(event.newValue);
        }
    });
});