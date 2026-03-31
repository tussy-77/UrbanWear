function abrirModalAgregar() {
    document.getElementById('modal-agregar').classList.add('active');
}

function abrirModalEditarBtn(btn) {
    var genero = btn.dataset.genero || 'unisex';
    document.getElementById('form-editar').action     = '/admin/productos/editar/' + btn.dataset.id;
    document.getElementById('edit-nombre').value      = btn.dataset.nombre;
    document.getElementById('edit-precio').value      = btn.dataset.precio;
    document.getElementById('edit-descripcion').value = btn.dataset.descripcion;
    document.getElementById('edit-stock').value       = btn.dataset.stock;
    document.getElementById('edit-tallas').value      = btn.dataset.tallas;
    document.getElementById('edit-imagen-url').value  = btn.dataset.imagen.startsWith('http') ? btn.dataset.imagen : '';
    document.getElementById('edit-genero').value      = genero;
    document.getElementById('modal-editar').classList.add('active');
}

function cerrarModal(id) {
    document.getElementById(id).classList.remove('active');
}

document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.admin-modal').forEach(function (modal) {
        modal.addEventListener('click', function (e) {
            if (e.target === this) cerrarModal(this.id);
        });
    });
});
