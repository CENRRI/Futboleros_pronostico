from collections import defaultdict
from flask import Flask, render_template_string, request, redirect, url_for
import json
from flask import Flask, render_template
app = Flask(__name__)

# Tabla de pronósticos
pronosticos_raw = """JUGADOR PARAGUAY CHILE BRASIL COLOMBIA PERU BOLIVIA ECUADOR VENEZUELA URUGUAY ARGENTINA
KEVIN 1 0 1 1 1 0 2 1 1 1
EMANUELLE 1 2 3 1 1 0 2 1 0 2
ALVARO 2 2 2 1 2 0 2 0 1 2
HUGO 1 0 2 1 1 0 2 0 1 1
CESAR 1 0 2 1 1 0 2 1 1 2
CARLOS 2 0 2 1 2 0 2 1 1 1
BERLY 2 0 1 0 2 1 3 0 0 0"""

@app.route('/')
def index():
    pronosticos = procesar_pronosticos(pronosticos_raw)
    resultados = procesar_resultados(obtener_resultados_guardados())
    puntuaciones = calcular_puntos(pronosticos, resultados)
    return generar_html(pronosticos, resultados, puntuaciones)

def procesar_pronosticos(raw_data):
    lines = raw_data.strip().split('\n')
    headers = lines[0].split()
    pronosticos = {}
    for line in lines[1:]:
        datos = line.split()
        jugador = datos[0]
        pronosticos[jugador] = {headers[i]: int(datos[i]) for i in range(1, len(datos))}
    return pronosticos

def procesar_resultados(resultados_dict):
    resultados = {}
    for partido, datos in resultados_dict.items():
        if datos['jugado'] and datos['goles1'] != 'x' and datos['goles2'] != 'x':
            equipo1, equipo2 = partido.split()
            try:
                resultados[equipo1] = int(datos['goles1'])
                resultados[equipo2] = int(datos['goles2'])
            except ValueError:
                continue
    return resultados

def guardar_resultados(resultados):
    ruta_archivo = r"c:\Users\WORD STATIUM\OneDrive\Documentos\agente\exceldatos\pronostico\resultados.json"
    try:
        with open(ruta_archivo, 'w') as f:
            json.dump(resultados, f, indent=4)
            f.flush()
    except Exception as e:
        print(f"Error guardando resultados: {e}")

