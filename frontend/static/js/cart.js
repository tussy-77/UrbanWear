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
            const res = await fetch('/api/auth/login', {
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
            const res = await fetch('/api/auth/magic-link', {
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
    window.location.href = '/api/auth/google';
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
        const res = await fetch('/api/cart', {
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
                    const sizeBadge = item.size
                        ? `<span style="background:rgba(255,255,255,0.12); color:rgba(255,255,255,0.7); font-size:0.68rem; font-weight:700; padding:2px 7px; border-radius:4px; letter-spacing:0.5px;">${item.size}</span>`
                        : '';
                    container.innerHTML += `
                        <div class="cart-sidebar-item" style="display:flex; gap:10px; margin-bottom:15px;">
                            <img src="https://placehold.co/60x60?text=Item" style="width:60px; border-radius:5px;">
                            <div style="flex:1;">
                                <p style="margin:0; font-weight:bold; font-size:0.85rem;">${item.product_name}</p>
                                <div style="display:flex; align-items:center; gap:6px; margin:3px 0;">
                                    <p style="margin:0; font-size:0.78rem; color:rgba(255,255,255,0.5);">Cant: ${item.quantity}</p>
                                    ${sizeBadge}
                                </div>
                                <p style="margin:0; color:#fff; font-size:0.85rem;">$${item.subtotal.toLocaleString()}</p>
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

async function agregarAlCarrito(productId, size) {
    const token = getAuthToken();
    if (!token) { mostrarToast('Inicia sesión para agregar al carrito', 'error'); return; }

    try {
        const body = { product_id: productId, quantity: 1 };
        if (size) body.size = size;

        const res = await fetch('/api/cart/add', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const data = await res.json();
        if (res.ok) {
            actualizarVistaCarrito();
            abrirCarrito();
        } else {
            mostrarToast(data.msg || 'No se pudo agregar al carrito', 'error');
        }
    } catch (e) {
        mostrarToast('Error de conexión', 'error');
    }
}

function mostrarToast(mensaje, tipo) {
    let toast = document.getElementById('cart-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'cart-toast';
        toast.style.cssText = 'position:fixed;bottom:24px;left:50%;transform:translateX(-50%) translateY(12px);padding:12px 20px;border-radius:8px;font-size:0.82rem;font-weight:600;letter-spacing:0.3px;z-index:9999;opacity:0;transition:opacity 0.25s,transform 0.25s;pointer-events:none;font-family:inherit;';
        document.body.appendChild(toast);
    }
    toast.textContent = mensaje;
    toast.style.background = tipo === 'error' ? '#111' : '#16a34a';
    toast.style.color = '#fff';
    toast.style.opacity = '1';
    toast.style.transform = 'translateX(-50%) translateY(0)';
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(-50%) translateY(12px)';
    }, 3000);
}

async function procesarPago() {
    const token = getAuthToken();
    if (!token) return;
    window.location.href = '/checkout';
    try {
        const res = await fetch('/api/orders/checkout', {
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

// 4b. BUSCADOR
var searchTimer = null;

function abrirBuscador() {
    document.getElementById('search-overlay').style.display = 'block';
    document.getElementById('search-panel').style.display = 'block';
    setTimeout(() => document.getElementById('search-input').focus(), 50);
}

function cerrarBuscador() {
    document.getElementById('search-overlay').style.display = 'none';
    document.getElementById('search-panel').style.display = 'none';
    document.getElementById('search-results').style.display = 'none';
    document.getElementById('search-input').value = '';
}

function onSearchInput(q) {
    clearTimeout(searchTimer);
    if (!q.trim()) { document.getElementById('search-results').style.display = 'none'; return; }
    searchTimer = setTimeout(() => buscarProductos(q), 280);
}

async function buscarProductos(q) {
    try {
        const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
        const data = await res.json();
        renderResultados(data.products, q);
    } catch (e) {}
}

function renderResultados(products, q) {
    const box = document.getElementById('search-results');
    if (!products.length) {
        box.style.display = 'block';
        box.innerHTML = `<p style="padding:18px 20px; color:rgba(255,255,255,0.4); font-size:0.82rem; letter-spacing:1px;">Sin resultados para "${q}" — <a href="/catalogo?q=${encodeURIComponent(q)}" style="color:rgba(255,255,255,0.65); text-decoration:underline;">ver catálogo</a></p>`;
        return;
    }
    box.style.display = 'block';
    box.innerHTML = products.map(p => `
        <a href="/producto/${p.id}" onclick="cerrarBuscador()" style="display:flex; align-items:center; gap:14px; padding:12px 20px; text-decoration:none; border-bottom:1px solid rgba(255,255,255,0.06); transition:background 0.15s;" onmouseover="this.style.background='rgba(255,255,255,0.06)'" onmouseout="this.style.background='none'">
            <div style="width:42px; height:42px; border-radius:6px; overflow:hidden; flex-shrink:0; background:#1a1a1a;">
                ${p.image_src ? `<img src="${p.image_src}" style="width:100%; height:100%; object-fit:cover;">` : ''}
            </div>
            <div style="flex:1; min-width:0;">
                <p style="margin:0; font-size:0.82rem; font-weight:500; color:#fff; letter-spacing:0.5px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${p.name}</p>
                <p style="margin:0; font-size:0.75rem; color:rgba(255,255,255,0.4);">$${p.price.toLocaleString()}</p>
            </div>
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 256 256" style="fill:rgba(255,255,255,0.25); flex-shrink:0;"><path d="M221.66,133.66l-72,72a8,8,0,0,1-11.32-11.32L196.69,136H40a8,8,0,0,1,0-16H196.69L138.34,61.66a8,8,0,0,1,11.32-11.32l72,72A8,8,0,0,1,221.66,133.66Z"/></svg>
        </a>
    `).join('') + `<a href="/catalogo?q=${encodeURIComponent(q)}" onclick="cerrarBuscador()" style="display:block; padding:12px 20px; font-size:0.75rem; letter-spacing:1.5px; color:rgba(255,255,255,0.45); text-decoration:none; text-align:center; text-transform:uppercase;" onmouseover="this.style.color='rgba(255,255,255,0.75)'" onmouseout="this.style.color='rgba(255,255,255,0.45)'">Ver todos los resultados →</a>`;
}

function irAlCatalogoBusqueda() {
    const q = document.getElementById('search-input').value.trim();
    if (q) { cerrarBuscador(); window.location.href = `/catalogo?q=${encodeURIComponent(q)}`; }
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

  const searchToggle = document.getElementById('search-toggle');
    if (searchToggle) searchToggle.onclick = (e) => { e.preventDefault(); abrirBuscador(); };

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