function abrirModalAgregar() {
    document.getElementById('modal-agregar').classList.add('active');
}

function abrirModalEditarBtn(btn) {
    var genero = btn.dataset.genero || 'unisex';
    var imagen = btn.dataset.imagen || '';
    
    document.getElementById('form-editar').action     = '/admin/productos/editar/' + btn.dataset.id;
    document.getElementById('edit-nombre').value      = btn.dataset.nombre;
    document.getElementById('edit-precio').value      = btn.dataset.precio;
    document.getElementById('edit-descripcion').value = btn.dataset.descripcion;
    document.getElementById('edit-stock').value       = btn.dataset.stock;
    document.getElementById('edit-tallas').value      = btn.dataset.tallas;
    document.getElementById('edit-imagen-url').value  = imagen.startsWith('http') ? imagen : '';
    document.getElementById('edit-genero').value      = genero;
    
    // Mostrar imagen actual
    const imgActual = document.getElementById('edit-imagen-actual');
    const sinImagen = document.getElementById('edit-sin-imagen');
    
    if (imagen && imagen.trim() !== '') {
        // Si es URL externa o path local
        let imgSrc = imagen;
        if (!imagen.startsWith('http')) {
            imgSrc = '/static/uploads/' + imagen;
        }
        imgActual.src = imgSrc;
        imgActual.style.display = 'block';
        sinImagen.style.display = 'none';
    } else {
        imgActual.style.display = 'none';
        sinImagen.style.display = 'block';
    }
    
    // Limpiar preview de nuevas imágenes
    document.getElementById('preview-editar').innerHTML = '';
    document.getElementById('editar-imagenes').value = '';
    
    document.getElementById('modal-editar').classList.add('active');
}

function cerrarModal(id) {
    document.getElementById(id).classList.remove('active');
}

// Preview imágenes múltiples
function configurarPreviewImagenes(inputId, previewId) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);
    const MAX_IMAGES = 3;

    input.addEventListener('change', function () {
        preview.innerHTML = '';
        
        // Validar cantidad de imágenes
        if (this.files.length > MAX_IMAGES) {
            alert(`Solo puedes seleccionar máximo ${MAX_IMAGES} imágenes`);
            this.value = '';
            return;
        }
        
        Array.from(this.files).forEach(function (file, index) {
            const reader = new FileReader();
            reader.onload = function (e) {
                const container = document.createElement('div');
                container.style.cssText = 'position:relative;';
                
                const img = document.createElement('img');
                img.src = e.target.result;
                img.style.cssText = 'width:60px; height:60px; object-fit:cover; border-radius:6px; border:1px solid #ddd;';
                
                const badge = document.createElement('div');
                badge.textContent = index + 1;
                badge.style.cssText = 'position:absolute; top:-6px; right:-6px; background:#111; color:#fff; border-radius:50%; width:20px; height:20px; display:flex; align-items:center; justify-content:center; font-size:0.75rem; font-weight:700;';
                
                container.appendChild(img);
                container.appendChild(badge);
                preview.appendChild(container);
            };
            reader.readAsDataURL(file);
        });
    });
}
//ya incluye todo este document
document.addEventListener('DOMContentLoaded', function () {
    // Cierre de modales al hacer clic fuera
    document.querySelectorAll('.admin-modal').forEach(function (modal) {
        modal.addEventListener('click', function (e) {
            if (e.target === this) cerrarModal(this.id);
        });
    });

    // Preview imágenes
    configurarPreviewImagenes('agregar-imagenes', 'preview-agregar');
    configurarPreviewImagenes('editar-imagenes', 'preview-editar');
});
