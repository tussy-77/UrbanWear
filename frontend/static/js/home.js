document.addEventListener('DOMContentLoaded', function () {

    // Aplicar imágenes de fondo a todos los elementos con data-bg
    document.querySelectorAll('[data-bg]').forEach(function (el) {
        var bg = el.getAttribute('data-bg');
        if (bg) el.style.backgroundImage = "url('" + bg + "')";
    });

    // Hero: mostrar overlay y ocultar patrón decorativo si hay imagen de fondo
    var heroBg = document.getElementById('hero-bg');
    if (heroBg && heroBg.getAttribute('data-bg')) {
        var overlay = document.getElementById('hero-overlay');
        var pattern = document.getElementById('hero-pattern');
        if (overlay) overlay.style.background = 'rgba(0,0,0,0.5)';
        if (pattern) pattern.style.display = 'none';
    }

});
