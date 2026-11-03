// static/js/theme.js
(function () {
    // 1. Function to apply theme to documentElement and body
    function applyTheme(theme) {
        const isLight = (theme === "light");
        
        if (isLight) {
            document.documentElement.classList.add("light-theme");
            if (document.body) {
                document.body.classList.add("light-theme");
            }
        } else {
            document.documentElement.classList.remove("light-theme");
            if (document.body) {
                document.body.classList.remove("light-theme");
            }
        }

        // Update toggle button icon if this page has one (e.g. Dashboard)
        const themeToggleBtn = document.getElementById("theme-toggle");
        if (themeToggleBtn) {
            const themeIcon = themeToggleBtn.querySelector("i");
            if (themeIcon) {
                if (isLight) {
                    themeIcon.classList.remove("fa-sun");
                    themeIcon.classList.add("fa-moon");
                } else {
                    themeIcon.classList.remove("fa-moon");
                    themeIcon.classList.add("fa-sun");
                }
            }
        }
    }

    // 2. Immediate execution: applies theme right away to prevent any flash of dark theme
    const savedTheme = localStorage.getItem("theme") || "dark";
    applyTheme(savedTheme);

    // 3. When DOM is ready, sync body and attach toggle button handler if present
    document.addEventListener("DOMContentLoaded", function () {
        const currentTheme = localStorage.getItem("theme") || "dark";
        applyTheme(currentTheme);

        const themeToggleBtn = document.getElementById("theme-toggle");
        if (themeToggleBtn) {
            themeToggleBtn.addEventListener("click", function () {
                const current = localStorage.getItem("theme") || "dark";
                const nextTheme = (current === "light") ? "dark" : "light";
                localStorage.setItem("theme", nextTheme);
                applyTheme(nextTheme);
            });
        }
    });

    // 4. Real-time multi-tab/window synchronization
    window.addEventListener("storage", function (event) {
        if (event.key === "theme") {
            applyTheme(event.newValue || "dark");
        }
    });
})();
