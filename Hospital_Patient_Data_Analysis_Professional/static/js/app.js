document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.getElementById("sidebar");
    const menu = document.getElementById("menuBtn");
    if (menu) menu.addEventListener("click", () => sidebar.classList.toggle("open"));
});
