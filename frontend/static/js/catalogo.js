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
            var show   = (genero === 'todos'  && gender === 'accesorios') ||
                         (genero === 'hombre' && (gender === 'hombre' || gender === 'unisex')) ||
                         (genero === 'mujer'  && (gender === 'mujer'  || gender === 'unisex'));
            card.style.display = show ? '' : 'none';
            if (show) visible++;
        });

        // Actualizar contador
        var countEl = document.getElementById('catalogo-count');
        if (countEl) {
            var label = genero === 'todos'  ? 'accesorios' :
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

        var q = new URLSearchParams(window.location.search).get('q');
        if (q) {
            filtrarPorBusqueda(q);
        } else {
            setTab(generoInicial || 'hombre');
        }
    });

    function filtrarPorBusqueda(q) {
        // Desactivar todos los tabs
        ['hombre', 'mujer', 'todos'].forEach(function (g) {
            var btn = document.getElementById('tab-' + g);
            if (btn) btn.classList.remove('active');
        });

        var termino = q.toLowerCase();
        var cards   = document.querySelectorAll('#catalogo-grid .catalogo-card');
        var visible = 0;

        cards.forEach(function (card) {
            var nombre = (card.querySelector('.catalogo-card__name') || card).textContent.toLowerCase();
            var show   = nombre.includes(termino);
            card.style.display = show ? '' : 'none';
            if (show) visible++;
        });

        var countEl = document.getElementById('catalogo-count');
        if (countEl) countEl.textContent = visible + ' resultado' + (visible !== 1 ? 's' : '') + ' para "' + q + '"';

        var noResults = document.getElementById('no-results');
        if (noResults) noResults.style.display = visible === 0 ? 'block' : 'none';
    }

})();
