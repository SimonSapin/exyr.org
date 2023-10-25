#!/usr/bin/env python
import os.path
from base64 import b64encode

import weasyprint
import lxml.html
from lxml.etree import Element, tostring


def render(html_filename, pdf_filename):
    tree = lxml.html.parse(html_filename)
    for svg in tree.xpath('//svg'):
        xml = tostring(svg).replace(b'viewbox=', b'viewBox=')
        svg.getparent().replace(svg, Element(
            'img', {'src': 'data:image/svg+xml;base64,' +
                           b64encode(xml).decode('ascii')}))
    weasyprint.HTML(tree=tree, base_url=html_filename).write_pdf(pdf_filename)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    render('slides.html', 'slides.pdf')
