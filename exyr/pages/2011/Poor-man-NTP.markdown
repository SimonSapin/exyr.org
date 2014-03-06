title: Poor man’s NTP
published: 2011-05-28
summary: How to synchronize a Linux computer’s clock when NTP doesn’t work.

The network where I live currently is heavily filtered. I believe that UDP
from or to the Internet is not allowed at all. As a result,
[NTP](http://en.wikipedia.org/wiki/Network_Time_Protocol) doesn’t work and
my computer’s clock does not synchronize itself. 
[My favorite “VPN”](http://github.com/apenwarr/sshuttle) does not support UDP,
and “real” VPNs that do usually use UDP themselves, so they wouldn’t help either.
It’s been about a month and my machine already has more than a minute of drift.

I do however have access to servers whose clocks *are* synchronized with NTP,
so all is not lost. First, make sure it really is up-to-date. On the server,
run:

    sudo ntpdate pool.ntp.org

Now, let’s read the server’s clock across the network with SSH and see how
much time it takes (the ``time`` command does that.)

    time ssh hako date +%F\\ %T.%N

This time is the upper bound for the error of this method. Most of it is
network latency, with several round-trips to establish the SSH connection.
I get about 270 milliseconds with password-less SSH login. This is not
super-accurate: NTP can do much better but it was designed to compensate for
network latency, while we’re not compensating at all. Yet this is still much
better than keeping a one minute drift.

On Linux the system clock is set with ``date -s``. ``+%F\\ %T.%N`` above is
the format we want for the date. The double slash is transformed into one slash
by the local shell, and that slash protects the space on the server’s shell.
The format was chosen to include sub-second precision and be standard enough
to be recognized by ``date -s``.

Once everything looks good, actually set the system clock:

    :::sh
    sudo date -s "$(ssh hako date +%F\\ %T.%N)"

On Linux the system clock is handled by the kernel and is completely separated
from the hardware clock. The hardware clock is usually read on boot and set
on shutdown. This means that the computer needs to be properly shut down for
the new time to be kept for the next boot.
