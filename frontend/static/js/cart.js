// 1. CONFIGURACIÓN (Elementos del DOM)
const cartToggle = document.getElementById('cart-toggle');
const cartDropdown = document.getElementById('cart-dropdown');

// 2. FUNCIÓN PARA OBTENER EL TOKEN FRESCO
function getAuthToken() {
    return localStorage.getItem('urban_token');
}

// 3. FUNCIÓN PARA LLENAR EL DESPLEGABLE
async function actualizarVistaCarrito() {
    const token = getAuthToken();
    if (!token) return;

    try {
        const res = await fetch('http://127.0.0.1:5000/api/cart', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        
        const container = document.getElementById('cart-items-container');
        const badge = document.getElementById('cart-badge');
        const totalText = document.getElementById('cart-total-value');

        container.innerHTML = "";
        badge.innerText = data.items.length;
        totalText.innerText = data.total.toLocaleString();

        if (data.items.length === 0) {
            container.innerHTML = '<p style="padding: 15px; text-align:center; color:#666;">Tu carrito está vacío</p>';
        } else {
            data.items.forEach(item => {
                container.innerHTML += `
                    <div class="cart-item">
                        <div class="cart-item__info">
                            <b>${item.product_name}</b>
                            <span>Cantidad: ${item.quantity}</span>
                        </div>
                    <div class="cart-item__price">
                        <strong>$${item.subtotal.toLocaleString()}</strong>
                    </div>
                </div>`;
            });
        }
    } catch (e) {
        console.error("Error al obtener el carrito:", e);
    }
}

// 4. FUNCIÓN PARA AGREGAR PRODUCTOS
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

// 5. FUNCIÓN PARA PROCESAR EL PAGO (CHECKOUT)
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
            cartDropdown.classList.remove('active');
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

// 6. EVENTOS
cartToggle.addEventListener('click', (e) => {
    e.preventDefault();
    cartDropdown.classList.toggle('active');
    if (cartDropdown.classList.contains('active')) {
        actualizarVistaCarrito();
    }
});

// Cargar estado inicial
actualizarVistaCarrito();