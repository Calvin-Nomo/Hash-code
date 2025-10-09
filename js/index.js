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
const themeToggler = document.querySelector(".theme-toggler");
const body = document.body;
const lightIcon = themeToggler.querySelector("span:nth-child(1)");
const darkIcon = themeToggler.querySelector("span:nth-child(2)");

// Load saved theme from localStorage
if (localStorage.getItem("theme") === "dark") {
  body.classList.add("dark-theme-variables");
  lightIcon.classList.remove("active");
  darkIcon.classList.add("active");
}

themeToggler.addEventListener("click", () => {
  body.classList.toggle("dark-theme-variables");

  // Toggle icon active class
  lightIcon.classList.toggle("active");
  darkIcon.classList.toggle("active");

  // Save preference
  if (body.classList.contains("dark-theme-variables")) {
    localStorage.setItem("theme", "dark");
  } else {
    localStorage.setItem("theme", "light");
  }
});
document.addEventListener("DOMContentLoaded", function () {
  const langMenu = document.querySelector(".lang-menu");
  const selected = langMenu.querySelector(".selected-language");
  const options = langMenu.querySelectorAll(".lang-options a");
  // New side bar
  document.querySelectorAll(".dropdown-toggle").forEach((toggle) => {
    toggle.addEventListener("click", function (e) {
      e.preventDefault();
      const dropdown = this.parentElement;
      dropdown.classList.toggle("active");
    });
  });
  // Toggle dropdown
  selected.addEventListener("click", () => {
    langMenu.classList.toggle("active");
  });

  // Change selected language with flag
  options.forEach((option) => {
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

fetch("http://127.0.0.1:8000/order_info") // Replace with your API endpoint
  .then((res) => res.json())
  .then((data) => {
    const tbody = document.querySelector("#order-table tbody"); // Replace with your API endpoint
    tbody.innerHTML = ""; // clear any existing rows

    data.forEach((order) => {
      const row = document.createElement("tr");
      row.innerHTML = `
          <td>#${order.Order_ID}</td>
          <td>${order.Client_Name}</td>
          <td>${order.No_Telephone}</td>
          <td>${order.Order_Type}</td>
          <td>${order.Total_Amount} FCFA</td>
          <td>${order.Payment_Status}</td>
          <td>${new Date(order.Order_Date).toLocaleString()}</td>
        `;
      tbody.appendChild(row);
    });
  })
  .catch((err) => console.error("Error fetching orders:", err));
//Fetch Product from the backend(limit 15 from product_list.html)
fetch("http://127.0.0.1:8000/product/product/product_limit")
  .then((res) => res.json())
  .then((data) => {
    const tbody = document.querySelector("#product-table tbody");
    tbody.innerHTML = ""; // Clear any existing rows
    data.forEach((product) => {
      const row = document.createElement("tr");
      row.innerHTML = `
            <td>#${product.No_Product}</td>
            <td>${product.Image_Path}</td>
          <td>${product.Product_Name}</td>
          <td>${product.Product_Description}</td>
          <td>${product.Category}</td>  
          <td>${product.Unit_Price} FCFA</td>
            <td>
            <button class="edit-btn" onclick="editProduct(${product.No_Product})">
            <img src="image/pencil.png" alt="Edit" />
            </button>
            <button class="delete-btn" onclick="deleteProduct(${product.No_Product})">
            <img src="image/delete.png" alt="Delete" />
            </button>
          </td>
        `;
      tbody.appendChild(row);
    });
  })
  .catch((err) => console.error("Error fetching products:", err));
// updating the product in the inventory

// Fetch and display total orders from the backend
fetch("http://127.0.0.1:8000/order/order/total_order")
  .then((res) => res.json())
  .then((data) => {
    const totalOrderElement = document.getElementById("total_order");
    totalOrderElement.textContent = `${data.total}`;
  })
  .catch((err) => console.error("Error fetching total orders:", err));
document.addEventListener("DOMContentLoaded", () => {
  fetch("http://127.0.0.1:8000/payment/payment/total_revenue") // <-- your actual API endpoint
    .then((res) => {
      if (!res.ok) {
        throw new Error(`HTTP error! Status: ${res.status}`);
      }
      return res.json();
    })
    .then((data) => {
      console.log("Data received from backend:", data);

      const saleElement = document.getElementById("total-sales");

      if (saleElement) {
        if (data.total !== undefined) {
          // Optional: format the number to 2 decimal places
          saleElement.textContent = `${Number(data.total).toFixed(0)} FCFA`;
        } else {
          console.warn("No 'total' field in response data.");
          saleElement.textContent = "Total sale: N/A";
        }
      } else {
        console.warn("Element with ID 'total-sale' not found in DOM.");
      }
    })
    .catch((err) => {
      console.error("Error fetching total sales:", err);
    });
});

document.addEventListener("DOMContentLoaded", () => {
  // Fetch and display total reservations from the backend
  fetch("http://127.0.0.1:8000/reservation/reservation/total_reservations")
    .then((res) => {
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      return res.json();
    })
    .then((data) => {
      const totalReservationsElement =
        document.getElementById("total-reservation");
      if (totalReservationsElement) {
        totalReservationsElement.textContent = `${data.total}`;
      } else {
        console.warn("Element with ID 'reservation' not found in the DOM.");
      }
    })
    .catch((err) => {
      console.error("Error fetching total reservations:", err);
    });
});
