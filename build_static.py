import os
from app import app, obtener_resultados_guardados
from flask_frozen import Freezer

# Configurar Freezer
app.config['FREEZER_DESTINATION'] = 'static'
freezer = Freezer(app)

if __name__ == '__main__':
    # Asegurar que el directorio static existe
    if not os.path.exists('static'):
        os.makedirs('static')
    
    # Generar sitio estático
    freezer.freeze()