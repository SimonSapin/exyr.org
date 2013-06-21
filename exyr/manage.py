import subprocess

from flask_script import Manager
from . import app
from .freezer import freezer


manager = Manager(app, with_default_commands=False)


@manager.command
def run():
    """Start a development server."""
    app.run(debug=True)


@manager.command
def freeze(serve=False):
    """Freezes the static version of the website."""
    if serve:
        freezer.run(debug=True)
    else:
        urls = freezer.freeze()
        print('Built %i files.' % len(urls))


@manager.command
def up(destination='hako:http/exyr.org/htdocs/'):
    """Freezes and uploads the website."""
    push = subprocess.Popen(['git', 'push'], stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    print('### Freezing')
    freeze()
    print('### Uploading to', destination)
    subprocess.call(
        ['rsync', '-Pah', '--del', freezer.root + '/', destination])
    print('### Pushing to github')
    stdout, stderr = push.communicate()
    # stdout was redirected
    print(stdout)


@manager.shell
def shell_context():
    from . import app, pages
    from .freezer import freezer
    return locals()


if __name__ == '__main__':
    manager.run()
