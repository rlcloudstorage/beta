""""""
import os

from flask import Flask


HELLO_WORLD = """<html>
<head>
    <title>rueben - PythonAnywhere</title>
</head>
<body>
<h1>Hello, World!</h1>
<p>
    This is the default welcome page for a
    <a href="https://www.pythonanywhere.com/">PythonAnywhere</a>
    hosted web application.
</p>
<p>
    Find out more about how to configure your own web application
    by visiting the <a href="https://www.pythonanywhere.com/web_app_setup/">web app setup</a> page
</p>
</body>
</html>"""


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    # app.config.from_mapping(
    #     # a default secret that should be overridden by instance config
    #     SECRET_KEY="dev",
    #     # store the database in the instance folder
    #     DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    # )

    # if test_config is None:
    #     # load the instance config, if it exists, when not testing
    #     app.config.from_pyfile("config.py", silent=True)
    # else:
    #     # load the test config if passed in
    #     app.config.update(test_config)

    # # ensure the instance folder exists
    # try:
    #     os.makedirs(app.instance_path)
    # except OSError:
    #     pass

    @app.route("/hello")
    def hello():
        return HELLO_WORLD

    # # register the database commands
    # from . import db

    # db.init_app(app)

    # apply the blueprints to the app
    # from . import auth
    # from . import stonk

    # app.register_blueprint(auth.bp)
    # app.register_blueprint(stonk.bp)

    # make url_for('index') == url_for('blog.index')
    # in another app, you might define a separate main index here with
    # app.route, while giving the blog blueprint a url_prefix, but for
    # the tutorial the blog will be the main index
    # app.add_url_rule("/", endpoint="index")

    return app



# When people talk about configs in Flask, they are generally talking about loading
# values into the app's configuration. In your above example you could have something
# like app.config.from_object('config') in your init.py file. Then all the configuration
# values will be loaded into the app.config dictionary.

# Then in any of your files you could just import the app object to gain access to that
# dictionary. I tend to access that app object by doing from flask import current_app as app
# then just app.config['MY_SETTING'] to get the value I care about. Read up more in the documentation.

# Note that you can also load values directly from a TOML file:

# import tomllib
# app.config.from_file("config.toml", load=tomllib.load, text=False)

# Or from a JSON file:

# import json
# app.config.from_file("config.json", load=json.load)
