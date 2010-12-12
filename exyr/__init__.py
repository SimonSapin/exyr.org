from flask import Flask


app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello from exyr.org'


def run():
    app.run(debug=True)

