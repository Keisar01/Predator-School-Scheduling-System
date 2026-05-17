const searchInput = document.getElementById("eventSearch");
const cards = Array.from(document.querySelectorAll(".event-card"));
const emptySearch = document.getElementById("emptySearch");
const deleteForms = Array.from(document.querySelectorAll(".delete-event-form"));

if (searchInput) {
  searchInput.addEventListener("input", (event) => {
    const query = event.target.value.trim().toLowerCase();
    let visibleCount = 0;

    cards.forEach((card) => {
      const searchableText = card.dataset.event || "";
      const shouldShow = searchableText.includes(query);
      card.classList.toggle("hidden", !shouldShow);
      if (shouldShow) visibleCount += 1;
    });

    if (emptySearch) {
      emptySearch.classList.toggle("hidden", visibleCount !== 0);
    }
  });
}

deleteForms.forEach((form) => {
  form.addEventListener("submit", (event) => {
    const ok = window.confirm("Delete this event?");
    if (!ok) event.preventDefault();
  });
});

document.addEventListener("DOMContentLoaded", function () {

    /* =====================
       LOGOUT MODAL
    ===================== */
    const logoutModal = document.getElementById("logoutModal");

    document.querySelectorAll(".logout-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.preventDefault();

            logoutModal.classList.remove("hidden");
            logoutModal.classList.add("flex");
        });
    });

    const cancelLogout = document.getElementById("cancelLogout");

    if (cancelLogout) {
        cancelLogout.addEventListener("click", () => {
            logoutModal.classList.add("hidden");
            logoutModal.classList.remove("flex");
        });
    }


    /* =====================
       DELETE EVENT MODAL (FIXED)
    ===================== */
    const deleteModal = document.getElementById("deleteEventModal");
    const confirmDelete = document.getElementById("confirmDeleteEvent");
    const cancelDelete = document.getElementById("cancelDeleteEvent");

    document.querySelectorAll(".delete-event-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            confirmDelete.href = btn.dataset.url;

            deleteModal.classList.remove("hidden");
            deleteModal.classList.add("flex");
        });
    });

    if (cancelDelete) {
        cancelDelete.addEventListener("click", () => {
            deleteModal.classList.add("hidden");
            deleteModal.classList.remove("flex");
        });
    }

});