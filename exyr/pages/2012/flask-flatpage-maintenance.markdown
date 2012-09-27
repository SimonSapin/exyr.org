title: Who wants to maintain Flask-FlatPages?
published: 2012-09-27
tags: [web-development, flask]
summary: >
    I stopped using Flask-FlatPages on this site and I most likely won’t
    work on it anymore. Anyone wants to take over and maintain the project?

I made both [Frozen-Flask](http://packages.python.org/Frozen-Flask/) and
[Flask-FlatPages](http://packages.python.org/Flask-FlatPages/) at the same
time when I built the current iteration of this website. If I were to do
it again I would make Frozen-Flask exactly the same, it is close to perfect.
But I would not make a library like Flask-FlatPages at all.

There is not much in Flask-FlatPages itself: it’s mostly glue around
YAML, Markdown and Pygments. While a library should be generic and configurable
to accommodate all kinds of use case, Flask-FlatPages is just at the level
where each application will make different choices: not quite this directory
structure, slightly different parameters for Markdown, …

As a result, Flask-FlatPages has more configuration and abstractions than
actually useful code. (Not to mention a cache with weird invalidation rules.)
My own needs on this blog are actually much more modest then everything the
library can do: one page at `/about/`; everything else at `/<year>/<name>/`
where `<year>` is a four-digit integer.

So after using and maintaining Flask-FlatPages for a while, I just don’t
like it. So I [refactored this site](https://github.com/SimonSapin/exyr.org/commit/d1cedc633c1df4d1f395441a56d01cfef8dcebd6)
to not use it anymore. I have ~50 lines of app-specific code that does
what it needs to and no more, instead of a ~200 lines lib that needs to
be tested, packaged and maintained. I am very satisfied with the result.
I did added caching (invalidated by the files’s modification time) because
it was easy, but even that is overkill.

But apparently some people do use Flask-FlatPages, and actually like it!
I don’t really want to work on it anymore, but I won’t throw it away either.
If anyone wants to take over and maintain the project, please let me know and
I will gladly give them PyPI and Github access. Otherwise I guess the project
will continue stagnating. I will be discussing this on the
[Flask mailing-list](http://flask.pocoo.org/mailinglist/).
