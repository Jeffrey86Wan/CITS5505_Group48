document.addEventListener("DOMContentLoaded", function () {
    // User avatar dropdown menu
    const userAvatar = document.querySelector(".user-avatar");
    const userDropdownContent = document.querySelector(".user-dropdown-content");
    const userDropdown = document.querySelector(".user-dropdown");

    if (userAvatar && userDropdownContent) {
        let dropdownTimeout;

        // Click avatar to show/hide dropdown menu
        userAvatar.addEventListener("click", function (e) {
            e.stopPropagation();
            userDropdownContent.classList.toggle("hidden");
        });

        // Mouse enters avatar to show dropdown menu
        userDropdown.addEventListener("mouseenter", function () {
            clearTimeout(dropdownTimeout);
            userDropdownContent.classList.remove("hidden");
        });

        // Mouse leaves dropdown area with delay to hide menu, giving users more time to select
        userDropdown.addEventListener("mouseleave", function () {
            dropdownTimeout = setTimeout(() => {
                userDropdownContent.classList.add("hidden");
            }, 300); // 300ms delay, can be adjusted as needed
        });

        // Clear hide timer when mouse enters dropdown content area
        userDropdownContent.addEventListener("mouseenter", function () {
            clearTimeout(dropdownTimeout);
        });

        // Click elsewhere on the page to hide dropdown menu
        document.addEventListener("click", function () {
            userDropdownContent.classList.add("hidden");
        });

        // Prevent page click event when clicking on dropdown menu content
        userDropdownContent.addEventListener("click", function (e) {
            e.stopPropagation();
        });
    }

    // Flash message fade out effect
    const flashMessages = document.querySelectorAll(".flash-messages");
    if (flashMessages.length > 0) {
        flashMessages.forEach((message) => {
            setTimeout(() => {
                message.style.opacity = "0";
                message.style.transition = "opacity 0.5s ease";

                setTimeout(() => {
                    message.style.display = "none";
                }, 500);
            }, 3000);
        });
    }
});
