/* =======================================================
   📂 DASHBOARD MAIN JAVASCRIPT
   Handles sidebar, theme, language, data fetching, search,
   and UI updates including product images.
   ======================================================= */

// =============== 🧭 SIDEBAR TOGGLE ===============
const sideMenu = document.querySelector("aside");
const openBtn = document.getElementById("menu-btn");
const closeBtn = document.getElementById("close-btn");

openBtn?.addEventListener("click", () => (sideMenu.style.display = "block"));
closeBtn?.addEventListener("click", () => (sideMenu.style.display = "none"));

// =============== 🌗 THEME TOGGLER ===============
const themeToggler = document.querySelector(".theme-toggler");
const body = document.body;
const lightIcon = themeToggler?.querySelector("span:nth-child(1)");
const darkIcon = themeToggler?.querySelector("span:nth-child(2)");

document.addEventListener("DOMContentLoaded", () => {
  try {
    const savedTheme = localStorage.getItem("theme");
    const isDark = savedTheme === "dark";
    body.classList.toggle("dark-theme-variables", isDark);
    lightIcon?.classList.toggle("active", !isDark);
    darkIcon?.classList.toggle("active", isDark);
  } catch (err) {
    console.warn("⚠️ localStorage access blocked:", err);
  }
});

themeToggler?.addEventListener("click", () => {
  const isDark = body.classList.toggle("dark-theme-variables");
  lightIcon?.classList.toggle("active", !isDark);
  darkIcon?.classList.toggle("active", isDark);

  try {
    localStorage.setItem("theme", isDark ? "dark" : "light");
  } catch (err) {
    console.warn("⚠️ localStorage write blocked:", err);
  }
});

// =============== 🌍 LANGUAGE MENU ===============
document.addEventListener("DOMContentLoaded", () => {
  const langMenu = document.querySelector(".lang-menu");
  const selected = langMenu?.querySelector(".selected-language");
  const options = langMenu?.querySelectorAll(".lang-options a");

  selected?.addEventListener("click", () =>
    langMenu?.classList.toggle("active")
  );

  options?.forEach((option) => {
    option.addEventListener("click", (e) => {
      e.preventDefault();
      const flagUrl = option.getAttribute("data-flag");
      const langText = option.textContent.trim();
      if (selected)
        selected.innerHTML = `<img src="${flagUrl}" alt=""> ${langText} <i class="arrow down"></i>`;
      langMenu?.classList.remove("active");
    });
  });

  window.addEventListener("click", (e) => {
    if (langMenu && !langMenu.contains(e.target))
      langMenu.classList.remove("active");
  });

  // Sidebar dropdown toggles
  document.querySelectorAll(".dropdown-toggle").forEach((toggle) => {
    toggle.addEventListener("click", (e) => {
      e.preventDefault();
      toggle.parentElement.classList.toggle("active");
    });
  });
});

// ================== 📊 FETCH ORDERS ==================
fetch("http://127.0.0.1:8000/order_info")
  .then((res) => res.json())
  .then((data) => {
    const tbody = document.querySelector("#order-table tbody");
    if (!tbody) return;
    tbody.innerHTML = "";
    data.forEach((order) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>#${order.Order_ID}</td>
        <td>${order.Client_Name}</td>
        <td>${order.Order_Type}</td>
        <td>${order.Total_Amount} FCFA</td>
        <td>${new Date(order.Order_Date).toLocaleString()}</td>
    <td class="action-cell">
  <!-- View Details -->
  <button class="action-btn view" title="View Details">
    <span class="material-icons-sharp">visibility</span>
  </button>
  <!-- Edit -->
  <button class="action-btn edit" title="Edit">
    <span class="material-icons-sharp">edit</span>
  </button>
  <!-- Delete -->
  <button class="action-btn delete" title="Delete" >
    <span class="material-icons-sharp">delete</span>
  </button>
</td>

      `;
      tbody.appendChild(row);
    });
  })
  .catch((err) => console.error("❌ Error fetching orders:", err));

// ================== 📦 FETCH PRODUCTS ==================
let allProducts = [];

function fetchProducts() {
  fetch("http://127.0.0.1:8000/product/product/Product")
    .then((res) => res.json())
    .then((data) => {
      allProducts = data;
      renderProducts(data);
    })
    .catch((err) => console.error("❌ Error fetching products:", err));
}

function renderProducts(products) {
  const tbody = document.querySelector("#product-table tbody");
  if (!tbody) return;
  tbody.innerHTML = "";

  products.forEach((product) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>#${product.No_Product}</td>
      <td><img src="${product.Image_link}"></td>
      <td>${product.Product_Name}</td>
      <td class="description">${product.Product_Description || ""}</td>
      <td>${product.Category}</td>
      <td>${product.Price} FCFA</td>
      <td class="action-cell">
  <!-- View Details -->
  <button class="action-btn view" title="View Details">
    <span class="material-icons-sharp">visibility</span>
  </button>
  <!-- Edit -->
  <button class="action-btn edit" title="Edit">
    <span class="material-icons-sharp">edit</span>
  </button>
  <!-- Delete -->
  <button class="action-btn delete" title="Delete">
    <span class="material-icons-sharp">delete</span>
  </button>
</td>


    `;

    //     <td>
    //   <button class="edit-btn" onclick="editProduct(${
    //     product.No_Product
    //   })">Edit</button>
    //   <button class="delete-btn" onclick="deleteProduct(${
    //     product.No_Product
    //   })">Delete</button>
    //     <td>
    //   ${
    //     product.Image_Path
    //       ? `<img src="${product.Image_Path}" alt="${product.Product_Name}" width="80"/>`
    //       : `<span>No Image</span>`
    //   }
    // </td>
    // </td>
    tbody.appendChild(row);
  });
}

