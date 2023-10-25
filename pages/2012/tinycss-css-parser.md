title: "tinycss: a new CSS parser for Python"
published: 2012-04-05
summary: |
    I made [tinycss](http://packages.python.org/tinycss/), a new free software
    CSS parser for Python. It is extensible, well-documented, well-tested
    and fast. It replaces cssutils in both WeasyPrint and CairoSVG.


I’m happy to announce the first release of tinycss!
I captured it best in the README, so here it is:

> *tinycss* is a complete yet simple CSS parser for Python. It supports the
> full syntax and error handling for CSS 2.1 as well as some CSS 3 modules:
>
> * Selectors 3 (can also find matching elements in a [lxml](http://lxml.de/)
>   document)
> * CSS Color 3
> * CSS Paged Media 3
>
> It is designed to be easy to extend for new CSS modules and syntax.
>
> Quick facts:
>
> * Free software: BSD licensed
> * Compatible with Python 2.6+ and 3.x
> * Latest documentation [on python.org](http://packages.python.org/tinycss/)
> * Source, issues and pull requests
>   [on Github](https://github.com/SimonSapin/tinycss/)
> * Releases [on PyPI](http://pypi.python.org/pypi/tinycss)
> * Install with `pip install tinycss`


It now replaces [cssutils](http://packages.python.org/cssutils/) in both
[WeasyPrint](http://weasyprint.org/) and [CairoSVG](http://cairosvg.org/).
Sorry, Christof!

cssutils has served us very well. It allowed me to skip entire chapters
of the CSS specifications when I started WeasyPrint a year ago, and get
started quickly. The source is quite readable and well documented.
cssutils is overall a very nice project.

However, patching cssutils to add support for the CSS 3 `@page` syntax
turned out to be more painful than − I think − it should have been.
The parser is somehow interleaved with the various data structures.
cssutils also has some hard-to-fix performance issues.
(Accessing a selector goes through the whole stylesheet every time to
look for `@namespace` rules.)

So, as thankful as I am to [Christof Höke](http://cthedot.de/) for his
work cssutils and for his support and collaboration with me, it was time
for something simpler.

I started working on tinycss with a very clear idea of what I wanted:
keep the implementation straightforward, and make it easy to extend for
new syntax. After a few days of hacking I had a mostly working prototype that
was already quite fast. I ended up adding optional
[Cython](http://cython.org/) accelerators. The process of profiling
and optimizing for speed was very interesting, but it is a whole other story.

This [micro-benchmark](
https://github.com/SimonSapin/tinycss/blob/master/tinycss/tests/speed.py)
(parsing and traversing a small stylesheet 20 times on my laptop)
probably does not mean much, but the results certainly look nice:

    $ python -m tinycss.tests.speed
    tinycss + speedups        119 ms
    tinycss WITHOUT speedups  174 ms  1.46x
    cssutils                  928 ms  7.80x

As for extending, adding syntax is a matter of writing a subclass of
`CSS21Parser` and overriding some methods. In fact, CSS 3 modules in
tinycss are implemented precisely this way. Doing so ensure that extending
is viable, and that the required hooks are included.

I then spent a lot more time getting the details right, polishing the API,
writing documentation, and updating WeasyPrint to use this new parser.
I’ve now got to a point where I am very satisfied with the project.
From this 0.1 version, I will try not to change the user API without a
good reason. (Although such reasons will probably come up sooner or later :)

For future versions I plan on adding parser support for
[Media Queries](http://www.w3.org/TR/css3-mediaqueries/) and
[CSS Namespaces](http://www.w3.org/TR/css3-namespace/), as well as maybe
adding the selectors that are missing in
[lxml.cssselect](http://lxml.de/cssselect.html).

I hope you’ll like cssutils too. Keep me posted if you do anything interesting
with it (or any of my projects!)
Have a look at the [tinycss documentation](
http://packages.python.org/tinycss/) and go from there.
