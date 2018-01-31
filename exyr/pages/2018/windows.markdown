title: Setting up Windows 10 for programming (in Rust)
published: 2018-01-31
summary: |
    Lately I’ve been working with Windows-specific APIs,
    so I needed to get a Windows dev environment.
    It took me a while to get a setup that I like.
    Here is what I wish I had known before.

Lately I’ve been working with Windows-specific APIs,
so I needed to get a Windows dev environment.
I’ve mostly used Linux for many years now,
so for me programming on Windows feels very foreign.
Getting to a point where I started being productive took a number of steps,
so here they are, if only for me to find them next time.

# Installing Windows 10

* **Buy Windows.**
  Or rather, a license / activation / product key.
  You can do this and *activate* later,
  the installer has a helpful *I don’t have a product key* button.

* **Obtain Windows.**
  This can be entirely separate from the above.
  Search for *Windows 10 ISO* to download an official installer image from Microsoft.

* **Decide where to install Windows.**
  Virtual machines can be great,
  but VirtualBox’s *Enable 3D acceleration* checkbox didn’t cut it for me for GPU programming.
  (The `glutin` crate returned a `NoAvailablePixelFormat` error.)

* **Make an installer media.**
  This isn’t needed on a virtual machine (mount the ISO as a virtual optical drive)
  or on Apple hardware
  (macOS’s Boot Camp Assistant will do its magic if you tell it where find the `.iso` file).
  Fortunately no Windows-only tool is required to make a bootable USB drive,
  the `.iso` file can be copied directly onto the raw device (not on a partition).
  The *Restore Disk Image* functionality of GNOME Disks works.

* **Run the installer.**
  Say no to Cortana, but it’ll still need to be disabled some more after the install.
  In the full-screen *Sign in with Microsoft* page,
  find the small *Offline account* button in the corner.
  Then insist a couple more time that indeed, you do not want a Microsoft account.
  Turn off everything on the *privacy settings* page.

* **Do the usual software update dance.**
  In case the last time you’ve used Windows was before 10, updates are in Settings.
  That’s the gear icon in the Start menu.
  It replaces the Control Panel,
  but only sort of because of course the Control Panel is still there somewhere too.

* **Uninstall crapware.**
  Unfortunately even the official installer from Microsoft comes with some.
  Fortunately most of them can be uninstalled in two clicks in Settings.
  Stuff on the right-hand-side of the Start menu (especially the annoying rotating ones)
  can be remove with right click and *unpin*.

* **Enable Developer Mode** in Settings.
  I don’t know if this is strictly necessary,
  but it has a convenient button to change several settings at once like showing file extensions.

# Installing programming tools

* **Install Visual Studio Community.**
  That’s the free-of-charge one.
  I don’t plan on writing a lot of C/C++ code, but Rust still needs a linker.
  And some crates have C or C++ dependencies.
  And I might need to compile Firefox later,
  search for *build firefox windows* to find the MDN page that lists
  which Visual Studio components to enable.

* **Install Chocolatey.**
  Clicking *Next*, *Next*, *Next* on a GUI installer
  and checking yet another checkbox to accept the GPL again gets old really fast.
  This is a command-line package manager.
  Don’t forget to run the shell as *Administrator*, follow instructions, then close that shell.
  This one won’t have the modified `PATH` environment variable.

* **Install Python and cmake.**
  Some crates use them in their build scripts.
  Run `choco install python2 cmake`, again in an administrative shell.
  (Or find installers on their respective websites.)

* **Install Rust**
  once Visual Studio has finished installing.
  Rustup’s default install method and configuration are fine.

* **Install Git for Windows,**
  which is a separate thing from the Git project’s own Windows builds.
  It comes with a terminal that runs `bash` in a Unix-like environment,
  which can be a lifesaver after many years of working on Linux.
  I hear good things about PowerShell,
  but I don’t feel like investing time in learning something completely different for this.

