let sideMenu = document.querySelector("aside");
let Theme_Change = document.querySelector(".theme-toggler");
let openBtn = document.getElementById("menu-btn");
let closeBtn = document.getElementById("close-btn");

// Hide and Show the Side bar
openBtn.addEventListener("click", () => {
  sideMenu.style.display = "block";
});
closeBtn.addEventListener("click", () => {
  sideMenu.style.display = "none";
});

Theme_Change.addEventListener("click", () => {
  document.body.classList.toggle("dark-theme-variables");
  Theme_Change.querySelector("span:nth-child(1)").classList.toggle("activate");
  Theme_Change.querySelector("span:nth-child(2)").classList.toggle("activate");
});
