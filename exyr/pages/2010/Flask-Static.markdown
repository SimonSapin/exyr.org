title: "Flask-Static: yet another static website generator"
published: 2010-12-28
modified: 2011-02-21
summary: >
    I’ve been working on re-launching my personal website (you’re looking
    at the result), and wrote a static website generator in the process.
    It’s made of two Flask extension: *Flask-FlatPages* gives easy access to
    content with metadata stored in text files, and *Flask-Static* takes a
    snapshot of a Flask application as static files.

**Update 2011-02-21:** Flask-Static has been renamed *Frozen-Flask*.

# Why static?

The modern way of doing web development is to write an application
in a high-level language with a pre-built framework. This application handle
HTTP requests by querying special-purpose database,
rendering HTML templates, and doing all kinds of fancy stuff on the way.
This scales very well as your application becomes more complex, but requires
special software on the server. That software needs to be maintained, patched
for security fixes, and it consumes resources. On my server, a Python process
with Django eats about 20 MB of memory all the time, though I get
ridiculously little traffic: restarting it all for each request is not practical.
Also, software and libraries available on your server may be limited to older
versions.

On the other hand, if instead of a dynamic application you make a website
with no user-interaction, you can have a set of static files
sent as-is by the server. This means that you don’t need any special software
on the server, only a web server on the kind that has existed as long as the
web. This solution is fast (no database or complex rendering), secure
(no site-specific security vulnerability since no site-specific code is running
on the server) and universally available.

Working on text files instead of a web administration interface also has 
it’s advantages: you can work offline, and you can
use the same version control and diff tools you use for source code.

There are a lot of systems out there that allow you
to generate said set of static files while keeping your sanity (by eg. using
templates to avoid repeating HTML that is the same in most pages, using a
micro markup language for content, …)

In the process of rewriting (again) this website, I also wrote my own static
website generator. It comes as two extensions for the
[Flask](http://flask.pocoo.org/) micro-framework:
**Flask-Static** and **Flask-FlatPages**.

**Update 2011-02-21:** Flask-Static has been renamed *Frozen-Flask*.

# Why Flask-Static?

So, why not pick one of these existing systems? I have to admit there is a bit
of NIH here, but there are other reasons:

These systems are frameworks with their own conventions and assumptions.
They may decide that one text file equals one page, or invent new concepts to
give back a bit of flexibility. ([Hyde](http://ringce.com/hyde) has
“media processors” that allow eg. to minify CSS.)

Early static website generators required you to re-run the build to view 
every little change in you web browser. They tried to be faster by not
rebuilding what hadn’t changed, but that requires a dependency system.
Declaring dependencies explicitly is bothersome and error-prone, while
inferring them automatically is not easy. More recent systems have a built-in
HTTP server for development and only build what is required for a given
request. Sounds familiar? Yup, that’s exactly how dynamic web applications
work.

Since a built-in server is the way to go for development, let’s build our
website like a dynamic application, using an existing framework (Flask)
with its concepts and conventions.


# Flask-FlatPages

* [Documentation](http://packages.python.org/Flask-FlatPages/)
* [Code](https://github.com/SimonSapin/Flask-FlatPages)

Flask-FlatPages gives easy access to a set of pages stored in a text files
from a Flask application.
Each file is a page made of meta-data and content separated by a blank line.
I started by parsing `key: value` pairs myself but noticed this is valid
[YAML](http://www.yaml.org/). So meta-data is YAML which gives us niceties
such as list and date parsing for free. The default content format is
[Markdown](http://daringfireball.net/projects/markdown/) with
[code highlighting](http://www.freewisdom.org/projects/python-markdown/CodeHilite)
using [Pygments](http://pygments.org/), but can be configured to something
else.


# <del>Flask-Static</del> <ins>Frozen-Flask</ins>

* [Documentation](http://packages.python.org/Frozen-Flask/)
* [Code](https://github.com/SimonSapin/Frozen-Flask)

Flask-Static builds a static snapshot of a Flask application.
It takes a list of URLs, simulates requests to the application, and save the
responses in files. URLs with a trailing slash are interpreted as directories
and the content is saved in `index.html`.

It can guess URLs for static files and views that take no parameter, but
you need to provide “URL generators” for everything else: functions that yield
either URLs or view names with associated parameters.


# Examples

See the respective documentation for more details. But as an
example is said to be worth a thousand word, so you can see the source code
for two website using this: [exyr.org](https://github.com/SimonSapin/exyr.org)
and [simonsapin.info](https://github.com/SimonSapin/simonsapin.info).