// ================== 🛠 FETCH STOCK ==================
fetch("http://127.0.0.1:8000/stock/stock/Stock")
  .then((res) => res.json())
  .then((data) => {
    const tbody = document.querySelector("#stock-table tbody");
    if (!tbody) return;
    tbody.innerHTML = "";
    data.forEach((stock) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>#${stock.No_Stock}</td>
        <td>${stock.Product_Name}</td>
        <td>${stock.Quantity_Available}</td>
<td class="action-cell">
  <!-- View Details -->
  <button class="action-btn view" title="View Details">
    <span class="material-icons-sharp">visibility</span>
  </button>
  <!-- Edit -->
  <button class="action-btn edit" title="Edit">
    <span class="material-icons-sharp">edit</span>
  </button>
  <!-- Delete -->
  <button class="action-btn delete" title="Delete">
    <span class="material-icons-sharp">delete</span>
  </button>
</td>

      `;
      //       <td>
      //   <button class="edit-btn" onclick="editStock(${stock.No_Stock})">Edit</button>
      //   <button class="delete-btn" onclick="deleteStock(${stock.No_Stock})">Delete</button>
      // </td>
      tbody.appendChild(row);
    });
  })
  .catch((err) => console.error("❌ Error fetching stock:", err));

// ================== 👥 FETCH CLIENTS ==================
fetch("http://127.0.0.1:8000/client/client/Client")
  .then((res) => res.json())
  .then((data) => {
    const tbody = document.querySelector("#client-table tbody");
    if (!tbody) return;
    tbody.innerHTML = "";
    data.forEach((client) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>#${client.No_Client}</td>
        <td>${client.Client_Name}</td>
        <td>${client.No_Telephone}</td>
        <td class="action-cell">
  <!-- View Details -->
  <button class="action-btn view" title="View Details">
    <span class="material-icons-sharp">visibility</span>
  </button>
  <!-- Edit -->
  <button class="action-btn edit" title="Edit">
    <span class="material-icons-sharp">edit</span>
  </button>
  <!-- Delete -->
  <button class="action-btn delete" title="Delete">
    <span class="material-icons-sharp">delete</span>
  </button>
</td>
      `;
      tbody.appendChild(row);
    });
    //     <td>
    //   <button class="edit-btn" onclick="editClient(${client.No_Client})">Edit</button>
    //   <button class="delete-btn" onclick="deleteClient(${client.No_Client})">Delete</button>
    // </td>
  })
  .catch((err) => console.error("❌ Error fetching clients:", err));

// ================== 🔍 SEARCH + FILTER ==================
document.addEventListener("DOMContentLoaded", () => {
  fetchProducts();

  const searchInput = document.getElementById("searchInput");
  const categoryFilter = document.getElementById("categoryFilter");
  const priceFilter = document.getElementById("priceFilter");

  function filterProducts() {
    const searchValue = searchInput.value.toLowerCase();
    const categoryValue = categoryFilter.value;
    const priceValue = priceFilter.value;

    const filtered = allProducts.filter((p) => {
      const matchesSearch =
        p.Product_Name.toLowerCase().includes(searchValue) ||
        p.Category.toLowerCase().includes(searchValue);

      const matchesCategory = categoryValue
        ? p.Category === categoryValue
        : true;

      let matchesPrice = true;
      if (priceValue === "low") matchesPrice = p.Price < 2000;
      else if (priceValue === "mid")
        matchesPrice = p.Price >= 2000 && p.Price <= 5000;
      else if (priceValue === "high") matchesPrice = p.Price > 5000;

      return matchesSearch && matchesCategory && matchesPrice;
    });

    renderProducts(filtered);
  }

  searchInput?.addEventListener("input", filterProducts);
  categoryFilter?.addEventListener("change", filterProducts);
  priceFilter?.addEventListener("change", filterProducts);
});

