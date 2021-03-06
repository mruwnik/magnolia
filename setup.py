from setuptools import setup, find_packages


packages = find_packages('src')

setup(
    name='magnolia',
    version='0.1',
    description='Simulate the phyllotaxy of plant stems',
    author='Daniel O\'Connell',
    author_email='tojad99@gmail.com',
    packages=packages,
    package_dir={'': 'src'},
    install_requires=[
        'ipython',
        'qtpy==1.2.1',
        'path.py==10.1',
    ],
    tests_require=[
        'pytest==2.7.3',
        'pylama==7.4.3',
        'pylama_pylint==2.0.0',
        'pylint==1.4.4',
        'hypothesis==3.1.0',
    ],
    entry_points={
        # this is totally incorrect, but it's just as a reminder of how it's done
        # 'forms': ['pyuic5 ui/mainwindow.ui > src/magnolia/ui/forms.py']
    },
)
