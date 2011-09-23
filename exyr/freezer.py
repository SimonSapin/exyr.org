import os
import posixpath
import mimetypes

from . import app, pages, STATIC_EXTENSIONS, all_articles
from flaskext.frozen import Freezer, walk_directory


# Seems to be available only on some systems...
mimetypes.add_type('application/atom+xml', '.atom')


freezer = Freezer(app)


@freezer.register_generator
def archives():
    for name in os.listdir(pages.root):
        if name.isdigit():
            yield {'year': name}


@freezer.register_generator
def static_in_pages():
    for filename in walk_directory(pages.root):
        path, extension = posixpath.splitext(filename)
        if extension in STATIC_EXTENSIONS:
            yield {'path': path, 'type': extension}
