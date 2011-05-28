import posixpath

from . import app, pages, IMAGE_EXTENSIONS, all_articles
from flaskext.frozen import Freezer, walk_directory


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
def image():
    for filename in walk_directory(pages.root):
        path, extension = posixpath.splitext(filename)
        if extension in IMAGE_EXTENSIONS:
            yield {'path': path, 'type': extension}


