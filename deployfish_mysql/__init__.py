import os

from cement import App

import deployfish_mysql.adapters  # noqa:F401
from .controllers.mysql import MysqlController

<<<<<<< HEAD
__version__ = "1.2.9"
=======
__version__ = "1.2.10"
>>>>>>> 76f5c50389aeec95c039dd251d05eb1d5c305c06


def add_template_dir(app: App):
    path = os.path.join(os.path.dirname(__file__), 'templates')
    app.add_template_dir(path)


def load(app: App) -> None:
    app.handler.register(MysqlController)
    app.hook.register('post_setup', add_template_dir)
