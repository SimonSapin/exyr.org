import re

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



def minify_css(css):
    # Remove comments. *? is the non-greedy version of *
    css = re.sub(r'/\*.*?\*/', '', css)
    # Remove redundant whitespace
    css = re.sub(r'\s+', ' ', css)
    # Put back line breaks after block so that it's not just one huge line
    css = re.sub(r'} ?', '}\n', css)
    return css

@app.route('/style.css')
def stylesheet():
    css = render_template('style.css', pygments_style_defs=pygments_style_defs)
    return app.response_class(minify_css(css), mimetype='text/css')


@builder.register_generator
def pages_urls():
    for page in pages:
        yield 'page', {'path': page.path}

