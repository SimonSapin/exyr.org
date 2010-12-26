import re

import markdown
import jinja2
from flask import Flask, render_template
from flaskext.flatpages import FlatPages, pygments_style_defs
from flaskext.static import StaticBuilder


app = Flask(__name__)
app.jinja_env.undefined = jinja2.StrictUndefined

builder = StaticBuilder(app)
pages = FlatPages(app)
app.jinja_env.globals['pages'] = pages


def my_markdown(text):
    return markdown.markdown(text, ['codehilite'] + 2 * ['downheader'])

app.config['FLATPAGES_HTML_RENDERER'] = my_markdown


def all_articles():
    return (p for p in pages if 'published' in p.meta)

def by_date(articles):
    return sorted(articles, reverse=True, key=lambda p: p.meta['published'])


@app.route('/')
def index():
    latest = by_date(all_articles())
    return render_template('article_list.html', articles=latest)


@app.route('/<path:path>/')
def page(path):
    page = pages.get_or_404(path)
    sub_pages = by_date(p for p in all_articles()
                        if p.path.startswith(path + '/'))
    return render_template('flatpage.html', page=page, articles=sub_pages)



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

