import re
import posixpath

import markdown
import jinja2
from flask import Flask, render_template, send_from_directory, abort
from flaskext.flatpages import FlatPages, pygments_style_defs
from flaskext.static import StaticBuilder, walk_directory


app = Flask(__name__)
app.jinja_env.undefined = jinja2.StrictUndefined

# The atom.xml template uses url_for(..., _external=True)
app.config['STATIC_BUILDER_BASE_URL'] = 'http://exyr.org/'
builder = StaticBuilder(app)

pages = FlatPages(app)
app.jinja_env.globals['pages'] = pages


def my_markdown(text):
    return markdown.markdown(text, ['codehilite'] + 2 * ['downheader'])

app.config['FLATPAGES_HTML_RENDERER'] = my_markdown


def all_articles():
    return (p for p in pages if 'published' in p.meta)

def by_date(articles):
    return sorted(articles, reverse=True, key=lambda p: p['published'])


@app.route('/')
def index():
    return render_template('all_posts.html', posts=by_date(all_articles()))


@app.route('/tags/')
def tags():
    return render_template('tag_list.html', tags=sorted(set(
        tag for a in all_articles() for tag in a.meta.get('tags', [])
    )))

@app.route('/tags/<name>')
def tag(name):
    articles = by_date(
        a for a in all_articles() if name in a.meta.get('tags', [])
    )
    if not articles:
        abort(404)
    return render_template('tag.html', tag=name, posts=articles)


@app.route('/<path:path>/')
def page(path):
    return render_template('flatpage.html',
        page=pages.get_or_404(path),
        sub_pages=by_date(p for p in all_articles()
                          if p.path.startswith(path + '/')),
    )


@app.route('/feed.atom')
def feed():
    articles = by_date(all_articles())[:10]
    # with `modified`, but defaults to `published`
    articles = [(a, a.meta.get('modified', a['published'])) for a in articles]
    feed_updated = max(updated for article, updated in articles)
    xml = render_template('atom.xml', **locals())
    return app.response_class(xml, mimetype='application/atom+xml')
    

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


IMAGE_EXTENSIONS = ('.jpg', '.png')

# the repr() of a tuple matches the micro-syntax used by `any`
# http://werkzeug.pocoo.org/documentation/dev/routing.html#werkzeug.routing.AnyConverter
@app.route('/<path:path><any%r:type>' % (IMAGE_EXTENSIONS,))
def image(path, type):
    return send_from_directory(pages.root, path + type)

@builder.register_generator
def images_urls():
    for filename in walk_directory(pages.root):
        path, extension = posixpath.splitext(filename)
        if extension in IMAGE_EXTENSIONS:
            yield 'image', {'path': path, 'type': extension}

