// 1. CONFIGURACIÓN DE ELEMENTOS
const cartToggle = document.getElementById('cart-toggle');
const cartSidebar = document.getElementById('cart-sidebar');
const cartClose = document.getElementById('cart-close');
const cartOverlay = document.getElementById('cart-overlay');

// 2. UTILIDADES
function getAuthToken() {
    return localStorage.getItem('urban_token');
}

// 3. INTERFAZ DE USUARIO (ICONOS Y MENÚ)
function actualizarInterfazUsuario() {
    const token = getAuthToken();
    const userName = localStorage.getItem('client_name') || 'Cliente';
    
    const guestIcon = document.getElementById('guest-icon');
    const userProfileIcon = document.getElementById('user-profile-icon');
    const displayName = document.getElementById('user-display-name');

    if (token) {
        if (guestIcon) guestIcon.style.display = 'none';
        if (userProfileIcon) userProfileIcon.style.display = 'flex';
        if (displayName) displayName.innerText = userName;
    } else {
        if (guestIcon) guestIcon.style.display = 'flex';
        if (userProfileIcon) userProfileIcon.style.display = 'none';
    }
}

function toggleProfileMenu() {
    const menu = document.getElementById('profile-dropdown');
    if (menu) {
        menu.style.display = (menu.style.display === 'none' || menu.style.display === '') ? 'block' : 'none';
    }
}

function cerrarSesion() {
    localStorage.removeItem('urban_token');
    localStorage.removeItem('client_name');
    alert("Sesión cerrada correctamente.");
    window.location.href = "/";
}

// 4. LÓGICA DEL CARRITO
async function actualizarVistaCarrito() {
    const token = getAuthToken();
    if (!token) return;

    try {
        const res = await fetch('http://127.0.0.1:5000/api/cart', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        
        const container = document.getElementById('cart-sidebar-items');
        const totalText = document.getElementById('cart-total-sidebar');
        const badge = document.getElementById('cart-badge');

        if (container) {
            container.innerHTML = "";
            if (!data.items || data.items.length === 0) {
                container.innerHTML = '<p class="cart-empty-msg">Tu carrito está vacío</p>';
            } else {
                data.items.forEach(item => {
                    container.innerHTML += `
                        <div class="cart-sidebar-item" style="display: flex; gap: 10px; margin-bottom: 15px;">
                            <img src="https://placehold.co/60x60?text=Item" style="width:60px; border-radius:5px;">
                            <div>
                                <p style="margin:0; font-weight:bold;">${item.product_name}</p>
                                <p style="margin:0; font-size:0.8rem; color:#888;">Cant: ${item.quantity}</p>
                                <p style="margin:0; color:#fff;">$${item.subtotal.toLocaleString()}</p>
                            </div>
                        </div>`;
                });
            }
        }
        if (totalText) totalText.innerText = data.total.toLocaleString();
        if (badge) {
            const totalQty = data.items ? data.items.reduce((acc, item) => acc + item.quantity, 0) : 0;
            badge.innerText = totalQty;
            badge.style.opacity = totalQty > 0 ? "1" : "0";
        }
    } catch (e) { console.error("Error carrito:", e); }
}

function abrirCarrito() {
    if (cartSidebar) cartSidebar.classList.add('active');
    actualizarVistaCarrito();
}

function cerrarCarrito() {
    if (cartSidebar) cartSidebar.classList.remove('active');
}

async function agregarAlCarrito(productId) {
    const token = getAuthToken();
    if (!token) { alert("Inicia sesión primero"); return; }

    try {
        const res = await fetch('http://127.0.0.1:5000/api/cart/add', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId, quantity: 1 })
        });
        if (res.ok) { actualizarVistaCarrito(); abrirCarrito(); }
    } catch (e) { console.error(e); }
}

async function procesarPago() {
    const token = getAuthToken();
    if (!token) return;
    try {
        const res = await fetch('http://127.0.0.1:5000/api/orders/checkout', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
        });
        if (res.ok) {
            const data = await res.json();
            alert(`¡Compra exitosa! Orden: ${data.order_id}`);
            actualizarVistaCarrito();
            cerrarCarrito();
        }
    } catch (e) { console.error(e); }
}

// 5. EVENTOS E INICIALIZACIÓN
document.addEventListener('DOMContentLoaded', () => {
    actualizarInterfazUsuario();
    actualizarVistaCarrito();

    if (cartToggle) cartToggle.onclick = (e) => { e.preventDefault(); abrirCarrito(); };
    if (cartClose) cartClose.onclick = (e) => { e.preventDefault(); cerrarCarrito(); };
    if (cartOverlay) cartOverlay.onclick = cerrarCarrito;

    // Cerrar menú de perfil al hacer clic fuera
    window.onclick = (event) => {
        if (!event.target.closest('.user-menu-wrapper')) {
            const menu = document.getElementById('profile-dropdown');
            if (menu) menu.style.display = 'none';
        }
    };
});