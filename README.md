# magnolia
Simulate the phyllotaxy of flowers

# Setup
## Get the code
This can be done manually by downloading the whole project as a zip package, but that is not recommended. The best way is to use [git](https://en.wikipedia.org/wiki/Git). If you go the PyCharm route (see below), then you can most likely get it to do it for you (albeit I don't know if that's true). If you want to do it manually, then the following will do it:

    $ git clone git@github.com:mruwnik/magnolia.git

Git can be daunting at first, but it's most certainly worth the effort to at least know the basics. There are many resources out there, so make use of them, e.g. [here](https://try.github.io/levels/1/challenges/1)

## Install dependancies
This is based on PyQt5 for python3, so the following must be installed:

* Python 3, which can be downloaded [here](https://www.python.org/downloads/). On Debian systems (e.g. Ubuntu), apt-get will do the trick:

    sudo apt-get install python3

* Once you have Python installed, make sure you also have [pip](https://pip.pypa.io/en/stable/installing/) installed. Run the following to check if you have it:

    python -m pip -V

* Qt5 can be downloaded from their [website](http://info.qt.io/download-qt-for-application-development). It's probably best to also install qtcreator while installing the rest of it.
* PyQt5 can be installed via pip. Unfortunately it doesn't want to play nicely with setup.py, and I can't be bothered to get it to work, so this will have to be done manually. More about that below.
* For development it's generally a good idea to have a decent IDE. I personally use [spacemacs](http://info.qt.io/download-qt-for-application-development), but a lot of people are satisfied with e.g. [PyCharm](http://info.qt.io/download-qt-for-application-development). PyCharm makes git easy (as long as your uses are really simple) and it also handles your virtualenvs for you, so it's worth investigating.

## Virtualenv
Python without [virtualenvs](http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/) can lead to dependancy hell, so make use of them. To set up the environment (assuming all dependancies have been installed), run the following commands (skip the `$`):

    $ mkvirtualenv -p /usr/bin/python3 magnolia

If you have python installed somewhere else, make sure to point it to the appropriate place. I named my virtualenv `magnolia`, but you can name it whatever you want.

    $ pip install pyqt5
    $ python setup.py develop
    $ python main.py

That's it. You should now see a window with a sample meristem.

## Windows with PyCharm
 Start by installing the above mentioned dependancies. Also install [git](https://git-scm.com/downloads), then start PyCharm.

### Checkout the project:
* VCS -> Checkout from version control -> git
* set `https://github.com/mruwnik/magnolia.git` as the get repository url
* press `clone`
This should result in PyCharm seeing the project

### Install python dependancies
* open `main.py`
* a popup should appear notifying that certain requirements are missing -> click `Install requirements` -> Install
* After all dependancies are installed (which can take a while) click the green triangle (or Run -> Run) to run the program

# UI modifications
Use QTCreator. There is a ready project in the `ui` folder - open that with qtcreator and you should be good to go. Once you've changed what you want to be changed, make sure to convert `mainwindow.ui` into python classes. To do so execute the following:

    pyuic5 ui/mainwindow.ui > ui/forms.py

Don't make any changes to the `forms.py` file, as it is overwritten every time. See the `Prog` class in [main.py](https://github.com/mruwnik/magnolia/blob/master/main.py#L53), or the end of the [canvas.py](https://github.com/mruwnik/magnolia/blob/master/ui/canvas.py#L181) file to see how widgets can be used. The easiest way is using slots. This amounts to connecting widgets to functions in QtCreator, and then simply adding a function in the appropriate class. For more info check the `allowSelection` or `allowMovement` functions in the `OGLCanvas` class.

# Buds
The whole point of this program is to display buds on meristems. The following classes from the [meristem.py](https://github.com/mruwnik/magnolia/blob/master/meristem.py) file can be used for that:

## Meristem
A collection of buds. That's about it. To add a single bud, use the `add_bud` function. If more are to be added, it's better to make a list of buds, and then pass them all in via the `add` function. `add_bud` is very slow, as each addition results in all vertices being recalculated to speed up OpenGL calls. Using the `add` function only runs the calculations once.

Functions:
* `select` - used to select the meristem. If a bud was clicked on, its `select` function will also be called.
* `calculate_lists` - recalculate all cached vertices info. This is very slow, so try to avoid its usage
* `refresh_field` - recalculate only the data for the given field (e.g. colour data)

## Bud
A single bud. Currently it's just a coloured sphere. The sphere mesh is read in from a file, so changing what is displayed should just amount to replacing [ui/models/sphere.obj](https://github.com/mruwnik/magnolia/blob/master/ui/models/sphere.obj) with a different *.obj model. Each bud is characterised by the following parameters:

 * radius - how far away it is from the meristems main axis. This should be roughly the same for all buds, unless they are at the apex, in which case the radius should be smaller
 * angle - how far the bud is rotated clockwise around the meristem axis (in degrees)
 * height - the buds vertical position along the meristem. The bottom is 0, the closer the apex, the larger the value
 * scale - how much the underlying model should be scaled. Sphere.obj has a radius of more or less 0.5. This option sets the size of the bud
 * fill_colour - the colour of the bud (until decent textures are introduced)
 
 Functions:
 
 * `offset` - the postion of the bud on the X-Z plane, as opposed to an angle and radius. They convey the same information, but in a different manner.
 * `select` - select the given bud. This doesn't really do anything, it's more for subclassing
 
 ## Phyllotaxy
 Currently there are no decent algorithms implemented, just basic ring functions - see `make_ring` and `make_buds` in `main.py`
 
 
 # TODO
 
 * The most interesting part - i.e. the actual simulation of how things grow
 * Installers for windows so this can be installed on normal peoples computers
 * a decent UI
