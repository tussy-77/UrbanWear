const PEDIDOS_ITEMS = JSON.parse(document.getElementById('pedidos-items-data').textContent);

function itemsHTML(items) {
    if (!items || !items.length) return '<p style="font-size:0.78rem;color:#888;margin:0;">Sin productos</p>';
    return items.map((item, i) => {
        const sep = i < items.length - 1 ? 'border-bottom:1px solid #eee; margin-bottom:3px;' : '';
        const subtotal = Math.round(item.qty * item.price).toLocaleString('en-US');
        return `<div style="display:flex; justify-content:space-between; font-size:0.78rem; padding:3px 0; color:#444; ${sep}">
            <span>${item.name} × ${item.qty}</span>
            <span style="font-weight:600;">$${subtotal}</span>
        </div>`;
    }).join('');
}

// Mapas de acciones disponibles por estado
const TRANSICIONES = {
    pendiente:  [{ label: 'MARCAR PAGADO',    estado: 'pagado',     cls: 'success' },
                 { label: 'CANCELAR',          estado: 'cancelado',  cls: 'danger'  }],
    pagado:     [{ label: 'MARCAR ENVIADO',   estado: 'enviado',    cls: 'primary' },
                 { label: 'CANCELAR',          estado: 'cancelado',  cls: 'danger'  }],
    enviado:    [{ label: 'MARCAR ENTREGADO', estado: 'entregado',  cls: 'done'    }],
    entregado:  [],
    cancelado:  []
};

function accionesHTML(orderId, status) {
    const trans = TRANSICIONES[status] || [];
    if (!trans.length) return '<span style="color:#bbb;font-size:0.75rem;">—</span>';
    return trans.map(t =>
        `<button class="accion-btn accion-btn--${t.cls}"
            onclick="cambiarEstado(${orderId}, '${t.estado}')">
            ${t.label}
        </button>`
    ).join('');
}

async function cambiarEstado(orderId, nuevoEstado) {
    const btn = event.currentTarget;
    btn.disabled = true;
    btn.style.opacity = '0.6';

    try {
        const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
        const res = await fetch(`/admin/pedidos/${orderId}/estado`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken },
            body: JSON.stringify({ estado: nuevoEstado })
        });
        const data = await res.json();

        if (res.ok) {
            // Actualizar badge
            const badge = document.getElementById(`badge-${orderId}`);
            badge.className = `order-badge order-badge--${nuevoEstado}`;
            badge.textContent = nuevoEstado.toUpperCase();

            // Actualizar acciones
            document.getElementById(`acciones-${orderId}`).innerHTML = accionesHTML(orderId, nuevoEstado);

            // Actualizar data-status en la fila (para el filtro)
            document.getElementById(`fila-${orderId}`).dataset.status = nuevoEstado;

            mostrarToast(`Orden #${orderId} → ${nuevoEstado}`, 'ok');
        } else {
            mostrarToast(data.msg || 'Error al actualizar', 'error');
            btn.disabled = false;
            btn.style.opacity = '1';
        }
    } catch {
        mostrarToast('Error de conexión', 'error');
        btn.disabled = false;
        btn.style.opacity = '1';
    }
}

function toggleItems(orderId) {
    const box = document.getElementById(`items-${orderId}`);
    const chevron = document.getElementById(`chevron-${orderId}`);
    const open = box.style.display === 'block';
    if (!open && !box.dataset.rendered) {
        box.innerHTML = itemsHTML(PEDIDOS_ITEMS[String(orderId)]);
        box.dataset.rendered = '1';
    }
    box.style.display = open ? 'none' : 'block';
    chevron.style.transform = open ? 'rotate(0deg)' : 'rotate(180deg)';
}

function mostrarToast(msg, tipo) {
    const t = document.getElementById('admin-toast');
    t.textContent = msg;
    t.style.background = tipo === 'ok' ? '#16a34a' : '#dc2626';
    t.style.color = '#fff';
    t.style.opacity = '1';
    clearTimeout(t._timer);
    t._timer = setTimeout(() => { t.style.opacity = '0'; }, 3000);
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('#tabla-pedidos tbody tr[id^="fila-"]').forEach(fila => {
        const id = fila.id.replace('fila-', '');

        // Acciones por estado
        document.getElementById(`acciones-${id}`).innerHTML = accionesHTML(id, fila.dataset.status);

        // Contador de productos en el botón
        const items = PEDIDOS_ITEMS[id] || [];
        const n = items.length;
        document.getElementById(`item-count-${id}`).textContent = `${n} producto${n !== 1 ? 's' : ''}`;
    });

    // Conectar botones de toggle (sin onclick inline)
    document.querySelectorAll('.toggle-items-btn').forEach(btn => {
        btn.addEventListener('click', () => toggleItems(btn.dataset.order));
    });
});
