async function login() {
    const email    = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const msg      = document.getElementById('msg');

    if (!email || !password) {
        msg.style.color = '#ef4444';
        msg.style.display = 'block';
        msg.textContent = 'Completa todos los campos.';
        return;
    }

    try {
        const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
        const res  = await fetch('/api/admin/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();

        if (res.ok) {
            window.location.href = '/admin';
        } else {
            msg.style.color = '#ef4444';
            msg.style.display = 'block';
            msg.textContent = data.msg || 'Error al iniciar sesión.';
        }
    } catch (e) {
        msg.style.color = '#ef4444';
        msg.style.display = 'block';
        msg.textContent = 'Error de conexión.';
    }
}
