// Opens and closes the menu on small phone screens
const menu = document.getElementById("menu");
const nav = document.getElementById("nav");
if (menu && nav) menu.addEventListener("click", () => nav.classList.toggle("open"));
