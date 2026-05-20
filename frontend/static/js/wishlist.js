// Wishlist — corazones y página de favoritos

let _wishlistIds = new Set();

async function initWishlist() {
    const token = localStorage.getItem('urban_token');
    if (!token) return;
    try {
        const res = await fetch('/api/wishlist', {
            headers: { Authorization: `Bearer ${token}` }
        });
        if (!res.ok) return;
        const data = await res.json();
        _wishlistIds = new Set(data.ids);
        _renderHearts();
    } catch (_) {}
}

function _renderHearts() {
    document.querySelectorAll('[data-wishlist-id]').forEach(btn => {
        const id = parseInt(btn.dataset.wishlistId);
        _setHeartActive(btn, _wishlistIds.has(id));
    });
}

function _setHeartActive(btn, active) {
    const svg = btn.querySelector('svg');
    if (!svg) return;
    const isProductoPage = btn.classList.contains('wishlist-btn--producto');
    if (active) {
        svg.setAttribute('fill', 'currentColor');
        btn.classList.add('wishlist-active');
        if (isProductoPage) btn.style.borderColor = '#111';
    } else {
        svg.setAttribute('fill', 'none');
        btn.classList.remove('wishlist-active');
        if (isProductoPage) btn.style.borderColor = '#ddd';
    }
}

async function toggleWishlist(btn, productId) {
    const token = localStorage.getItem('urban_token');
    if (!token) {
        if (typeof abrirModal === 'function') abrirModal('main');
        return;
    }

    // optimistic
    const wasSaved = _wishlistIds.has(productId);
    if (wasSaved) {
        _wishlistIds.delete(productId);
    } else {
        _wishlistIds.add(productId);
    }
    _setHeartActive(btn, !wasSaved);

    try {
        const res = await fetch(`/api/wishlist/${productId}`, {
            method: 'POST',
            headers: { Authorization: `Bearer ${token}` }
        });
        if (!res.ok) throw new Error();
        const data = await res.json();
        if (typeof mostrarToast === 'function') {
            mostrarToast(data.saved ? 'Guardado en favoritos' : 'Eliminado de favoritos');
        }
    } catch (_) {
        // revert
        if (wasSaved) {
            _wishlistIds.add(productId);
        } else {
            _wishlistIds.delete(productId);
        }
        _setHeartActive(btn, wasSaved);
    }
}

// ── Página /favoritos ────────────────────────────────────────────────────────

async function loadFavoritos() {
    const grid = document.getElementById('favoritos-grid');
    const empty = document.getElementById('favoritos-empty');
    if (!grid) return;

    const token = localStorage.getItem('urban_token');
    if (!token) {
        if (empty) { empty.style.display = 'block'; }
        grid.style.display = 'none';
        return;
    }

    try {
        const res = await fetch('/api/wishlist/products', {
            headers: { Authorization: `Bearer ${token}` }
        });
        const data = await res.json();
        const products = data.products || [];

        if (products.length === 0) {
            if (empty) empty.style.display = 'block';
            grid.style.display = 'none';
            return;
        }

        grid.innerHTML = products.map(p => `
            <div class="fav-card" id="fav-card-${p.id}">
                <a href="/producto/${p.id}" class="fav-card__img-wrap">
                    <img src="${p.image_src || '/static/img/placeholder.png'}" alt="${p.name}" loading="lazy">
                </a>
                <div class="fav-card__body">
                    <a href="/producto/${p.id}" class="fav-card__name">${p.name}</a>
                    <span class="fav-card__price">$${p.price.toLocaleString('es-CO')}</span>
                    <div class="fav-card__actions">
                        <button class="fav-card__remove" onclick="removeFavorito(${p.id}, this)">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
                            Eliminar
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
        grid.style.display = 'grid';
        if (empty) empty.style.display = 'none';
    } catch (_) {
        if (empty) empty.style.display = 'block';
        grid.style.display = 'none';
    }
}

async function removeFavorito(productId, btn) {
    const token = localStorage.getItem('urban_token');
    if (!token) return;
    try {
        await fetch(`/api/wishlist/${productId}`, {
            method: 'POST',
            headers: { Authorization: `Bearer ${token}` }
        });
        const card = document.getElementById(`fav-card-${productId}`);
        if (card) {
            card.style.opacity = '0';
            card.style.transform = 'scale(0.95)';
            card.style.transition = 'opacity 0.25s, transform 0.25s';
            setTimeout(() => { card.remove(); checkEmpty(); }, 260);
        }
    } catch (_) {}
}

function checkEmpty() {
    const grid = document.getElementById('favoritos-grid');
    const empty = document.getElementById('favoritos-empty');
    if (grid && grid.children.length === 0) {
        grid.style.display = 'none';
        if (empty) empty.style.display = 'block';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initWishlist();
    loadFavoritos();
});
