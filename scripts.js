document.addEventListener('DOMContentLoaded', () => {
    const cartCountElement = document.getElementById('cart-count');
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
    const categoryButtons = document.querySelectorAll('.category-btn');
    const productCards = document.querySelectorAll('.product-card');

    let cartCount = 0;

    // --- 1. Cart Functionality ---
    addToCartButtons.forEach(button => {
        button.addEventListener('click', () => {
            cartCount++;
            cartCountElement.textContent = cartCount;
            // Optional: Provide visual feedback to the user
            button.textContent = 'Added!';
            setTimeout(() => {
                // Reset button text after a brief delay
                button.innerHTML = button.dataset.price || '$X.XX' + ' <i class="material-icons">add</i>';
            }, 500);
        });

        // Store price in data attribute for easy reset/management
        const price = button.textContent.split(' ')[0];
        button.dataset.price = price;
    });


    // --- 2. Category Filtering ---
    categoryButtons.forEach(button => {
        button.addEventListener('click', () => {
            // 2a. Update active state for buttons
            categoryButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            const filterCategory = button.textContent.toLowerCase().trim();

            // 2b. Filter the products (Basic implementation based on simplified data)
            productCards.forEach(card => {
                // NOTE: For a real app, products should have data attributes like data-category="roll"
                const cardTitle = card.querySelector('h4').textContent.toLowerCase();
                let isVisible = false;

                if (filterCategory === 'all') {
                    isVisible = true;
                } else if (filterCategory === 'roll' && cardTitle.includes('roll')) {
                    isVisible = true;
                } else if (filterCategory === 'baked goods' && (cardTitle.includes('croissant') || cardTitle.includes('bread'))) {
                    isVisible = true;
                } else if (filterCategory === 'meat' && (cardTitle.includes('burger') || cardTitle.includes('beef'))) {
                    isVisible = true;
                }
                // Add more complex category logic here

                card.style.display = isVisible ? 'flex' : 'none';
            });
            
            // Re-display sections if 'All' is selected, otherwise hide sections not matching filter
            document.querySelectorAll('.product-list h3').forEach(heading => {
                 heading.style.display = (filterCategory === 'all' || heading.nextElementSibling.querySelector('.product-card[style*="flex"]')) ? 'block' : 'none';
            });
        });
    });

    // Simple initialization logic (e.g., set the initial state of product prices)
    productCards.forEach(card => {
        const priceElement = card.querySelector('.add-to-cart-btn');
        const price = priceElement.textContent.trim();
        priceElement.dataset.price = price;
        priceElement.innerHTML = `${price} <i class="material-icons">add</i>`;
    });
});
