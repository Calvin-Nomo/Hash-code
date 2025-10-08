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

document.addEventListener("DOMContentLoaded", function () {
  const langMenu = document.querySelector(".lang-menu");
  const selected = langMenu.querySelector(".selected-language");
  const options = langMenu.querySelectorAll(".lang-options a");

  // Toggle dropdown
  selected.addEventListener("click", () => {
    langMenu.classList.toggle("active");
  });

  // Change selected language with flag
  options.forEach(option => {
    option.addEventListener("click", (e) => {
      e.preventDefault();
      const flagUrl = option.getAttribute("data-flag");
      const langText = option.textContent.trim();

      // Update selected language display
      selected.innerHTML = `<img src="${flagUrl}" alt=""> ${langText} <i class="arrow down"></i>`;
      langMenu.classList.remove("active");
    });
  });

  // Close dropdown if clicking outside
  window.addEventListener("click", (e) => {
    if (!langMenu.contains(e.target)) {
      langMenu.classList.remove("active");
    }
  });
});
// Fetch and display orders from the backend

   fetch("http://localhost:5000/api/orders")  // Replace with your API endpoint
    .then(res => res.json())
    .then(data => {
      const tbody = document.querySelector("#order-table tbody");// Replace with your API endpoint
      tbody.innerHTML = ""; // clear any existing rows

      data.forEach(order => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>''${order.Order_ID}</td>
          <td>${order.Client_Name}</td>
          <td>${order.No_Telephone}</td>
          <td>${order.Order_Type}</td>
          <td>${order.Total_Amount}</td>
          <td>${order.Payment_Status}</td>
          <td>${new Date(order.Order_Date).toLocaleDateString()}</td>
        `;
        tbody.appendChild(row);
      });
    })
    .catch(err => console.error("Error fetching orders:", err));