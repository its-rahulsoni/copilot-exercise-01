// Script loaded
console.log("app.js script loaded");

// Try to run immediately
console.log("Running immediately");
const activitiesList = document.getElementById("activities-list");
console.log("activitiesList found:", activitiesList);

if (activitiesList) {
  activitiesList.innerHTML = "TEST: Found activitiesList element";
  fetchActivities();
}

document.addEventListener("DOMContentLoaded", () => {
  console.log("DOMContentLoaded fired");

  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  console.log("DOM elements found:", { activitiesList, activitySelect, signupForm, messageDiv });

  // Helper to show a transient status message
  function showMessage(text, type) {
    messageDiv.textContent = text;
    messageDiv.className = type;
    messageDiv.classList.remove("hidden");

    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }

  // Remove a participant from an activity
  async function removeParticipant(activityName, email) {
    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activityName)}/participants?email=${encodeURIComponent(email)}`,
        { method: "DELETE" }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        await fetchActivities();
      } else {
        showMessage(result.detail || "Unable to remove participant", "error");
      }
    } catch (error) {
      showMessage("Failed to remove participant. Please try again.", "error");
      console.error("Error removing participant:", error);
    }
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      console.log("Starting fetchActivities");
      const response = await fetch("/activities");
      console.log("Fetch response status:", response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const activities = await response.json();
      console.log("Fetched activities:", activities);
      console.log("activitiesList element:", activitiesList);

      // Clear loading message
      activitiesList.innerHTML = "TEST: JavaScript is working";

      // Reset select options
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        console.log(`Rendering activity: ${name}, participants:`, details.participants);

        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        const participantsHTML = details.participants.length > 0
          ? `<ul class="participant-list">${details.participants.map(participant =>
              `<li>${participant} <button class="delete-participant-btn" title="Remove participant" data-activity="${name}" data-email="${participant}">🗑️</button></li>`
            ).join('')}</ul>`
          : '<p class="no-participants">No participants yet</p>';

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <p><strong>Participants (${details.participants.length}):</strong></p>
            <p>TEST: This should be visible</p>
          </div>
        `;

        console.log("Generated HTML for participants section:", participantsHTML);

        // Add event listeners to delete buttons
        activityCard.querySelectorAll('.delete-participant-btn').forEach(btn => {
          btn.addEventListener('click', () => {
            const activity = btn.dataset.activity;
            const email = btn.dataset.email;
            removeParticipant(activity, email);
          });
        });

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
