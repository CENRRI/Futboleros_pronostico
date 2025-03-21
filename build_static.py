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
                <div class="card-body">
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

    # Add match results
    for partido, datos in resultados.items():
        equipo1, equipo2 = partido.split()
        estado = "Jugado" if datos['jugado'] else "Pendiente"
        resultado = f"{datos['goles1']} - {datos['goles2']}" if datos['jugado'] else "-"
        
        html += f"""
                            <tr>
                                <td>{equipo1} vs {equipo2}</td>
                                <td>{resultado}</td>
                                <td>{estado}</td>
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
        <script>
            const ctx = document.getElementById('rankingChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: [""" + ", ".join(labels) + """],
                    datasets: [{
                        label: 'Puntos',
                        data: [""" + ", ".join(map(str, datos)) + """],
                        backgroundColor: '#4a90e2'
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: { color: '#233554' },
                            ticks: { color: '#ffffff' }
                        },
                        x: {
                            grid: { color: '#233554' },
                            ticks: { color: '#ffffff' }
                        }
                    },
                    plugins: {
                        legend: {
                            labels: { color: '#ffffff' }
                        }
                    }
                }
            });
        </script>
    </body>
    </html>"""
    return html

def generar_pagina_estatica():
    # Obtener datos
    pronosticos = procesar_pronosticos(pronosticos_raw)
    resultados = obtener_resultados_guardados()
    puntuaciones = calcular_puntos(pronosticos, {})
    
    ranking_ordenado = sorted(puntuaciones.items(), 
                            key=lambda x: (x[1]["puntos_totales"], x[1]["exactos"]), 
                            reverse=True)
    
    labels = [f"'{jugador}'" for jugador, _ in ranking_ordenado]
    datos = [stats["puntos_totales"] for _, stats in ranking_ordenado]
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(generar_html_estatico(pronosticos, resultados, ranking_ordenado, labels, datos))

if __name__ == '__main__':
    generar_pagina_estatica()