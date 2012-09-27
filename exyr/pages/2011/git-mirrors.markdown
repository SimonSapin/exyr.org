title: Mirroring a Gitorious repository to GitHub
published: 2011-04-30
tags: [git, backups]
summary: |
    You can not make Gitorious or GitHub push to somewhere else, so mirroring
    them requires a few more steps.

I recently started working on [WeasyPrint](http://weasyprint.org/). Development
is done [on Gitorious](https://gitorious.org/+kozea/weasyprint/weasyprint)
as with the company’s other projects, but I also wanted it on
[my GitHub account](https://github.com/SimonSapin/) so that the project would
get a bit more visibility.

There is nothing special with GitHub and Gitorious here. This technique would
work exactly the same the other way around or with other servers.

In a nutshell
-------------

    :::sh
    # Inital setup
    git clone --mirror git://gitorious.org/weasyprint/weasyprint.git weasyprint
    GIT_DIR=weasyprint git remote add github git@github.com:SimonSapin/WeasyPrint.git
    
    # In cron
    cd /path/to/weasyprint && git fetch -q && git push -q --mirror github

How it works
------------

Mirroring with [Git](http://git-scm.com/) is pretty easy: just pull from or
push to another repository. GitHub and Gitorious allow you to push
to them or pull from them, but you can not make them push to somewhere else.
You need something in the middle.

Digging a bit in the man pages tells you that the magic option is
``--mirror``. First, clone your “source” repository:

    :::sh
    git clone --mirror git://gitorious.org/weasyprint/weasyprint.git weasyprint

``--mirror`` implies ``--bare``. This repository is not for working, you don’t
want it to have a working directory. More importantly,
``--mirror`` sets up the *origin* remote so that ``git fetch`` will directly
fetch into local branches without doing any merge. It will force the update
if the remote history has diverged from the local one.

    :::sh
    git fetch

Now our local repository is an exact mirror of what we have on Gitorious.
Let’s push it to GitHub:

    :::sh
    git remote add github git@github.com:SimonSapin/WeasyPrint.git
    git push --mirror github

The ``--mirror`` option for ``git push`` is similar to that for ``git clone``:
instead of pushing just a branch, it says that all references (branches,
tags, …) should be the same on the remote end as they are here, even if it
means forced updates or removing.

Now our GitHub repository also is a mirror. Let’s update it every hour with
cron. The ``-q`` option says to suppress normal output but keep error messages,
which cron should send you by email if your server is properly configured.

    :::sh
    42 *    * * *   cd /path/to/weasyprint && git fetch -q && git push -q --mirror github

Warning: ``--mirror`` is like ``--force``
-----------------------------------------

Both ``--mirror`` options are kind of like ``--force`` in that you can
lose data if you’re not careful. It will make exact mirrors, no question asked.
If you push changes to the mirror’s destination, they will be
overwritten/removed on the next update if they are not in the mirror’s source.