* **Configure bash.**
  At the moment my `~/.bash_profile` on Windows is as below.
  Without the first two lines, I get colored output from Cargo but not from rustc 1.25.0.
  `RUSTFLAGS` tells rustc to use color even as it thinks the output is not a terminal.
  This is arguably a bug in rustc,
  when running on Windows it only checks for the presence of a Windows console.
  `TERMINFO` lets it know where to find data about how this terminal works.
  Finally, `autocd` implicitly runs `cd` when typing only the path to a directory.

        #!sh
        export RUSTFLAGS="--color always"
        export TERMINFO=$(cygpath -w /usr/share/terminfo)
        shopt -s autocd

# Accessing Windows remotely

Even when I’m sitting next to the machine running Windows,
I prefer to use my usual keyboard and text editor on my main laptop
and accessing other machines through the network.
The fundamental component of that is of course SSH.

There are a few different ways to run an OpenSSH server on Windows.
I’ve had the most success with Chocolatey:

    #!sh
    choco install openssh -params '"/SSHServerFeature /SSHServerPort:2210"'

I don’t understand the nested quotes, but Chocolatey seems to be picky about them.
Using an alternative port number is easier because Windows might already be using port 22,
and it helps my client not freak out about different server keys
when connecting at the same IP address to the other dual-boot operating system.

After connect with a ssh:// URL in Nautilus,
through GNOME’s integration of SFTP/SSH I can edit remote files as if they were local.
For Linux or macOS remote hosts I also run `ssh` in a local terminal to get a remote shell
and do most of my work there,
but on Windows I get a `cmd.exe`-like shell and haven’t yet figured out how to run `bash` there.

So I’ll need remote GUI access, and will be using it a lot.
Both VNC servers I tried were pretty bad, with video latency above one second on a local network.
(The VNC servers on macOS or Linux on the same network from the same client did not have that problem.)
Remote Desktop turned out to work much better, and support copy/pasting across machines.
As to clients:

* `rdesktop` couldn’t connect to my Windows 10’s native Remote Desktop server
* `Vinagre` would randomly get its keyboard input in a broken state, until I disconnect and reconnect.
  (*Have you tried turning it off and on again?*)
* `xfreerdp` works pretty well for me.

xfreerdp is started from the command-line (or a script) and accepts many options.
Some notable ones are:

* `/d: /u:$USER /p:$RDP_PASSWORD` so it doesn’t prompt for credentials.
* `/w:1920 /h:2031` The remote “screen size” is determined by the client!
  This size is half of a 4k monitor,
  leaving enough vertical space for GNOME 3’s top bar and window decoration.
* `/scale:180` Speaking of high DPI,
  this tells the remote application to use a scale factor other than 100%.
  I ended up not using it because it sort of broke Windows’s window manager for me.
  I configured the terminal to use a large font instead.
* `/smart-sizing` Another one I didn’t use, because I prefer sharp text.
  This does client-side scaling based on the size of the local window.
* `+font` Enable font anti-aliasing (ClearType)

# OpenSSH client configuration

This is not specific to Windows, but the usual SSH tricks apply.
The interesting parts of my client-side (on the Linux laptop) `~/.ssh/config` file are below.
See `man ssh_config` for more stuff.


    #!sh
    Host windows
        Hostname 10.11.12.13
        Port 2210

    # When not on the same network, connect through an intermediate SSH server
    Match host windows exec "ip addr|grep -qv 'inet 10\.11\.12\.'"
        ProxyCommand ssh -W %h:%p jumphost

    Host *
        # When a connection is otherwise inactive ping the server regularly.
        # If it’s unresponsive, drop the connection after ~30 seconds.
        # (ServerAliveCountMax defaults to 3.)
        # This helps when resuming the laptop from sleep with open connections,
        # the server might have dropped them in the meantime without the laptop knowing.
        ServerAliveInterval 10
