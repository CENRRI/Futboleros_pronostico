from flask_frozen import Freezer
from app import app

app.config['FREEZER_DESTINATION'] = 'build'
freezer = Freezer(app)

if __name__ == '__main__':
    freezer.freeze()