def obtener_resultados_guardados():
    ruta_archivo = r"c:\Users\WORD STATIUM\OneDrive\Documentos\agente\exceldatos\pronostico\resultados.json"
    try:
        with open(ruta_archivo, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        resultados_iniciales = {
            "PARAGUAY CHILE": {'goles1': 'x', 'goles2': 'x', 'jugado': False},
            "BRASIL COLOMBIA": {'goles1': 'x', 'goles2': 'x', 'jugado': False},
            "PERU BOLIVIA": {'goles1': 'x', 'goles2': 'x', 'jugado': False},
            "ECUADOR VENEZUELA": {'goles1': 'x', 'goles2': 'x', 'jugado': False},
            "URUGUAY ARGENTINA": {'goles1': 'x', 'goles2': 'x', 'jugado': False}
        }
        with open(ruta_archivo, 'w') as f:
            json.dump(resultados_iniciales, f, indent=4)
        return resultados_iniciales

def calcular_puntos(pronosticos, resultados):
    puntuaciones = defaultdict(lambda: {
        "puntos_totales": 0,
        "exactos": 0,
        "aciertos": 0,
        "contrarios": 0,
        "partidos_jugados": 0
    })
    
    # Obtener resultados del archivo JSON
    resultados_guardados = obtener_resultados_guardados()
    
    # Procesar solo partidos jugados
    for partido, datos in resultados_guardados.items():
        if datos['jugado'] and datos['goles1'] != 'x' and datos['goles2'] != 'x':
            equipo1, equipo2 = partido.split()
            try:
                goles1 = int(datos['goles1'])
                goles2 = int(datos['goles2'])
                
                # Calcular puntos para cada jugador
                for jugador, predicciones in pronosticos.items():
                    puntuaciones[jugador]["partidos_jugados"] += 1
                    
                    # Obtener predicciones del jugador
                    pred1 = predicciones[equipo1]
                    pred2 = predicciones[equipo2]
                    
                    # EXACTO (3 puntos): mismo resultado y goles
                    if pred1 == goles1 and pred2 == goles2:
                        puntuaciones[jugador]["puntos_totales"] += 3
                        puntuaciones[jugador]["exactos"] += 1
                    # ACIERTO (1 punto): acertó quién ganó pero no los goles
                    elif (pred1 > pred2 and goles1 > goles2) or \
                         (pred1 < pred2 and goles1 < goles2) or \
                         (pred1 == pred2 and goles1 == goles2):
                        puntuaciones[jugador]["puntos_totales"] += 1
                        puntuaciones[jugador]["aciertos"] += 1
                    # CONTRARIO (0 puntos): no acertó el resultado
                    else:
                        puntuaciones[jugador]["contrarios"] += 1
            except ValueError:
                continue
    
    return dict(puntuaciones)

@app.route('/actualizar_resultado', methods=['POST'])
def actualizar_resultado():
    equipo1 = request.form['equipo1']
    equipo2 = request.form['equipo2']
    goles1 = request.form.get('goles1', '')
    goles2 = request.form.get('goles2', '')
    
    # Modificar la lógica de jugado
    jugado = goles1 != '' and goles2 != '' and goles1 != 'x' and goles2 != 'x'
    
    try:
        if jugado:
            goles1 = int(goles1)
            goles2 = int(goles2)
        else:
            goles1 = 'x'
            goles2 = 'x'
    except ValueError:
        return "Los goles deben ser números", 400
    
    resultados_actuales = obtener_resultados_guardados()
    resultados_actuales[f"{equipo1} {equipo2}"] = {
        'goles1': goles1,
        'goles2': goles2,
        'jugado': jugado
    }
    guardar_resultados(resultados_actuales)
    return redirect(url_for('index'))

def generar_html(pronosticos, resultados, puntuaciones):
    # Get ranking data first
    ranking_ordenado = sorted(puntuaciones.items(), 
                            key=lambda x: (x[1]["puntos_totales"], x[1]["exactos"]), 
                            reverse=True)

    html = """
    <!DOCTYPE html>
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
                color: #ffffff !important;
            }
            .table-striped > tbody > tr:nth-of-type(even) {
                background-color: #1a365d;
                color: #ffffff !important;
            }
            .form-control {
                background-color: #1a365d;
                border-color: #233554;
                color: #ffffff !important;
            }
            .form-control:focus {
                background-color: #1a365d;
                border-color: #4a90e2;
                color: #ffffff !important;
            }
            .table-striped tbody tr:hover {
                background-color: #233554;
                color: #ffffff !important;
            }
            thead tr {
                background-color: #233554 !important;
                color: #ffffff !important;
            }
            th, td {
                color: #ffffff !important;
            }
            .text-dark {
                color: #ffffff !important;
            }
            .card-header {
                color: #ffffff !important;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="text-center mb-4 text-light">Ranking de Pronósticos</h1>
            
            <!-- Gráfico de Ranking -->
            <div class="card mb-4">
                <div class="card-header bg-primary text-white">
                    <h2 class="h5 mb-0">Gráfico de Puntuaciones</h2>
                </div>
                <div class="card-body">
                    <div class="chart-container">
                        <canvas id="rankingChart"></canvas>
                    </div>
                </div>
            </div>
            
            <!-- Tabla de Apuestas -->
            <div class="card mb-4">
                <div class="card-header bg-warning text-dark">
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
                            <tbody>
    """
    
    # Add betting table rows
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
            
            <!-- Tabla de resultados -->
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
                                <th></th>
                            </tr>
                        </thead>
                        <tbody>
    """
    
    resultados_guardados = obtener_resultados_guardados()
    for partido, datos in resultados_guardados.items():
        equipo1, equipo2 = partido.split()
        # Modificar la lógica del estado
        estado = "Jugado" if datos['jugado'] and datos['goles1'] != 'x' and datos['goles2'] != 'x' else "Pendiente"
        
        html += f"""
                            <tr>
                                <td>{equipo1} vs {equipo2}</td>
                                <td>
                                    <form action="/actualizar_resultado" method="POST" class="row g-2 align-items-center">
                                        <input type="hidden" name="equipo1" value="{equipo1}">
                                        <input type="hidden" name="equipo2" value="{equipo2}">
                                        <input type="hidden" name="jugado" value="true">
                                        <div class="col-5">
                                            <input type="number" class="form-control form-control-sm" name="goles1" 
                                                value="{datos['goles1'] if datos['goles1'] != 'x' else ''}" min="0">
                                        </div>
                                        <div class="col-2 text-center">-</div>
                                        <div class="col-5">
                                            <input type="number" class="form-control form-control-sm" name="goles2" 
                                                value="{datos['goles2'] if datos['goles2'] != 'x' else ''}" min="0">
                                        </div>
                                        <div class="col-12 text-end">
                                            <button type="submit" class="btn btn-primary btn-sm">Guardar</button>
                                        </div>
                                    </form>
                                </td>
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
                        <tbody>
    """
    
    ranking_ordenado = sorted(puntuaciones.items(), 
                            key=lambda x: (x[1]["puntos_totales"], x[1]["exactos"]), 
                            reverse=True)
    
    for pos, (jugador, stats) in enumerate(ranking_ordenado, 1):
        html += f"""
                            <tr>
                                <td>{pos}</td>
                                <td>{jugador}</td>
                                <td>{stats["puntos_totales"]}</td>
                                <td>{stats["exactos"]}</td>
                                <td>{stats["aciertos"]}</td>
                                <td>{stats["contrarios"]}</td>
                                <td>{stats["partidos_jugados"]}</td>
                            </tr>"""
    
    html += """
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    # Add Chart.js initialization before closing body tag
    html += """
            <script>
                const ctx = document.getElementById('rankingChart').getContext('2d');
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: [%s],
                        datasets: [{
                            label: 'Puntos Totales',
                            data: [%s],
                            backgroundColor: '#4a90e2',
                            borderColor: '#2171cd',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                grid: {
                                    color: '#233554'
                                },
                                ticks: {
                                    color: '#ffffff'
                                }
                            },
                            x: {
                                grid: {
                                    color: '#233554'
                                },
                                ticks: {
                                    color: '#ffffff'
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                labels: {
                                    color: '#ffffff'
                                }
                            }
                        }
                    }
                });
            </script>
        </body>
    </html>
    """ % (
        str([jugador for jugador, _ in ranking_ordenado])[1:-1],
        str([stats["puntos_totales"] for _, stats in ranking_ordenado])[1:-1]
    )
    
    return html

if __name__ == '__main__':
    app.run(debug=True)