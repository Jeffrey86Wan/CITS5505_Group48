/**
 * Common JavaScript for Auth Pages - Flash Message Handler
 * Used for managing messages on login and registration pages
 */
document.addEventListener("DOMContentLoaded", function () {
  // LocalStorage key for storing message state
  const FLASH_MESSAGE_KEY = "flash_message_shown";

  // Get current page URL path
  const currentPath = window.location.pathname;

  // Check if navigated from another auth page
  const previousPath = localStorage.getItem("auth_previous_page");
  if (previousPath && previousPath !== currentPath) {
    // If coming from another auth page, clear all existing messages
    clearAllFlashMessages();
  }

  // Update current page path
  localStorage.setItem("auth_previous_page", currentPath);

  // Get all flash messages
  const flashMessages = document.querySelectorAll(
    ".flash-message-auto-disappear"
  );

  // Process each message
  flashMessages.forEach((message) => {
    console.log("Processing flash message:", message.textContent);

    // Set auto-hide (after 5 seconds)
    setTimeout(() => {
      hideMessage(message);
    }, 5000);
  });

  // Listen for link clicks, clear messages when navigating to other auth pages
  document.querySelectorAll('a[href^="/auth/"]').forEach((link) => {
    link.addEventListener("click", function () {
      // Mark messages to be cleared - used in the next page
      localStorage.setItem("clear_auth_messages", "true");
    });
  });

  // Check if messages need to be cleared (navigated from another page)
  if (localStorage.getItem("clear_auth_messages") === "true") {
    clearAllFlashMessages();
    localStorage.removeItem("clear_auth_messages");
  }

  // Clear all flash messages
  function clearAllFlashMessages() {
    const messages = document.querySelectorAll(".flash-message-auto-disappear");
    messages.forEach((msg) => {
      if (msg.parentNode) {
        msg.parentNode.removeChild(msg);
      }
    });
  }

  // Function to hide a message
  function hideMessage(element) {
    // Add transition effect
    element.style.transition = "opacity 0.5s ease";
    element.style.opacity = "0";

    // Remove from DOM after transition completes
    setTimeout(() => {
      if (element.parentNode) {
        element.parentNode.removeChild(element);
      }
    }, 500);
  }
});
