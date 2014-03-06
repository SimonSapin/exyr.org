title: Programatically open multiple GNOME Terminal tabs
published: 2011-02-20
summary: |
    To run several tasks in parallel and keep their output separated, run each
    one in its own shell. Doing so can be automated, and thus it should.
    Here is how to open a GNOME Terminal window with multiple tabs from a script.

Once in a while, [apticron](http://www.debian-administration.org/articles/491)
tells me that I should do package upgrades on my server. Easy enough:
ssh into the server and run `sudo aptitude update && sudo aptitude safe-upgrade`.
That’s a bit too much typing, so I have an alias in the server’s `.bashrc`:

    :::sh
    alias apt-upgrade="sudo aptitude update && sudo aptitude safe-upgrade"

And bash-completion does its magic with just `apt-u<TAB>`.
Everything is well and good.

But now I have two Debian servers. When one has updates available, the other
server probably has the same. Things can be parallelized by starting with the
second server in a new shell while the first is still running. It’s not
too bad, but this still is a sequence of actions that are always the same
and repeated regularly. This means that it can, and should be automated.

Without any more suspense, the incantation to open from a script a new
GNOME Terminal window with multiple tab and some script being run in each tab
is:

    :::sh
    gnome-terminal --tab -e command1 --tab -e command2 [...]

A few things to note here:

 * Each tab is gonna close as soon as the command is done. If you want to be
   able to see the output, add a dummy `read` at the end of your script
   (assuming bash) so that is waits for keyboard input before ending.
   (If you don’t care about the output, don’t bother with terminal tabs and run
   your task in the background.)
 * Each command is a single argument for `gnome-terminal`. If your command
   takes its own arguments, quote the whole thing. Eg. `-e "sudo foo"`
 * Commands are executed as-is, **not** interpreted by a shell. Anything like
   `-e "foo && read"` will not work. You can however call a shell explicitly:
   `-e "bash -c 'foo && read'"`

SSH has a few subtleties too:

    :::sh
    ssh -t "sudo aptitude update && sudo aptitude safe-upgrade"

The `.bashrc` file is not sourced in non-interactive mode, that is when a
command is given, so we can not use the alias. That’s okay since this line
is gonna be in a script anyway. The quotes are there so that the `&&` part
is interpreted by the server and not locally. Finally, `-t` asks for a
pseudo-tty to be allocated as in interactive mode. Without it, sudo only
gets a “dumb” pipe for standard input and output and can not prevent the
password from being echoed on the terminal.

Putting all this together is straightforward but one needs to be careful with
quote escaping. However I want to be prepared for the day I have 3 or 30
servers, and things should be
[DRY](http://en.wikipedia.org/wiki/Don%27t_repeat_yourself) anyway.
Sticking with bash is doable, (think piping a `for` loop into `xargs`)
but quote escaping gets *really* hairy. Trust me, I tried. Time to get a real
programming language. Enter Python: short and sweet.

    :::python
    #!/usr/bin/env python
    import subprocess

    command = 'sudo aptitude update && sudo aptitude safe-upgrade'
    terminal = ['gnome-terminal']
    for host in ('server1', 'server2'):
        terminal.extend(['--tab', '-e', '''
            bash -c '
                echo "%(host)s$ %(command)s"
                ssh -t %(host)s "%(command)s"
                read
            '
        ''' % locals()])
    subprocess.call(terminal)

(Find this code [on github](https://github.com/SimonSapin/snippets/blob/master/gnome_terminal_tabs.py))

Two tricks here reduce the quote escaping by a level each: `subprocess` can
take an actual list of argument instead of a space-separated string, and Python
has triple-quoted strings that can contain unescaped quotes.

Bonus: it displays what command is being run on what server in each shell.

Link that to somewhere in your `$PATH` with a name that works well with 
bash-completion, and that’s pretty much as good as it gets.
