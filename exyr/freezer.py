import os
import mimetypes

from . import app, Page
from flask_frozen import Freezer, walk_directory


# Seems to be available only on some systems...
mimetypes.add_type('application/atom+xml', '.atom')


freezer = Freezer(app)


@freezer.register_generator
def static_in_pages():
    for year in Page.years():
        for name in os.listdir(os.path.join(Page.root, year)):
            directory = os.path.join(Page.root, year, name)
            if os.path.isdir(directory):
                for path in walk_directory(directory):
                    yield {'year': int(year), 'name': name, 'path': path}