// ================== 📊 TOTAL COUNTERS ==================
fetch("http://127.0.0.1:8000/order/order/total_order")
  .then((res) => res.json())
  .then(
    (data) =>
      (document.getElementById("total_order").textContent = data.total || 0)
  )
  .catch((err) => console.error("❌ Error fetching total orders:", err));

fetch("http://127.0.0.1:8000/payment/payment/total_revenue")
  .then((res) => res.json())
  .then((data) => {
    const el = document.getElementById("total-sales");
    el.textContent = data.total
      ? `${Number(data.total).toFixed(0)} FCFA`
      : "N/A";
  })
  .catch((err) => console.error("❌ Error fetching total sales:", err));

fetch("http://127.0.0.1:8000/reservation/reservation/total_reservations")
  .then((res) => res.json())
  .then(
    (data) =>
      (document.getElementById("total-reservation").textContent =
        data.total || 0)
  )
  .catch((err) => console.error("❌ Error fetching total reservations:", err));

// ================== 🧾 FETCH RESERVATIONS ==================
fetch("http://127.0.0.1:8000/reservation_info")
  .then((res) => res.json())
  .then((data) => {
    const tbody = document.querySelector("#reservation-table tbody");
    if (!tbody) return;
    tbody.innerHTML = "";

    data.forEach((resv) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>#${resv.No_Reservation}</td>
        <td>${resv.Client_Name}</td>
        <td>${new Date(resv.Reservation_Date).toLocaleDateString()}</td>
                <td class="action-cell">
  <!-- View Details -->
  <button class="action-btn view" title="View Details">
    <span class="material-icons-sharp">visibility</span>
  </button>
  <!-- Edit -->
  <button class="action-btn edit" title="Edit">
    <span class="material-icons-sharp">edit</span>
  </button>
  <!-- Delete -->
  <button class="action-btn delete" title="Delete">
    <span class="material-icons-sharp">delete</span>
  </button>
</td>
        
      `;
      tbody.appendChild(row);
    });
  })
  .catch((err) => console.error(" Error fetching reservations:", err));
// ================== 🧾 FETCH TABLES ==================
fetch("http://127.0.0.1:8000/table/table/Table")
  .then((res) => res.json())
  .then((data) => {
    const tbody = document.querySelector("#tables-table tbody");
    if (!tbody) return;
    tbody.innerHTML = "";

    data.forEach((tab) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>#${tab.Table_ID}</td>
        <td>${tab.No_Table}</td>
        <td>${tab.Seat_Number}</td>
        <td class="action-cell">
          <!-- Edit -->
          <button class="action-btn edit" title="Edit">
            <span class="material-icons-sharp">edit</span>
          </button>
          <!-- Delete -->
          <button class="action-btn delete" title="Delete">
            <span class="material-icons-sharp">delete</span>
          </button>
        </td>
      `;
      tbody.appendChild(row);
    });
  })
  .catch((err) => console.error("Error fetching tables:", err));

// ---------------- DELETE POPUP ----------------
const deletePopup = document.getElementById("deletePopup");
const confirmDelete = document.getElementById("confirmDelete");
const cancelDelete = document.getElementById("cancelDelete");

let targetRow = null; // store the row to delete

// Event delegation on tbody
const tbody = document.querySelector("#tables-table tbody");

tbody.addEventListener("click", (e) => {
  const deleteBtn = e.target.closest(".action-btn.delete");
  if (deleteBtn) {
    targetRow = deleteBtn.closest("tr"); // get parent row
    deletePopup.style.display = "flex"; // show popup
  }
});

// Cancel deletion
cancelDelete.addEventListener("click", () => {
  deletePopup.style.display = "none"; // hide popup
  targetRow = null;
});

// Confirm deletion
confirmDelete.addEventListener("click", () => {
  if (targetRow) {
    targetRow.remove(); // delete the row
  }
  deletePopup.style.display = "none"; // hide popup
  targetRow = null;
});
