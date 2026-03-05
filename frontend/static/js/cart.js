// --------------------------  ---  ESTO ES PARA AUTOMATIZAR EL USO DEL TOKEN  --- ------------------------------------- \\

// El token lo vamos a manejar con localStorage para que las peticiones vayan firmadas automáticamente en los Headers \\

// SI NO SABE PREGUNTELE A SU NOVIA CLAUDIA :V 

// 1. CONFIGURACIÓN INICIAL
let TOKEN = localStorage.getItem('urban_token');
const cartDropdown = document.getElementById('cart-dropdown');
const cartBadge = document.getElementById('cart-badge');


async function loginManual() {
    const email = prompt("Introduce tu email:");
    const password = prompt("Introduce tu contraseña:");

    const response = await fetch('http://127.0.0.1:5000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });

    const data = await response.json();
    if (data.access_token) {
        localStorage.setItem('urban_token', data.access_token);
        TOKEN = data.access_token;
        alert("¡Login exitoso!");
        actualizarVistaCarrito(); 
    } else {
        alert("Error en el login");
    }
}


async function actualizarVistaCarrito() {
    if (!TOKEN) return;

    try {
        const res = await fetch('http://127.0.0.1:5000/api/cart', {
            headers: { 'Authorization': `Bearer ${TOKEN}` }
        });
        const data = await res.json();
        
        const container = document.getElementById('cart-items-container');
        const totalText = document.getElementById('cart-total-value');

        container.innerHTML = "";
        cartBadge.innerText = data.items.length; 
        totalText.innerText = data.total.toLocaleString();

        if (data.items.length === 0) {
            container.innerHTML = '<p style="text-align:center; padding:10px;">Vacío</p>';
        } else {
            data.items.forEach(item => {
                container.innerHTML += `
                    <div class="cart-item-mini">
                        <span>${item.product_name} (x${item.quantity})</span>
                        <b>$${item.subtotal}</b>
                    </div>`;
            });
        }
    } catch (e) {
        console.error("Error cargando carrito", e);
    }
}


async function agregarAlCarrito(productId) {
    if (!TOKEN) {
        alert("Debes iniciar sesión primero");
        loginManual();
        return;
    }

    const response = await fetch('http://127.0.0.1:5000/api/cart/add', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${TOKEN}`
        },
        body: JSON.stringify({ product_id: productId, quantity: 1 })
    });

    if (response.ok) {
        actualizarVistaCarrito(); 
        alert("¡Producto añadido!");
    }
}


document.getElementById('cart-toggle').addEventListener('click', () => {
    cartDropdown.classList.toggle('active');
});


actualizarVistaCarrito();