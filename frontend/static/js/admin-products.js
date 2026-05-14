// ─── Archivos acumulados por modal ───────────────────────────────────────────
// Guardamos los File objects seleccionados individualmente
var archivosAgregar = [];  // máximo 3
var archivosEditar  = [];  // máximo 3
var slotActivoId    = null; // qué picker se abrió ('agregar' o 'editar')

// ─── Renderiza los slots de imagen ───────────────────────────────────────────
// modalId: 'agregar' o 'editar'
function renderSlots(modalId) {
    var archivos = modalId === 'agregar' ? archivosAgregar : archivosEditar;
    var container = document.getElementById('slots-' + modalId);
    container.innerHTML = '';

    // Dibuja un slot por cada archivo ya seleccionado
    archivos.forEach(function (file, i) {
        var url = URL.createObjectURL(file);

        var slot = document.createElement('div');
        slot.style.cssText = 'position:relative; width:72px; height:72px;';

        // Preview de la imagen
        var img = document.createElement('img');
        img.src = url;
        img.style.cssText = 'width:72px; height:72px; object-fit:cover; border-radius:8px; border:2px solid #ddd;';

        // Número de orden encima
        var badge = document.createElement('div');
        badge.textContent = i + 1;
        badge.style.cssText = [
            'position:absolute; top:-7px; left:-7px;',
            'background:#111; color:#fff;',
            'border-radius:50%; width:20px; height:20px;',
            'display:flex; align-items:center; justify-content:center;',
            'font-size:0.72rem; font-weight:700;'
        ].join('');

        // Botón X para eliminar ese archivo
        var btnX = document.createElement('button');
        btnX.type = 'button';
        btnX.textContent = '×';
        btnX.style.cssText = [
            'position:absolute; top:-7px; right:-7px;',
            'background:#e53e3e; color:#fff; border:none; cursor:pointer;',
            'border-radius:50%; width:20px; height:20px;',
            'display:flex; align-items:center; justify-content:center;',
            'font-size:0.9rem; font-weight:700; line-height:1;'
        ].join('');
        btnX.onclick = function () {
            // Elimina ese archivo del array y re-renderiza
            if (modalId === 'agregar') {
                archivosAgregar.splice(i, 1);
            } else {
                archivosEditar.splice(i, 1);
            }
            renderSlots(modalId);
        };

        slot.appendChild(img);
        slot.appendChild(badge);
        slot.appendChild(btnX);
        container.appendChild(slot);
    });

    // Si hay menos de 3, muestra el botón "+"
    if (archivos.length < 3) {
        var btnAdd = document.createElement('button');
        btnAdd.type = 'button';
        btnAdd.textContent = '+';
        btnAdd.title = 'Agregar imagen';
        btnAdd.style.cssText = [
            'width:72px; height:72px; border-radius:8px;',
            'border:2px dashed #bbb; background:#fafafa;',
            'font-size:2rem; color:#bbb; cursor:pointer;',
            'display:flex; align-items:center; justify-content:center;',
            'transition: border-color 0.2s, color 0.2s;'
        ].join('');
        btnAdd.onmouseover = function () {
            this.style.borderColor = '#111';
            this.style.color = '#111';
        };
        btnAdd.onmouseout = function () {
            this.style.borderColor = '#bbb';
            this.style.color = '#bbb';
        };
        btnAdd.onclick = function () {
            // Guardamos qué modal disparó el picker
            slotActivoId = modalId;
            document.getElementById('picker-' + modalId).click();
        };
        container.appendChild(btnAdd);
    }

    // Sincroniza los File objects al formulario para que Flask los reciba
    sincronizarInputOculto(modalId, archivos);
}

// ─── Crea un DataTransfer con los archivos y lo asigna a un input real ───────
// Flask recibe el campo "imagen" con todos los archivos acumulados
function sincronizarInputOculto(modalId, archivos) {
    // Buscamos o creamos el input real que va dentro del form
    var formId  = modalId === 'agregar' ? 'form-agregar' : 'form-editar';
    var inputId = 'input-real-' + modalId;
    var form    = document.getElementById(formId);

    var inputReal = document.getElementById(inputId);
    if (!inputReal) {
        inputReal = document.createElement('input');
        inputReal.type     = 'file';
        inputReal.name     = 'imagen';   // nombre que lee Flask
        inputReal.id       = inputId;
        inputReal.multiple = true;
        inputReal.style.display = 'none';
        form.appendChild(inputReal);
    }

    // Transfiere los File objects al input real
    var dt = new DataTransfer();
    archivos.forEach(function (f) { dt.items.add(f); });
    inputReal.files = dt.files;
}

// ─── Modales ─────────────────────────────────────────────────────────────────
function abrirModalAgregar() {
    archivosAgregar = [];
    renderSlots('agregar');
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

    // Imagen actual del producto
    var imgActual = document.getElementById('edit-imagen-actual');
    var sinImagen = document.getElementById('edit-sin-imagen');
    if (imagen && imagen.trim() !== '') {
        imgActual.src          = imagen.startsWith('http') ? imagen : '/static/uploads/' + imagen;
        imgActual.style.display = 'block';
        sinImagen.style.display = 'none';
    } else {
        imgActual.style.display = 'none';
        sinImagen.style.display = 'block';
    }

    // Limpiar slots de editar
    archivosEditar = [];
    renderSlots('editar');

    document.getElementById('modal-editar').classList.add('active');
}

function cerrarModal(id) {
    document.getElementById(id).classList.remove('active');
}

// ─── Inicialización ──────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {

    // Cierre de modales al hacer clic fuera
    document.querySelectorAll('.admin-modal').forEach(function (modal) {
        modal.addEventListener('click', function (e) {
            if (e.target === this) cerrarModal(this.id);
        });
    });

    // Render inicial de slots vacíos
    renderSlots('agregar');
    renderSlots('editar');

    // Picker de agregar — cuando el usuario elige un archivo
    document.getElementById('picker-agregar').addEventListener('change', function () {
        if (this.files[0] && archivosAgregar.length < 3) {
            archivosAgregar.push(this.files[0]);
            renderSlots('agregar');
        }
        this.value = ''; // reset para poder elegir el mismo archivo otra vez
    });

    // Picker de editar — cuando el usuario elige un archivo
    document.getElementById('picker-editar').addEventListener('change', function () {
        if (this.files[0] && archivosEditar.length < 3) {
            archivosEditar.push(this.files[0]);
            renderSlots('editar');
        }
        this.value = '';
    });
});