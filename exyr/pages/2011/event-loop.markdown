title: Single-threaded event loop for file input and timers
published: 2011-02-27
summary: |
    To wait for various events and without polling, a blocking threads for each
    event is the obvious solution. However, multi-threading comes with its
    pitfalls and problems.
    Here we are going to see how to build and event loop the handle multiple
    event in the same thread.

If an application needs to wait for various events and polling is not
possible or desirable, a popular solution is to use a blocking thread for each
events. However, multi-threading is easy to get wrong and often hard to debug.

This event loop is a framework that allows an application to wait for
various events without using threads. Currently supported events are
files being ready for reading and timers (repeating or not).

As usual, [grab the code](
https://github.com/SimonSapin/snippets/tree/master/event_loop) over there.
Here is an example of how this could be used. The “line reader” wraps the
“file ready” event and gives you lines as they come from the file, as would
`some_file.readline()`.

    :::python
    loop = EventLoop()
    
    @loop.add_timer(5)
    def timeout():
        print 'No new line in 5 seconds. Stopping now.'
        loop.stop()
    
    @loop.line_reader(sys.stdin)
    def new_line(line):
        timeout.reset() # Start again: count 5 seconds from now.
        print 'Echo:', line.strip()
        
    print 'Echoing lines.'
    loop.run()
    print 'Exit.'
    
The heart of the loop is not much more than a
[`select()`](http://docs.python.org/library/select.html#select.select) call
with a well-chosen timeout.

Be careful not to block for too long in a callback. Since we’re not using
threads or any form of concurrency, other events won’t
be handled as long as a callback has not returned. These events won’t be missed,
though; just delayed. (Except for repeating timers which may miss a few beats.)

State of the art
----------------

Of course this is not new. To Unix gurus out there, `select()` is as obvious as
fresh air and file descriptors. I just happen to have learned about it recently.
Indeed, if you’re just waiting on two files without timers (or with a contsant
timeout), plain `select()` is much simpler and thus better. There are also a
few systems such as [asynchat](http://docs.python.org/library/asynchat.html)
or the [Twisted framework](http://www.twistedmatrix.com/)
built on this kind of techniques, but they often are much more network-oriented
than what I need for this project.

Context
-------

This is meant for my research project at the [University of
Tokyo](http://lelab.t.u-tokyo.ac.jp/). The application reads and writes packets
to a serial port and these packets are transmitted over wireless.
    
Incoming packets arrive with varying timing, so polling is not appropriate.
There may be packet loss, so we need timeouts when waiting for something.
Also this part of the application gets its own instructions on its
standard input.

A packet reader is registered as a callback to the event loop and takes care of
reading and parsing whole packets. The reader has it’s own callback which is
called with each packet when they become available.
The code is similar to that of the line
reader, and is included in a [separate file](
https://github.com/SimonSapin/snippets/blob/master/event_loop/packet_reader.py).

Like many (if not all?) communication protocols, this kind of packet decoding
can be modeled as a [state machine](http://en.wikipedia.org/wiki/State_machine).
In the simplest programs to do such decoding with blocking reads, the state
in implicitly represented by the point in the code currently being executed.
If however blocking is not allowed, we may have to stop in the middle of a
packet to wait for more data, and later continue from where we left of.
This means that we have to explicitly save the current state somewhere.
The way of thinking to build such systems is a bit different from the
straightforward implementation. It’s not too difficult, but requires some
adaptation.

Other events
------------

`select()` can also wait for a file descriptor to be ready for writing.
Support for this wouldn’t be too hard to add to the event loop but as they say,
[You ain’t gonna need it](http://en.wikipedia.org/wiki/YAGNI).
Writing to a serial port may block and take some time, but it’s much faster
and more predictable than waiting for the next wireless packet. (Which could
even be lost!) Also, I’m only sending short commands to my sensors. The
high-throughput data goes the other way.

Thanks to the *Everything is a file* philosophy of Unix, many things such as
pipes and sockets have a file descriptor and thus can be used with `select()`.
However, supporting completely different events (unrelated to file descriptors
or time) in the same event loop is likely to be more difficult.

