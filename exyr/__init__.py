import jinja2
from flask import Flask, render_template
from flaskext import flatpages


app = Flask(__name__)
app.jinja_env.undefined = jinja2.StrictUndefined

pages = flatpages.FlatPages(app)


@app.route('/')
def index():
    articles = (p for p in pages
                if all(m in p.meta for m in ['published', 'title']))
    latest = sorted(articles, reverse=True, key=lambda p: p.meta['published'])
    return render_template('articles.html', articles=latest)


app.add_url_rule('/<path:path>/', 'page', pages.render)

