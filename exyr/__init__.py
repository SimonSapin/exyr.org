import jinja2
from flask import Flask, render_template
from flaskext.flatpages import FlatPages, pygments_style_defs
from flaskext.static import StaticBuilder


app = Flask(__name__)
app.jinja_env.undefined = jinja2.StrictUndefined

pages = FlatPages(app)
builder = StaticBuilder(app)


@app.route('/')
def index():
    articles = (p for p in pages
                if all(m in p.meta for m in ['published', 'title']))
    latest = sorted(articles, reverse=True, key=lambda p: p.meta['published'])
    return render_template('articles.html', articles=latest)


app.add_url_rule('/<path:path>/', 'page', pages.render)


@app.route('/pygments.css')
def pygments_css():
    return pygments_style_defs(), 200, {'Content-Type': 'text/css'}


@builder.register_generator
def pages_urls():
    for page in pages:
        yield 'page', {'path': page.path}

