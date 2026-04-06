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

    // Reveal escalonado de los productos New In y Essential al hacer scroll
    var revealItems = document.querySelectorAll('.newin-item');
    if (revealItems.length) {
        if ('IntersectionObserver' in window) {
            var observer = new IntersectionObserver(function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('is-visible');
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.12 });

            revealItems.forEach(function (el) {
                observer.observe(el);
            });
        } else {
            // Fallback para navegadores sin IntersectionObserver
            revealItems.forEach(function (el) {
                el.classList.add('is-visible');
            });
        }
    }

});
