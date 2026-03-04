// TODO: Agregar funcionalidad JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // TODO: Inicializar componentes cuando cargue la página
    const searchInput = document.getElementById('productSearch');
    const stockFilter = document.getElementById('stockFilter');

    const applyProductFilters = () => {
        const query = (searchInput?.value || '').toLowerCase().trim();
        const stockMode = stockFilter?.value || 'all';
        const items = document.querySelectorAll('.product-item');

        items.forEach((item) => {
            const name = item.dataset.name || '';
            const description = item.dataset.description || '';
            const stock = Number(item.dataset.stock || '0');

            const matchesQuery = !query || name.includes(query) || description.includes(query);
            const matchesStock =
                stockMode === 'all' ||
                (stockMode === 'available' && stock > 0) ||
                (stockMode === 'soldout' && stock === 0);

            item.style.display = matchesQuery && matchesStock ? '' : 'none';
        });
    };

    if (searchInput) {
        searchInput.addEventListener('input', applyProductFilters);
    }
    if (stockFilter) {
        stockFilter.addEventListener('change', applyProductFilters);
    }
});

// TODO: Función para agregar productos al carrito con AJAX
async function addToCart(productId, quantity = 1) {
    // TODO: Implementar agregado al carrito
    const payload = new URLSearchParams({ quantity: String(quantity) });
    const response = await fetch(`/add-to-cart/${productId}`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: payload
    });

    const result = await response.json();
    if (!response.ok || !result.success) {
        alert(result.message || 'No se pudo agregar al carrito.');
        return;
    }

    alert(result.message || 'Producto agregado al carrito.');
}

// TODO: Función para actualizar cantidad en el carrito
async function updateCartQuantity(itemId, quantity) {
    // TODO: Implementar actualización de cantidad
    const payload = new URLSearchParams({ quantity: String(quantity) });
    const response = await fetch(`/cart/items/${itemId}/update`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: payload
    });

    const result = await response.json();
    if (!response.ok || !result.success) {
        alert(result.message || 'No se pudo actualizar la cantidad.');
        return;
    }

    window.location.reload();
}

// TODO: Función para remover items del carrito
async function removeFromCart(itemId) {
    // TODO: Implementar remoción de items
    const response = await fetch(`/cart/items/${itemId}/remove`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    });

    const result = await response.json();
    if (!response.ok || !result.success) {
        alert(result.message || 'No se pudo remover el producto del carrito.');
        return;
    }

    window.location.reload();
}