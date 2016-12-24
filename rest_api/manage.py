from flask import url_for
from flask_script import Manager
from IoP import app
import urllib.parse

manager = Manager(app)


@manager.command
def list_routes():
    output = []
    for rule in app.url_map.iter_rules():
        output.append(str(rule))

    for line in sorted(output):
        print(line)

if __name__ == "__main__":
    manager.run()
