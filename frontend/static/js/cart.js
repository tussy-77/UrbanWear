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
    const sidebarLoggedIn = document.getElementById('profile-logged-in');
    const sidebarGuest = document.getElementById('profile-guest');

    if (token) {
        if (guestIcon) guestIcon.style.display = 'none';
        if (userProfileIcon) userProfileIcon.style.display = 'flex';
        if (displayName) displayName.innerText = userName;
        if (sidebarLoggedIn) sidebarLoggedIn.style.display = 'flex';
        if (sidebarGuest) sidebarGuest.style.display = 'none';
    } else {
        if (guestIcon) guestIcon.style.display = 'flex';
        if (userProfileIcon) userProfileIcon.style.display = 'none';
        if (sidebarLoggedIn) sidebarLoggedIn.style.display = 'none';
        if (sidebarGuest) sidebarGuest.style.display = 'flex';
    }
}

function toggleProfileMenu() {
    const sidebar = document.getElementById('profile-sidebar');
    const overlay = document.getElementById('profile-sidebar-overlay');
    const isOpen = sidebar.style.right === '0px';

    if (isOpen) {
        sidebar.style.right = '-320px';
        overlay.style.display = 'none';
    } else {
        sidebar.style.right = '0px';
        overlay.style.display = 'block';
    }
}

function cerrarSesion() {
    localStorage.removeItem('urban_token');
    localStorage.removeItem('client_name');
    alert("Sesión cerrada correctamente.");
    window.location.href = "/";
}

let authMode = null;

function abrirModal() {
    const modal = document.getElementById('login-modal');
    modal.style.display = 'flex';
    document.getElementById('sub-form').style.display = 'none';
    document.getElementById('auth-msg').style.display = 'none';
    document.getElementById('input-email').value = '';
    document.getElementById('input-password').value = '';
}

function cerrarModal() {
    document.getElementById('login-modal').style.display = 'none';
}

function mostrarFormEmail(modo) {
    authMode = modo;
    const subForm = document.getElementById('sub-form');
    const passInput = document.getElementById('input-password');
    const btn = document.getElementById('sub-form-btn');
    const linkRegistro = document.getElementById('link-registro');

    subForm.style.display = 'block';
    passInput.style.display = modo === 'password' ? 'block' : 'none';
    btn.textContent = modo === 'password' ? 'INICIAR SESIÓN' : 'ENVIAR CLAVE';
    linkRegistro.style.display = modo === 'password' ? 'block' : 'none';
}

async function submitAuth() {
    const email = document.getElementById('input-email').value.trim();
    const password = document.getElementById('input-password').value;

    if (!email) { mostrarAuthMsg('Ingresa tu email.', 'error'); return; }

    if (authMode === 'password') {
        if (!password) { mostrarAuthMsg('Ingresa tu contraseña.', 'error'); return; }

        try {
            const res = await fetch('http://127.0.0.1:5000/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            const data = await res.json();

            if (res.ok && data.access_token) {
                localStorage.setItem('urban_token', data.access_token);
                localStorage.setItem('client_name', data.name || email);
                cerrarModal();
                actualizarInterfazUsuario();
                actualizarVistaCarrito();
            } else {
                mostrarAuthMsg(data.msg || 'Credenciales incorrectas.', 'error');
            }
        } catch (e) {
            mostrarAuthMsg('Error de conexión.', 'error');
        }

    } else if (authMode === 'magic') {
        try {
            const res = await fetch('http://127.0.0.1:5000/api/auth/magic-link', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            });
            const data = await res.json();
            if (res.ok) {
                mostrarAuthMsg('✅ Revisa tu email, te enviamos una clave de acceso.', 'success');
            } else {
                mostrarAuthMsg(data.msg || 'Error al enviar el email.', 'error');
            }
        } catch (e) {
            mostrarAuthMsg('Error de conexión.', 'error');
        }
    }
}

function loginGoogle() {
    window.location.href = 'http://127.0.0.1:5000/api/auth/google';
}

function mostrarAuthMsg(texto, tipo) {
    const msg = document.getElementById('auth-msg');
    msg.style.color = tipo === 'error' ? '#e53e3e' : '#2f855a';
    msg.textContent = texto;
    msg.style.display = 'block';
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
    window.location.href = '/checkout';
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

function irAlCheckout() {
    const token = getAuthToken();
    if (!token) { abrirModal(); return; }
    window.location.href = '/checkout';
}

// 5. SCROLL — ocultar/mostrar header según dirección
(function () {
    var lastY = 0;
    var header = null;
    var threshold = 80; // px desde el top donde empieza a ocultarse

    window.addEventListener('scroll', function () {
        if (!header) header = document.querySelector('.header');
        if (!header) return;

        var currentY = window.scrollY;

        if (currentY > threshold && currentY > lastY) {
            header.classList.add('header--hidden');
        } else {
            header.classList.remove('header--hidden');
        }

        lastY = currentY;
    }, { passive: true });
})();

// 6. EVENTOS E INICIALIZACIÓN
document.addEventListener('DOMContentLoaded', () => {
      const urlParams = new URLSearchParams(window.location.search);
    const tokenUrl = urlParams.get('token');
    const nameUrl = urlParams.get('name');
    if (tokenUrl) {
        localStorage.setItem('urban_token', tokenUrl);
        localStorage.setItem('client_name', nameUrl || 'Cliente');
        window.history.replaceState({}, document.title, window.location.pathname);
    }
    actualizarInterfazUsuario();
    actualizarVistaCarrito();

  if (cartToggle) cartToggle.onclick = (e) => { e.preventDefault(); abrirCarrito(); };
    if (cartClose) cartClose.onclick = (e) => { e.preventDefault(); cerrarCarrito(); };
    if (cartOverlay) cartOverlay.onclick = cerrarCarrito;

    
    

   
    const loginModal = document.getElementById('login-modal');
    if (loginModal) {
        loginModal.addEventListener('click', function(e) {
            if (e.target === this) cerrarModal();
        });
    }
    

    
});