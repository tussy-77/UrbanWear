(function () {

    function setTab(genero) {
        // Actualizar tabs
        ['hombre', 'mujer', 'todos'].forEach(function (g) {
            var btn = document.getElementById('tab-' + g);
            if (!btn) return;
            if (g === genero) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // Filtrar tarjetas
        var cards   = document.querySelectorAll('#catalogo-grid .catalogo-card');
        var visible = 0;

        cards.forEach(function (card) {
            var gender = card.getAttribute('data-gender') || 'unisex';
            var show   = genero === 'todos' ||
                         (genero === 'hombre' && (gender === 'hombre' || gender === 'unisex')) ||
                         (genero === 'mujer'  && (gender === 'mujer'  || gender === 'unisex'));
            card.style.display = show ? '' : 'none';
            if (show) visible++;
        });

        // Actualizar contador
        var countEl = document.getElementById('catalogo-count');
        if (countEl) {
            var label = genero === 'todos' ? 'todos los productos' :
                        genero === 'hombre' ? 'colección hombre' : 'colección mujer';
            countEl.textContent = visible + ' producto' + (visible !== 1 ? 's' : '') + ' — ' + label;
        }

        // Mostrar/ocultar mensaje de sin resultados
        var noResults = document.getElementById('no-results');
        if (noResults) noResults.style.display = visible === 0 ? 'block' : 'none';
    }

    window.setTab = setTab;

    document.addEventListener('DOMContentLoaded', function () {
        var configEl      = document.getElementById('catalogo-config');
        var generoInicial = configEl ? JSON.parse(configEl.textContent) : 'hombre';
        setTab(generoInicial || 'hombre');
    });

})();
