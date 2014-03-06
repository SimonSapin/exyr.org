title: Flask-Static is dead, long live Frozen-Flask!
published: 2011-02-21
summary: Just because the new name is so much cooler.

[Flask-Static](/2010/Flask-Static/) is nice but the name was not so great.
The “Static” part sounded like it’s about static files (those that come with
your app, such as images and CSS,) but it was really not.
(Or not really. Maybe.)

After much debate, it was decided that Flask-Static was to be renamed
**Frozen-Flask**. *Frozen-Flask freezes your Flask app into a set of static
files.* Much cooler, uh?

New links:

* [Documentation](http://packages.python.org/Frozen-Flask/)
* [PyPI page](http://pypi.python.org/pypi/Frozen-Flask)
* [Code](https://github.com/SimonSapin/Frozen-Flask)

Other candidate names were *Flask-Cryogenics* and *Flask-OnTheRocks*.

While I was at breaking API compatibility, I also changed a few objects names.
For example the main class is now called `Freezer`. See the [brand new
changelog](http://packages.python.org/Frozen-Flask/#changelog) for details.

Now the only task left is to make a logo of the flask stuck in an ice cube.

