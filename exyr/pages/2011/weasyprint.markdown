title: WeasyPrint renders HTML+CSS to PDF
published: 2011-11-02
tags: [kozea, weasyprint]
summary:
    The project I’ve been working on in the past few months has finally
    reached an usable state and has gotten a public release!
    See [weasyprint.org](http://weasyprint.org/)


[WeasyPrint](http://weasyprint.org/) just got its first release!
It is a rendering engine for HTML and CSS that produces PDF.
I’ve been with [Kozea](http://community.kozea.org/) working on it for
a few months now.

While it uses many libraries to parse HTML and CSS, draw text or export PDF,
it is **not** based on an existing rendering engine such as WebKit or Gecko.
The layout logic is written in Python, is much simpler and thus easier to
hack on. In particular, creating WeasyPrint was probably easier than
[fixing page breaks in Webkit](
http://www.webkit.org/projects/printing/index.html).

This 0.1 release has support for basic CSS2.1 without tables, floats or
absolute positioning. However it can already be useful for documents with
a “simple” layout.

Grab it, use it, hack it:

* [Website](http://weasyprint.org/): documentation and everything else
* Sample output: [PDF](http://weasyprint.org/samples/CSS21-intro.pdf),
  [HTML source](http://www.w3.org/TR/CSS21/intro.html)
* [Code](https://github.com/Kozea/WeasyPrint) on GitHub
