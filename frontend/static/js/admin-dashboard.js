document.addEventListener('DOMContentLoaded', function () {

    var dataEl = document.getElementById('dashboard-data');
    if (!dataEl) return;

    var _d             = JSON.parse(dataEl.textContent);
    var mesesLabels    = _d.mesesLabels;
    var mesesTotales   = _d.mesesTotales;
    var estadosLabels  = _d.estadosLabels;
    var estadosValores = _d.estadosValores;

    // Gráfica de barras — ventas mensuales
    new Chart(document.getElementById('chartVentas'), {
        type: 'bar',
        data: {
            labels: mesesLabels,
            datasets: [{
                label: 'Ingresos ($)',
                data: mesesTotales,
                backgroundColor: 'rgba(255, 107, 53, 0.15)',
                borderColor: '#ff6b35',
                borderWidth: 2,
                borderRadius: 6,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function (ctx) {
                            return ' $' + ctx.parsed.y.toLocaleString('es-CO');
                        }
                    }
                }
            },
            scales: {
                x: { grid: { display: false }, ticks: { font: { size: 11, weight: '600' } } },
                y: {
                    grid: { color: '#f0f0f0' },
                    ticks: {
                        font: { size: 10 },
                        callback: function (v) {
                            return '$' + (v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v);
                        }
                    }
                }
            }
        }
    });

    // Gráfica de dona — pedidos por estado
    var coloresDona = ['#ff6b35', '#111', '#888', '#e5e5e5', '#e53e3e'];
    new Chart(document.getElementById('chartEstados'), {
        type: 'doughnut',
        data: {
            labels: estadosLabels,
            datasets: [{
                data: estadosValores,
                backgroundColor: coloresDona.slice(0, estadosLabels.length),
                borderWidth: 0,
                hoverOffset: 6,
            }]
        },
        options: {
            responsive: true,
            cutout: '68%',
            plugins: { legend: { display: false } }
        }
    });

    // Leyenda manual de la dona
    var leyenda = document.getElementById('estadosLeyenda');
    if (leyenda) {
        estadosLabels.forEach(function (label, i) {
            var el = document.createElement('div');
            el.style.cssText = 'display:flex;align-items:center;gap:5px;font-size:0.72rem;font-weight:600;';
            el.innerHTML = '<span style="width:10px;height:10px;border-radius:50%;background:' +
                           coloresDona[i] + ';display:inline-block;"></span>' +
                           label + ' (' + estadosValores[i] + ')';
            leyenda.appendChild(el);
        });
    }

});
