document.addEventListener('DOMContentLoaded', function () {

    // Aplicar imágenes de fondo a todos los previews con data-bg
    document.querySelectorAll('[data-bg]').forEach(function (el) {
        var bg = el.getAttribute('data-bg');
        if (bg) el.style.backgroundImage = "url('" + bg + "')";
    });

});
