// 1. CONFIGURACIÓN
let TOKEN = localStorage.getItem('urban_token');
const cartToggle = document.getElementById('cart-toggle');
const cartDropdown = document.getElementById('cart-dropdown');

// 2. FUNCIÓN PARA LLENAR EL DESPLEGABLE
async function actualizarVistaCarrito() {
    if (!TOKEN) return;

    try {
        const res = await fetch('http://127.0.0.1:5000/api/cart', {
            headers: { 'Authorization': `Bearer ${TOKEN}` }
        });
        const data = await res.json();
        
        const container = document.getElementById('cart-items-container');
        const badge = document.getElementById('cart-badge');
        const totalText = document.getElementById('cart-total-value');

        // Limpiamos el "Cargando..."
        container.innerHTML = "";
        badge.innerText = data.items.length;
        totalText.innerText = data.total.toLocaleString();

        if (data.items.length === 0) {
            container.innerHTML = '<p style="padding: 15px; text-align:center; color:#666;">Tu carrito está vacío</p>';
        } else {
            data.items.forEach(item => {
                container.innerHTML += `
                    <div style="display:flex; justify-content:space-between; padding:10px; border-bottom:1px solid #eee; font-size:14px;">
                        <span>${item.product_name} (x${item.quantity})</span>
                        <b>$${item.subtotal.toLocaleString()}</b>
                    </div>`;
            });
        }
    } catch (e) {
        console.error("Error al obtener el carrito:", e);
    }
}

// 3. EVENTO PARA ABRIR/CERRAR
cartToggle.addEventListener('click', (e) => {
    e.preventDefault();
    cartDropdown.classList.toggle('active'); // Tu compa debe tener la clase .active en CSS
    if (cartDropdown.classList.contains('active')) {
        actualizarVistaCarrito();
    }
});

// Cargar el numerito (badge) apenas abra la página
actualizarVistaCarrito();