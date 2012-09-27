title: Two Gedit 3 plugins packaged for Arch Linux
published: 2011-07-03
tags: [gedit, packaging, archlinux]
summary:
    I just packaged for Arch Linux the *Gedit Whitespace Terminator* and
    *Gedit Source Code Browser* plugins for Gedit 3. You can find them in
    the AUR.

I recently switched to Arch Linux and Gnome 3. This also means Gedit 3,
which breaks all Gedit 2 plugins. The one I missed most was the
[Class Browser](http://www.stambouliote.de/projects/gedit_plugins.html):

![(Screenshot of the Class Browser)](http://www.stambouliote.de/projects/img/gedit-classbrowser-070122.png)

Luckily [Source Code Browser](https://github.com/Quixotix/gedit-source-code-browser/)
does just the same for Gedit 3. I also started using
[Gedit Whitespace Terminator](https://gitorious.org/gedit-whitespace-terminator)
written by [Guillaume Ayoub](http://community.kozea.org/blog) after he yelled
too many times at me for committing code with trailing white-space into git ;)

Since I’m gonna need to install these more than once, I packaged
[both](http://aur.archlinux.org/packages.php?ID=50409) of
[them](http://aur.archlinux.org/packages.php?ID=50407) for Arch Linux’s AUR.
Hopefully this will be useful for someone else.

I found packaging for Arch much easier than what I remember from my (failed)
attempts at Debian packaging…
