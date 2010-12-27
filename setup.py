from setuptools import setup

setup(
    name='Exyr.org',
    version='0.1',
    author='Simon Sapin <simon.sapin@exyr.org>',
    packages=['exyr'],
    description='Code running the website at http://exyr.org',
    include_package_data = True,
    zip_safe=False,
    license="BSD License",
    install_requires=[
        'Flask',
        'Flask-FlatPages',
        'Flask-Static',
        'Flask-Script',
        'Pygments',
    ],
    entry_points={'console_scripts': [
        'exyr-manage=exyr.manage:manager.run',
    ]},
)
