import os
from weasyprint import HTML
from flask_frozen import Freezer
from flask_weasyprint.test_app import app

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

app.config['FREEZER_DESTINATION'] = os.path.join(ROOT, 'frozen_demo')
app.config['FREEZER_RELATIVE_URLS'] = True
Freezer(app).freeze()

HTML('http://www.pycon.fr/2012/schedule/').write_pdf(
    'PyConFR_2012_schedule.pdf', stylesheets=['print.css'])
