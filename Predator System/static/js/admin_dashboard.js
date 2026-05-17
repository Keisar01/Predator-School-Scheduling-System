const adminSearchInput = document.getElementById("adminEventSearch");
const adminRows = Array.from(document.querySelectorAll(".admin-event-row"));
const adminEmptySearch = document.getElementById("adminEmptySearch");
const adminDeleteForms = Array.from(document.querySelectorAll(".admin-delete-form"));

if (adminSearchInput) {
  adminSearchInput.addEventListener("input", (event) => {
    const query = event.target.value.trim().toLowerCase();
    let visibleCount = 0;

    adminRows.forEach((row) => {
      const searchableText = row.dataset.event || "";
      const shouldShow = searchableText.includes(query);
      row.classList.toggle("hidden", !shouldShow);
      if (shouldShow) visibleCount += 1;
    });

    if (adminEmptySearch) {
      adminEmptySearch.classList.toggle("hidden", visibleCount !== 0);
    }
  });
}

adminDeleteForms.forEach((form) => {
  form.addEventListener("submit", (event) => {
    const ok = window.confirm("Delete this event?");
    if (!ok) event.preventDefault();
  });
});

document.addEventListener("DOMContentLoaded", function () {

    /* =====================
       LOGOUT
    ===================== */
    const logoutModal = document.getElementById("logoutModal");

    document.querySelectorAll(".logout-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.preventDefault(); // ❗ THIS IS THE FIX

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

    document.getElementById("cancelLogout").addEventListener("click", () => {
        logoutModal.classList.add("hidden");
    });

    /* =====================
       DELETE EVENT
    ===================== */
    const deleteModal = document.getElementById("deleteModal");
    const confirmDelete = document.getElementById("confirmDelete");

    document.querySelectorAll(".delete-event-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            confirmDelete.href = btn.dataset.url;
            deleteModal.classList.remove("hidden");
            deleteModal.classList.add("flex");
        });
    });

    document.getElementById("cancelDelete").addEventListener("click", () => {
        deleteModal.classList.add("hidden");
    });

    /* =====================
       DELETE USER
    ===================== */
    const userModal = document.getElementById("deleteUserModal");
    const confirmUserDelete = document.getElementById("confirmUserDelete");

    document.querySelectorAll(".delete-user-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            confirmUserDelete.href = btn.dataset.url;
            userModal.classList.remove("hidden");
            userModal.classList.add("flex");
        });
    });

    document.getElementById("cancelUserDelete").addEventListener("click", () => {
        userModal.classList.add("hidden");
    });

    /* =====================
       MAKE ADMIN (NEW)
    ===================== */
    const makeAdminModal = document.getElementById("makeAdminModal");
    const confirmMakeAdmin = document.getElementById("confirmMakeAdmin");

    document.querySelectorAll(".make-admin-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            confirmMakeAdmin.href = btn.dataset.url;
            makeAdminModal.classList.remove("hidden");
            makeAdminModal.classList.add("flex");
        });
    });

    document.getElementById("cancelMakeAdmin").addEventListener("click", () => {
        makeAdminModal.classList.add("hidden");
    });

});