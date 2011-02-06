from werkzeug import cached_property
from flaskext.flatpages import FlatPages


class PublicPages(FlatPages):
    """
    In debug mode, prefix the title of pages that do not have a true-ish 
    `public` metadata with 'DRAFT: '. Otherwise hide these pages.
    """
    
    @cached_property
    def _pages(self):
        # cached_property(f).func is f
        pages = FlatPages._pages.func(self)
        if self.app.debug:
            return pages
        else:
            return dict((path, p) for path, p in pages.iteritems() if p.public)

    def _parse(self, *args, **kwargs):
        page = super(PublicPages, self)._parse(*args, **kwargs)
        page.public = page.meta.get('public', False)
        if not page.public:
            # Pages are required to have a title
            page.meta['title'] = 'DRAFT: ' + page.meta['title']
        return page

