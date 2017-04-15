from setuptools import setup, find_packages


packages = find_packages()

setup(
    name='magnolia',
    version='0.1',
    description='Simulate the phyllotaxy of plant stems',
    author='Daniel O\'Connell',
    author_email='tojad99@gmail.com',
    packages=packages,
    install_requires=[
        'ipython',
        'PyQt5',
    ],
    tests_require=[
        'pytest==2.7.3',
        'pylama==6.3.4',
        'pylama_pylint==2.0.0',
        'pylint==1.4.4',
        'hypothesis==3.1.0',
    ],
    entry_points={
        'pytest11': [
            'magnolia = tests.pytest_plugin',
        ],
        # this is totally incorrect, but it's just as a reminder of how it's done
        'forms': ['pyuic5 ui/mainwindow.ui > ui/forms.py']
    },
)
