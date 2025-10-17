// Simulate QR Table ID
const tableNumber =
  new URLSearchParams(window.location.search).get("table") || "A1";
document.getElementById("table-number").textContent = tableNumber;

// Cart data
let cart = [];

const cartSidebar = document.getElementById("cart-sidebar");
const cartItems = document.getElementById("cart-items");
const cartCount = document.getElementById("cart-count");
const cartTotal = document.getElementById("cart-total");

// Open Cart
document.querySelector(".cart-btn").addEventListener("click", () => {
  cartSidebar.classList.add("show");
});

// Close Cart
document.querySelector(".close-btn").addEventListener("click", () => {
  cartSidebar.classList.remove("show");
});

// Add to Cart
document.querySelectorAll(".add-to-cart-btn").forEach((btn) => {
  btn.addEventListener("click", (e) => {
    const card = e.target.closest(".product-card");
    const id = card.dataset.id;
    const name = card.querySelector("h4").innerText;
    const price = parseFloat(
      card.querySelector(".price").innerText.replace("$", "")
    );
    const img = card.querySelector("img").src;

    const existing = cart.find((item) => item.id === id);
    if (existing) existing.qty++;
    else cart.push({ id, name, price, img, qty: 1 });

    updateCart();
  });
});

// Update Cart Display
function updateCart() {
  cartItems.innerHTML = "";
  let total = 0;
  let count = 0;

  cart.forEach((item) => {
    total += item.price * item.qty;
    count += item.qty;

    const div = document.createElement("div");
    div.classList.add("cart-item");
    div.innerHTML = `
      <div>
        <h4>${item.name}</h4>
        <p>$${item.price.toFixed(2)} x ${item.qty}</p>
      </div>
      <button class="remove-btn" data-id="${item.id}">
        <i class="material-icons-sharp">delete</i>
      </button>
    `;
    cartItems.appendChild(div);
  });

  cartTotal.textContent = `$${total.toFixed(2)}`;
  cartCount.textContent = count;
  setupRemove();
}

// Remove item
function setupRemove() {
  document.querySelectorAll(".remove-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = btn.dataset.id;
      cart = cart.filter((item) => item.id !== id);
      updateCart();
    });
  });
}

// Checkout
document.querySelector(".checkout-btn").addEventListener("click", () => {
  alert(`Order placed for Table ${tableNumber}!`);
  cart = [];
  updateCart();
  cartSidebar.classList.remove("show");
});

// Category Filter
const buttons = document.querySelectorAll(".category-btn");
buttons.forEach((btn) =>
  btn.addEventListener("click", () => {
    buttons.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");

    const category = btn.dataset.category;
    document.querySelectorAll(".product-card").forEach((card) => {
      card.style.display =
        category === "all" || card.dataset.category === category
          ? "block"
          : "none";
    });
  })
);
