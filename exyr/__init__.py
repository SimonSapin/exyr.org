import os
import io
import re
import datetime
import itertools

import markdown as markdown_module
import pygments.formatters
import yaml
import jinja2
import werkzeug
from flask import Flask, render_template, send_from_directory, abort, url_for


app = Flask(__name__)
app.jinja_env.undefined = jinja2.StrictUndefined
app.jinja_env.globals['today'] = datetime.date.today

# The atom.xml template uses url_for(..., _external=True)
app.config['FREEZER_BASE_URL'] = 'http://exyr.org/'

PYGMENTS_CSS = (pygments.formatters.HtmlFormatter(style='tango')
                .get_style_defs('.codehilite'))


@app.template_filter()
def markdown(text):
    return markdown_module.markdown(
        text,
        ['codehilite', 'footnotes'] + 2 * ['downheader'],
        extension_configs={'codehilite': {'linenums': False}},
    )


class Page(object):
    root = os.path.join(app.root_path, u'pages')
    suffix = '.markdown'
    _cache = {}

    @classmethod
    def load(cls, year, name):
        filename = os.path.join(cls.root, year, name) + cls.suffix
        if not os.path.isfile(filename):
            abort(404)
        mtime = os.path.getmtime(filename)
        page, old_mtime = cls._cache.get(filename, (None, None))
        if not page or mtime != old_mtime:
            with io.open(filename, encoding='utf8') as fd:
                head = ''.join(itertools.takewhile(lambda x: x.strip(), fd))
                body = fd.read()
            page = cls(year, name, head, body)
            cls._cache[filename] = (page, mtime)
        return page

    @classmethod
    def years(cls):
        for year in os.listdir(cls.root):
            if year.isdigit():
                yield year

    @classmethod
    def articles_by_year(cls, year):
        directory = os.path.join(cls.root, year)
        if not os.path.isdir(directory):
            abort(404)
        for name in os.listdir(directory):
            if name.endswith(cls.suffix):
                page = cls.load(year, name[:-len(cls.suffix)])
                if app.config.get('EXYR_SHOW_DRAFTS') or not page.meta.get('draft'):
                    yield page

    @classmethod
    def all_articles(cls):
        for year in cls.years():
            for article in cls.articles_by_year(year):
                yield article

    def __init__(self, year, name, head, body):
        self.year = year
        self.name = name
        self.head = head
        self.body = body

    @werkzeug.cached_property
    def meta(self):
        return yaml.safe_load(self.head) or {}

    def __getitem__(self, name):
        return self.meta[name]

    @werkzeug.cached_property
    def html(self):
        return markdown(self.body)

    def url(self, **kwargs):
        return url_for(
            'article', year=int(self.year), name=self.name, **kwargs)

    def updated(self):
        return self.meta.get('modified', self['published'])


@app.route('/.htaccess')
def htaccess():
    return '''
        RedirectMatch /tags(/.*)?   /
        RedirectMatch /(\d+)/?$     /#$1
        RedirectMatch /2013/enumerated-types-python/slides.pdf /2013/algebraic-sum-types-python/slides.pdf
        RedirectMatch /2011/Poor-man-NTP/ /2011/low-tech-ntp/
        RedirectMatch /about/ /
    ''', 200, {'Content-Type': 'application/octet-stream'}


@app.route('/')
def home():
    return render_template(
        'all_posts.html',
        posts_by_year=itertools.groupby(
            sorted(
                Page.all_articles(),
                reverse=True,
                key=lambda p: p['published'],
            ),
            key=lambda p: p['published'].year,
        ),
        about=Page.load('', 'about')
    )


@app.route('/<int:year>/<name>/')
def article(year, name):
    return render_template('flatpage.html', page=Page.load(str(year), name))


@app.route('/<int:year>/<name>/<path:path>')
def static_in_pages(year, name, path):
    return send_from_directory(Page.root, '%i/%s/%s' % (year, name, path))


@app.route('/feed.atom')
def feed():
    articles = sorted(Page.all_articles(), key=lambda a: a.updated())
    feed_updated = articles[0].updated()
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
    css = render_template('style.css', pygments_css=PYGMENTS_CSS)
    css = minify_css(css)
    # Add this after minification, would be removed otherwise.
    css = (
        '/*\nNon-minified version is at\n'
        'https://github.com/SimonSapin/exyr.org'
        '/blob/master/exyr/templates/style.css\n*/\n'
        + css
    )
    return app.response_class(css, mimetype='text/css')


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')
