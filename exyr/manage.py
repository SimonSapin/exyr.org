from flaskext.script import Manager, Server
from . import app, builder


manager = Manager(app, with_default_commands=False)

# I prefer shorter names
manager.add_command('run', Server())

@manager.shell
def shell_context():
    from . import app, pages, builder
    return locals()


if __name__ == '__main__':
    manager.run()
