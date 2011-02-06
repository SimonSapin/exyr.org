import posixpath

from . import app, pages, IMAGE_EXTENSIONS, all_articles
from flaskext.static import StaticBuilder, walk_directory


builder = StaticBuilder(app)


@builder.register_generator
def tags():
    for article in all_articles():
        for tag in article.meta.get('tags', []):
            yield 'tag', {'name': tag}


@builder.register_generator
def page_urls():
    for page in pages:
        yield 'page', {'path': page.path}


@builder.register_generator
def archives():
    for page in pages:
        if '/' in page.path:
            first = page.path.split('/', 1)[0]
            try:
                year = int(first)
            except ValueError:
                pass
            else:
                yield 'archives', {'year': year}


@builder.register_generator
def images():
    for filename in walk_directory(pages.root):
        path, extension = posixpath.splitext(filename)
        if extension in IMAGE_EXTENSIONS:
            yield 'image', {'path': path, 'type': extension}


