import posixpath
import mimetypes

from . import app, pages, STATIC_EXTENSIONS, all_articles
from flaskext.frozen import Freezer, walk_directory


# Seems to be available only on some systems...
mimetypes.add_type('application/atom+xml', '.atom')


freezer = Freezer(app)


@freezer.register_generator
def tag():
    for article in all_articles():
        for tag in article.meta.get('tags', []):
            yield {'name': tag}


@freezer.register_generator
def page():
    for page in pages:
        yield {'path': page.path}


@freezer.register_generator
def archives():
    for page in pages:
        if '/' in page.path:
            first = page.path.split('/')[0]
            if first.isdigit():
                yield {'year': first}


@freezer.register_generator
def static_in_pages():
    for filename in walk_directory(pages.root):
        path, extension = posixpath.splitext(filename)
        if extension in STATIC_EXTENSIONS:
            yield {'path': path, 'type': extension}


