# -*- coding: utf-8 -*-
"""
A python markdown extension for reducing header level, h1 becomes h2, etc...

Load it twice for reducing it twice, load it more for more.

Author: Knx.corp
Source: http://code.google.com/p/markdown-downheader/
"""
import markdown
import re

def makeExtension(configs=None) :
    return DownHeaderExtension(configs=configs)
    
class DownHeaderExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        if 'downheader' in md.treeprocessors.keys():
            md.treeprocessors['downheader'].offset += 1
        else:
            md.treeprocessors.add('downheader', DownHeaderProcessor(), '_end')

class DownHeaderProcessor(markdown.treeprocessors.Treeprocessor):
    def __init__(self, offset=1):
        markdown.treeprocessors.Treeprocessor.__init__(self)
        self.offset = offset
    def run(self, node):
        expr = re.compile('h(\d)')
        for child in node.getiterator():
            match = expr.match(child.tag)
            if match:
                child.tag = 'h' + str(min(6, int(match.group(1))+self.offset))
        return node

