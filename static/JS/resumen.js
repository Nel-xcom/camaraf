document.addEventListener('DOMContentLoaded', function() {
    const dataElement = document.getElementById('chart-data');
    if (!dataElement) {
        console.error("No se encontró el elemento chart-data.");
        return;
    }

    try {
        const data = JSON.parse(dataElement.textContent);
        console.log("Datos cargados:", data);  // ✅ Verifica en consola

        data.forEach((item, index) => {
            const canvas = document.getElementById(`chart-${index + 1}`);
            if (!canvas) return;

            // Si importe_liquidado es null o undefined, poner 0
            const importeLiquidado = item.importe_liquidado ?? 0;

            new Chart(canvas, {
                type: 'bar',
                data: {
                    labels: ['Importe total a liquidar', 'Importe Liquidado'],
                    datasets: [{
                        label: 'Montos ($)',
                        data: [item.importe_100, importeLiquidado],
                        backgroundColor: ['#8cc0e8', '#4070b7']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        });

    } catch (error) {
        console.error("Error al parsear JSON:", error);
        console.error("Contenido del JSON:", dataElement.textContent);
    }
});
