title: Run a script on file changes with inotify
published: 2011-10-13
tags: [inotify, snippets]
summary:
    Have a script (eg. your test suite) run automatically every time a file
    changes.

The workflow for writing software typically goes like this:

* Make some changes in the source code
* Run the program, typically a test suite
* Watch the output
* Rinse and repeat

For me the second step means hitting *ALT-Tab* to switch from my text editor
to a terminal window, then the *up* arrow and *Enter* to re-run the last
command. After that, *ALT-Tab* again to go back to the text editor.

This is way too much repetitive work. It can, and thus should be automated.
What we want is a script that will watch source files, and run another script
when they change. We could poll the modification time of each file, but
that is a bit inefficient.

On Linux, [inotify](http://en.wikipedia.org/wiki/Inotify) can have the kernel,
well, notify you whenever a file changes. There are a
[number](https://github.com/peterbe/python-gorun)
[of](http://pypi.python.org/pypi/PyZen/)
[projects](https://github.com/mynyml/watchr) doing fancy things with inotify,
but it can be much more simple.

I have the following in an `inotifyrun` script:

    :::sh
    #!/bin/sh
    FORMAT=$(echo -e "\033[1;33m%w%f\033[0m written")
    "$@"
    while inotifywait -qre close_write --format "$FORMAT" .
    do
        "$@"
    done

When I run it with `inotifyrun attest` the script first runs my test suite
once with [Attest](http://packages.python.org/Attest/), then block until
a file is written in the current directory or a sub-directory. When that
happens, it runs the test suite again and repeats the loop.
I used Attest as an example but it can be any command, optionally
with arguments.

Your kernel probably has inotify already, but you may need to install a
`inotify-tools` package to get the command-line tools.

Web development
---------------

When building stuff for the web, you often test in a web browser rather than
in a terminal. Refresh a web page instead of running a script.

So, how can this script help? We need to instruct the browser to refresh
a page. As usual, Unix has a tool for that. `xdotool` does X11 magic to
simulate mouse and keyboard actions. It can also search among open windows.
Let’s combine these with inotify:

    inotifyrun xdotool search --name 'Chromium' key F5

Ta-da! Your browser reloads the current page as soon as you hit *Save* in your
text editor. Unfortunately though, Firefox doesn’t seem to respond to xdotool.

**Update 2012-07-19**: one day the command above just stopped working for me.
It turns out it only sends F5 to the *first* window that matches the search.
Sometimes that happens to be one the reloads on F5, sometimes not.
The new command below fixes this: `--window %@` sends the key to all matching
windows.

    xdotool search --name Chromium key --window %@ F5


How it works
------------

`inotifywait` watch all files in `.`, the current directory, recursively with
the `-r` option. `-q` suppresses a warning saying that the setup may be long
if you have many files, but that’s not a problem in practice.
The `echo -e` trick is required to have the color codes interpreted.
`%w%f` in the format string is replaced by the filename that was just
written to.

inotify can tell us about many events (any kind of operation on files)
but with `-e close_write` we say we’re only interested by files being closed
after they were written to. This is better than any `write` event because
it means you editor has finished writing the file.

Please [let me know](/about/) if you think this can be improved!
