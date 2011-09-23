import subprocess

from flaskext.script import Manager, Server
from . import app
from .freezer import freezer


manager = Manager(app, with_default_commands=False)

# I prefer shorter names
manager.add_command('run', Server())

@manager.command
def freeze(serve=False):
    """Freezes the static version of the website."""
    urls = freezer.freeze()
    print 'Built %i files.' % len(urls)
    if serve:
        freezer.serve()

@manager.command
def up(destination='hako:http/exyr.org/htdocs/'):
    """Freezes and uploads the website."""
    push = subprocess.Popen(['git', 'push'], stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    print '### Freezing'
    freeze()
    print '### Uploading to', destination
    subprocess.call(['rsync', '-Pah', '--del', freezer.root + '/', destination])
    print '### Pushing to github'
    stdout, stderr = push.communicate()
    # stdout was redirected
    print stdout


@manager.shell
def shell_context():
    from . import app, pages
    from .freezer import freezer
    return locals()


if __name__ == '__main__':
    manager.run()
