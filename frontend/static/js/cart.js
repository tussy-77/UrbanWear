// 1. CONFIGURACIÓN (Elementos del DOM)
const cartToggle = document.getElementById('cart-toggle');
const cartSidebar = document.getElementById('cart-sidebar');
const cartClose = document.getElementById('cart-close');
const cartOverlay = document.getElementById('cart-overlay');

// 2. FUNCIÓN PARA OBTENER EL TOKEN FRESCO
function getAuthToken() {
    return localStorage.getItem('urban_token');
}

// 3. FUNCIÓN PARA LLENAR EL PANEL LATERAL
async function actualizarVistaCarrito() {
    const token = getAuthToken();
    if (!token) return;

    try {
        const res = await fetch('http://127.0.0.1:5000/api/cart', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        
        const container = document.getElementById('cart-sidebar-items');
        const badge = document.getElementById('cart-badge');
        const totalText = document.getElementById('cart-total-sidebar');

        container.innerHTML = "";
        badge.innerText = data.items.length;
        totalText.innerText = data.total.toLocaleString();

        if (data.items.length === 0) {
            container.innerHTML = '<p class="cart-empty-msg">Tu carrito está vacío<br><small style="color: #ccc;">¡Agrega algunos productos!</small></p>';
        } else {
            data.items.forEach(item => {
                container.innerHTML += `
                    <div class="cart-sidebar-item">
                        <div class="cart-sidebar-item__image">
                            <img src="https://via.placeholder.com/100?text=${item.product_name.substring(0, 2)}" alt="${item.product_name}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 8px;">
                        </div>
                        <div class="cart-sidebar-item__info">
                            <p class="cart-sidebar-item__name">${item.product_name}</p>
                            <p class="cart-sidebar-item__category">Categoría: ${item.category || 'General'}</p>
                            <p class="cart-sidebar-item__qty">Cantidad: ${item.quantity}</p>
                            <div class="cart-sidebar-item__price">
                                <span class="cart-sidebar-item__subtotal">$${item.subtotal.toLocaleString()}</span>
                            </div>
                        </div>
                    </div>`;
            });
        }
    } catch (e) {
        console.error("Error al obtener el carrito:", e);
    }
}

// 4. FUNCIÓN PARA ABRIR EL PANEL LATERAL
function abrirCarrito() {
    cartSidebar.classList.add('active');
    actualizarVistaCarrito();
}

// 5. FUNCIÓN PARA CERRAR EL PANEL LATERAL
function cerrarCarrito() {
    cartSidebar.classList.remove('active');
}

// 6. FUNCIÓN PARA AGREGAR PRODUCTOS
async function agregarAlCarrito(productId) {
    const token = getAuthToken();
    
    if (!token) {
        alert("Debes iniciar sesión para agregar productos.");
        return;
    }

    try {
        const res = await fetch('http://127.0.0.1:5000/api/cart/add', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ product_id: productId, quantity: 1 })
        });

        if (res.ok) {
            actualizarVistaCarrito();
            alert("Producto añadido con éxito");
        } else {
            const error = await res.json();
            alert("No se pudo agregar: " + error.msg);
        }
    } catch (e) {
        console.error("Error al añadir producto:", e);
    }
}

// 7. FUNCIÓN PARA PROCESAR EL PAGO (CHECKOUT)
async function procesarPago() {
    const token = getAuthToken();
    
    if (!token) {
        alert("Inicia sesión para completar la compra.");
        return;
    }

    try {
        const response = await fetch('http://127.0.0.1:5000/api/orders/checkout', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (response.ok) {
            alert(`¡Compra exitosa! Orden ID: ${data.order_id}`);
            actualizarVistaCarrito(); 
            cerrarCarrito();
        } else {
            alert("Error: " + data.msg);
        }
    } catch (error) {
        console.error("Error en el checkout:", error);
    }
}

function actualizarInterfazUsuario() {
    const token = localStorage.getItem('urban_token');
    const userName = localStorage.getItem('client_name') || 'Cliente';
    
    const guestButtons = document.getElementById('guest-buttons');
    const userProfile = document.getElementById('user-profile-menu');
    const displayName = document.getElementById('user-display-name');

    if (token) {
        // Hay sesión iniciada
        guestButtons.style.display = 'none';
        userProfile.style.display = 'flex';
        displayName.innerText = userName;
    } else {
        // No hay sesión
        guestButtons.style.display = 'flex';
        userProfile.style.display = 'none';
    }
}

// Función para cerrar sesión
function cerrarSesion() {
    localStorage.removeItem('urban_token');
    localStorage.removeItem('client_name');
    alert("Sesión cerrada correctamente.");
    window.location.href = "/";
}

// Ejecutar al cargar la página
document.addEventListener('DOMContentLoaded', actualizarInterfazUsuario);

// 8. EVENTOS DEL CARRITO
if (cartToggle) {
    cartToggle.addEventListener('click', (e) => {
        e.preventDefault();
        abrirCarrito();
    });
}

if (cartClose) {
    cartClose.addEventListener('click', (e) => {
        e.preventDefault();
        cerrarCarrito();
    });
}

if (cartOverlay) {
    cartOverlay.addEventListener('click', (e) => {
        cerrarCarrito();
    });
}

// Cargar estado inicial
actualizarVistaCarrito();