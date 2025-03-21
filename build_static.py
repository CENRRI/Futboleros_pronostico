from app import procesar_pronosticos, obtener_resultados_guardados, calcular_puntos, pronosticos_raw

def generar_html_estatico(pronosticos, resultados, ranking_ordenado, labels, datos):
    html = """<!DOCTYPE html>
    <html>
    <head>
        <title>Ranking de Pronósticos</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { 
                padding: 20px; 
                background-color: #0a192f;
                color: #ffffff !important;
            }
            .card { 
                margin-bottom: 20px;
                background-color: #112240;
                border-color: #233554;
            }
            .table {
                color: #ffffff !important;
            }
            .table td, .table th {
                color: #ffffff !important;
            }
            .table-striped > tbody > tr:nth-of-type(odd) {
                background-color: #112240;
            }
            .table-striped > tbody > tr:nth-of-type(even) {
                background-color: #1a365d;
            }
            thead tr {
                background-color: #233554 !important;
            }
            .chart-container {
                position: relative;
                height: 400px;
                width: 100%;
            }
            .form-control, .form-select {
                background-color: #1a365d;
                border-color: #233554;
                color: #ffffff;
            }
            .jugado-row { background-color: rgba(46, 204, 113, 0.2) !important; }
            .pendiente-row { background-color: rgba(231, 76, 60, 0.2) !important; }
        </style>
    </head>
    <body>
        <div class="container mt-5">
            <h1 class="text-center mb-4 text-light">Ranking de Pronósticos</h1>
            
            <!-- Gráfico -->
            <div class="card mb-4">
                <div class="card-header bg-primary text-white">
                    <h2 class="h5 mb-0">Gráfico de Puntuaciones</h2>
                </div>
                <div class="card-body chart-container">
                    <canvas id="rankingChart"></canvas>
                </div>
            </div>

            <!-- Tabla de Apuestas -->
            <div class="card mb-4">
                <div class="card-header bg-warning">
                    <h2 class="h5 mb-0">Tabla de Apuestas</h2>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Jugador</th>
                                    <th>PAR</th>
                                    <th>CHI</th>
                                    <th>BRA</th>
                                    <th>COL</th>
                                    <th>PER</th>
                                    <th>BOL</th>
                                    <th>ECU</th>
                                    <th>VEN</th>
                                    <th>URU</th>
                                    <th>ARG</th>
                                </tr>
                            </thead>
                            <tbody>"""

    # Add betting table rows with actual data
    for jugador, predicciones in pronosticos.items():
        html += f"""
                                <tr>
                                    <td>{jugador}</td>
                                    <td>{predicciones.get('PARAGUAY', '-')}</td>
                                    <td>{predicciones.get('CHILE', '-')}</td>
                                    <td>{predicciones.get('BRASIL', '-')}</td>
                                    <td>{predicciones.get('COLOMBIA', '-')}</td>
                                    <td>{predicciones.get('PERU', '-')}</td>
                                    <td>{predicciones.get('BOLIVIA', '-')}</td>
                                    <td>{predicciones.get('ECUADOR', '-')}</td>
                                    <td>{predicciones.get('VENEZUELA', '-')}</td>
                                    <td>{predicciones.get('URUGUAY', '-')}</td>
                                    <td>{predicciones.get('ARGENTINA', '-')}</td>
                                </tr>"""

    html += """
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Resultados de Partidos -->
            <div class="card mb-4">
                <div class="card-header bg-info text-white">
                    <h2 class="h5 mb-0">Resultados de Partidos</h2>
                </div>
                <div class="card-body">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Partido</th>
                                <th>Resultado</th>
                                <th>Estado</th>
                            </tr>
                        </thead>
                        <tbody>"""

    # Actualizar la sección de resultados de partidos
    for partido, datos in resultados.items():
        equipo1, equipo2 = partido.split()
        estado = "Jugado" if datos['jugado'] else "Pendiente"
        
        html += f"""
                            <tr class="{estado.lower()}-row">
                                <td>{equipo1} vs {equipo2}</td>
                                <td>
                                    <div class="d-flex align-items-center">
                                        <input type="number" class="form-control form-control-sm me-2" 
                                            style="width: 60px" value="{datos['goles1']}" 
                                            id="goles1_{equipo1}_{equipo2}" min="0">
                                        <span class="mx-2">-</span>
                                        <input type="number" class="form-control form-control-sm ms-2" 
                                            style="width: 60px" value="{datos['goles2']}" 
                                            id="goles2_{equipo1}_{equipo2}" min="0">
                                    </div>
                                </td>
                                <td>
                                    <select class="form-select form-select-sm" id="estado_{equipo1}_{equipo2}">
                                        <option value="Pendiente" {'' if datos['jugado'] else 'selected'}>Pendiente</option>
                                        <option value="Jugado" {'selected' if datos['jugado'] else ''}>Jugado</option>
                                    </select>
                                </td>
                            </tr>"""

    html += """
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Ranking de Jugadores -->
            <div class="card">
                <div class="card-header bg-success text-white">
                    <h2 class="h5 mb-0">Ranking de Jugadores</h2>
                </div>
                <div class="card-body">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Posición</th>
                                <th>Jugador</th>
                                <th>Puntos Totales</th>
                                <th>Exactos (3 pts)</th>
                                <th>Aciertos (1 pt)</th>
                                <th>Contrarios (0 pt)</th>
                                <th>Partidos Jugados</th>
                            </tr>
                        </thead>
                        <tbody>"""

    # Add ranking rows
    for pos, (jugador, stats) in enumerate(ranking_ordenado, 1):
        html += f"""
                            <tr>
                                <td>{pos}</td>
                                <td>{jugador}</td>
                                <td>{stats['puntos_totales']}</td>
                                <td>{stats['exactos']}</td>
                                <td>{stats['aciertos']}</td>
                                <td>{stats['contrarios']}</td>
                                <td>{stats['partidos_jugados']}</td>
                            </tr>"""

    html += """
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        <div class="text-center mt-3 mb-5">
            <button class="btn btn-primary" onclick="guardarResultados()">Guardar Resultados</button>
        </div>
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                try {
                    const ctx = document.getElementById('rankingChart').getContext('2d');
                    new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: [""" + ", ".join(f"'{label}'" for label in labels) + """],
                            datasets: [{
                                label: 'Puntos',
                                data: [""" + ", ".join(map(str, datos)) + """],
                                backgroundColor: ['#4a90e2', '#2ecc71', '#e74c3c', '#f1c40f', '#9b59b6', '#1abc9c', '#e67e22'],
                                borderWidth: 1,
                                borderColor: '#ffffff'
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    grid: { color: '#233554' },
                                    ticks: { color: '#ffffff', font: { size: 14 } }
                                },
                                x: {
                                    grid: { color: '#233554' },
                                    ticks: { 
                                        color: '#ffffff', 
                                        font: { size: 14 },
                                        autoSkip: false,
                                        maxRotation: 45,
                                        minRotation: 45
                                    }
                                }
                            },
                            plugins: {
                                legend: {
                                    labels: { color: '#ffffff', font: { size: 14 } }
                                }
                            }
                        }
                    });
                } catch (error) {
                    console.error('Error al crear el gráfico:', error);
                }
            });
            
            function guardarResultados() {
                const resultados = {};
                document.querySelectorAll('tr').forEach(row => {
                    const equipos = row.querySelector('td')?.textContent.split(' vs ');
                    if (equipos && equipos.length === 2) {
                        const equipo1 = equipos[0].trim();
                        const equipo2 = equipos[1].trim();
                        const goles1 = document.getElementById(`goles1_${equipo1}_${equipo2}`).value;
                        const goles2 = document.getElementById(`goles2_${equipo1}_${equipo2}`).value;
                        const estado = document.getElementById(`estado_${equipo1}_${equipo2}`).value;
                        
                        resultados[`${equipo1} ${equipo2}`] = {
                            goles1: parseInt(goles1) || 0,
                            goles2: parseInt(goles2) || 0,
                            jugado: estado === 'Jugado'
                        };
                    }
                });
                
                fetch('/guardar_resultados', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(resultados)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Resultados guardados correctamente');
                        location.reload();
                    } else {
                        alert('Error al guardar los resultados');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error al guardar los resultados');
                });
            }
        </script>
    </body>
    </html>"""
    return html


if __name__ == '__main__':
    # Obtener datos
    pronosticos = procesar_pronosticos(pronosticos_raw)
    resultados = obtener_resultados_guardados()
    ranking_ordenado = calcular_puntos(pronosticos, resultados)
    
    # Preparar datos para el gráfico
    labels = [jugador for jugador, _ in ranking_ordenado]
    datos = [stats['puntos_totales'] for _, stats in ranking_ordenado]
    
    # Generar HTML
    html_content = generar_html_estatico(pronosticos, resultados, ranking_ordenado, labels, datos)
    
    # Guardar el archivo en la ubicación correcta para GitHub Pages
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("Archivo HTML generado correctamente como index.html")