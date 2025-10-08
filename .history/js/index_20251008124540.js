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
// Language Dropdown Menu
let langMenu = document.querySelector(".lang-menu");
let selectedLang = langMenu.querySelector(".selected-language");
let langOptions = langMenu.querySelector(".lang-options");
selectedLang.addEventListener("click", () => {
  langOptions.classList.toggle("active");
});
langOptions.querySelectorAll("li").forEach((option) => {
  option.addEventListener("click", () => {
    selectedLang.innerHTML = option.innerHTML;
    langOptions.classList.remove("active");
  });
});
// display the selected flag in the selected language section
selectedLang.addEventListener("click", () => {
  let selectedFlag = selectedLang.querySelector("img").src;
  selectedLang.style.backgroundImage = `url(${selectedFlag})`;
});
// Close the dropdown menu if the user clicks outside of it
window.addEventListener("click", (e) => {
  if (!langMenu.contains(e.target)) {
    langOptions.classList.remove("active");
  }

});
// Hide and Show the Side bar
selectedLang.addEventListener("click", () => {
  langOptions.style.display = "block";
});
// Toogle the active class in the sidebar
let allSideMenu = document.querySelectorAll("aside .side-menu li a");
allSideMenu.forEach((item) => {
  const li = item.parentElement;
  item.addEventListener("click", () => {
    allSideMenu.forEach((i) => {
      i.parentElement.classList.remove("active");
    });
    li.classList.add("active");
  }
  );
});
// Change the active page title
let allPageTitle = document.querySelectorAll(".page-title");
allSideMenu.forEach((item) => {
  item.addEventListener("click", () => {
    let text = item.textContent;
    allPageTitle.forEach((title) => {
      title.textContent = text;
    });
  });
}
);