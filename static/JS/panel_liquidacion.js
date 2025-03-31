const pagosPorObra = {{ datos_panel.pagos_por_obra|safe }};
            const ctx1 = document.getElementById('pagosObraSocial').getContext('2d');
            new Chart(ctx1, {
                type: 'pie',
                data: {
                    labels: Object.keys(pagosPorObra),
                    datasets: [{
                        data: Object.values(pagosPorObra),
                        backgroundColor: ['#2ECC71', '#FF6B6B', '#F4D03F']
                    }]
                }
            });

            const evolucionPagos = {{ datos_panel.evolucion_pagos|safe }};
            const ctx2 = document.getElementById('evolucionPagos').getContext('2d');
            new Chart(ctx2, {
                type: 'line',
                data: {
                    labels: Object.keys(evolucionPagos),
                    datasets: [{
                        data: Object.values(evolucionPagos),
                        borderColor: '#4070B7',
                        fill: false
                    }]
                }
            });