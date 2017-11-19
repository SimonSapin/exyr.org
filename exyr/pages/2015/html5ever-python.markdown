title: "Put some Rust in your Python"
published: 2015-09-26
draft: true
summary: |
    [CFFI](http://cffi.readthedocs.org/) can call into C libraries from Python,
    and [Rust](https://www.rust-lang.org/) libraries can expose a C-compatible API.
    Let’s put the two together, but let’s go a bit further than the integer Hello World.
    Dealing with strings, callbacks, panics/exceptions, and packaging requires some more thought.


# Python is slow!

… is a common criticism.
(At this point the PyPy developers will make sure to tell you
that you mean the CPython implementation,
[not necessarily](http://speed.pypy.org/) the Python language.)
The traditional response is that it doesn’t matter,
and when it does we can [rewrite the few critical bits in C](
https://docs.python.org/3/whatsnew/3.5.html#whatsnew-ordereddict).

Except nobody[^1] actually does it!
Many people chose Python in the first place because they don’t want to write C.
And with reason, writing correct C is notoriously difficult.
There are a bunch of rules to follow to avoid triggering *undefined behavior*.
Slip up once, and your program can have [a security vulnerability](
http://arstechnica.com/security/2015/08/how-security-flaws-work-the-buffer-overflow/)
without any complier warning.
This can be [very bad](http://heartbleed.com/).

[^1]: Alright, some brave people *do* write Python modules in C for everyone else to use, but they’re very few.


# Rust

[Rust](https://doc.rust-lang.org/book/README.html) is a systems programming language
focused on three goals: safety, speed, and concurrency.
It can be used in places that require the speed of C/C++,
but has much less undefined behavior and the pesky memory safety issues that come with it.

Rust [can be used from other languages](
http://blog.rust-lang.org/2015/04/24/Rust-Once-Run-Everywhere.html),
including [from Python](
https://github.com/alexcrichton/rust-ffi-examples/tree/master/python-to-rust).
Let’s see how that works in practice, beyond simple integers!


# HTML parsing

The Python world has many libraries for parsing HTML,
but in my opinion only two are relevant:
[html5lib](http://html5lib.readthedocs.org/en/latest/) is correct[^2],
and [lxml.html](http://lxml.de/) is [fast](
https://web.archive.org/web/20131125062252/http://www.ianbicking.org/blog/2008/03/python-html-parser-performance.html) (thanks to being written in C).

[^2]:
    An oversimplified history of web standards is that in the early years,
    standards defined “this is how things are”.
    But what if they’re not?
    What should browsers do with a website that sends horribly broken markup
    that barely looks like HTML?
    The standard did not say, and since [the Yellow Screen Of Death](
    https://commons.wikimedia.org/wiki/File:Yellow_screen_of_death.png)
    is a terrible user experience,
    they try to recover and interpret the content somehow.
    Of course they all did it slightly differently.
    The world was full of reverse-engineering and interoprability issues.

    When the [2004-era HTML standard](
    https://html.spec.whatwg.org/multipage/)
    (sometimes known as “HTML 5”)
    came along,
    it pioneered modern specifications that say “this is what you do”,
    in details,
    including in error cases.
    Nowadays, every modern browser implements HTML parsing per this specification
    and interoperability is much better.

    libxml2, used by lxml.html, pre-dates this new standard
    and uses its own algorithm for error recovery
    which sometimes differs the now-standard one.
    html5lib on the other hand implements that standard directly.

Why not have both?
[html5ever](https://github.com/servo/html5ever)
was developed for [Servo](https://github.com/servo/servo/).
It should be fast as it’s written in Rust,
and it demonstrates correctness by running the [html5lib test suite](
https://github.com/html5lib/html5lib-tests/).

I wrote [Python bindings for html5ever](https://github.com/SimonSapin/html5ever-python).
Here is how they work.


# Minimal FFI example

The Rust-from-Python example mentioned above
uses [ctypes](https://docs.python.org/3/library/ctypes.html),
but declaring the type of function parameters and return values in ctypes is a bit of a pain.
I much prefer using [CFFI](http://cffi.readthedocs.org/),
which takes declarations in C syntax.


# C as a common denominator

Rust and Python do not know how to talk to each other,
but like most programming languages they both know how to talk to C.
C is the [*lingua franca*](https://en.wikipedia.org/wiki/Lingua_franca)
of programming languages.

Even though no C compiler will be used,
we’ll have to do all our cross-language communication with C-compatible APIs.

TODO: traits, callbacks, strings, exceptions/panics


# Packaging

TODO: wheels
