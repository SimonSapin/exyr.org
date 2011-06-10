title: Frozen-Flask 0.3 and how to add package data in setup.py
public: false
published: 2011-05-29
tags: [web-development, flask]
summary: New release, and a tip for making packages with data files.

I just released Frozen-Flask 0.3. The main change is that URL generators can
now omit the endpoint. [See the documentation](
http://packages.python.org/Frozen-Flask/) for details.

Also, the tests now get installed alongside the code. I lost a lot of time
getting ``setup.py`` and ``MANIFEST.in`` right so that static files for the
test app would get installed too. Without that every test would just fail.


Including data files in packages
================================

Let’s say that you have a Python package that also contains non-Python files
− typically templates or static files for a Flask app − and that you want
to put it on [PyPI](http://pypi.python.org/pypi)
