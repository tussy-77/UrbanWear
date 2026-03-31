(function () {

    var ACTIVE_COLOR = '#FF6B00';

    function setTab(genero) {
        ['hombre', 'mujer', 'todos'].forEach(function (g) {
            var btn = document.getElementById('tab-' + g);
            if (!btn) return;
            btn.style.borderBottomColor = g === genero ? ACTIVE_COLOR : 'transparent';
            btn.style.color             = g === genero ? ACTIVE_COLOR : '#333';
        });

        var cards   = document.querySelectorAll('#catalogo-grid .product-card');
        var visible = 0;

        cards.forEach(function (card) {
            var gender = card.getAttribute('data-gender') || 'unisex';
            var show   = genero === 'todos' ||
                         (genero === 'hombre' && (gender === 'hombre' || gender === 'unisex')) ||
                         (genero === 'mujer'  && (gender === 'mujer'  || gender === 'unisex'));
            card.style.display = show ? '' : 'none';
            if (show) visible++;
        });

        var countEl = document.getElementById('catalogo-count');
        if (countEl) {
            var label = genero === 'todos' ? 'Todos los productos' :
                        genero === 'hombre' ? 'Hombre' : 'Mujer';
            countEl.textContent = visible + ' producto' + (visible !== 1 ? 's' : '') + ' — ' + label;
        }

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
