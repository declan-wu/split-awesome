from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import app, db

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()

# heroku run python manage.py db init --app split-awesome
# heroku run python manage.py db migrate --app split-awesome
# heroku run python manage.py db upgrade --app split-awesome


