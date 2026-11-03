document.addEventListener("DOMContentLoaded", function() {
    const menuToggle = document.getElementById("menu-toggle");
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("overlay");
    const sidebarClose = document.getElementById("sidebar-close");
    const navLinks = document.querySelectorAll(".sidebar .nav-link");

    function openSidebar() {
        if (sidebar) sidebar.classList.add("active");
        if (overlay) overlay.classList.add("active");
    }

    function closeSidebar() {
        if (sidebar) sidebar.classList.remove("active");
        if (overlay) overlay.classList.remove("active");
    }

    function toggleSidebar() {
        if (sidebar && sidebar.classList.contains("active")) {
            closeSidebar();
        } else {
            openSidebar();
        }
    }

    if (menuToggle) {
        menuToggle.addEventListener("click", toggleSidebar);
    }

    if (sidebarClose) {
        sidebarClose.addEventListener("click", closeSidebar);
    }

    if (overlay) {
        overlay.addEventListener("click", closeSidebar);
    }

    // Auto-close drawer on navigation when on mobile/tablet viewports
    navLinks.forEach(link => {
        link.addEventListener("click", () => {
            if (window.innerWidth <= 991) {
                closeSidebar();
            }
        });
    });

    // Close on Escape key
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            closeSidebar();
        }
    });

    // Handle resize: if resized to desktop width, remove mobile active overlay
    window.addEventListener("resize", () => {
        if (window.innerWidth > 991 && overlay && overlay.classList.contains("active")) {
            overlay.classList.remove("active");
        }
    });
});