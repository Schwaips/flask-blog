import sqlite3
from datetime import datetime
from pathlib import Path

import click
from alembic import command
from alembic.config import Config
from flask import current_app, g
from flask.cli import with_appcontext
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session

def get_db():
  if 'db' not in g:
      g.db = sqlite3.connect(
          current_app.config['DATABASE'],
          detect_types=sqlite3.PARSE_DECLTYPES
      )
      g.db.row_factory = sqlite3.Row

  return g.db


def close_db(e=None):
  db = g.pop('db', None)

  if db is not None:
      db.close()


def init_db():
    """Apply pending migrations without clearing existing data."""
    project_root = Path(current_app.root_path).parent
    config = Config(str(project_root / "alembic.ini"))
    # Preserve the logging configuration of the running Flask application.
    config.attributes["skip_logging_config"] = True

    with get_engine().begin() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, "head")

def init_app(app):
    database_url = URL.create(
        "sqlite",
        database=app.config["DATABASE"],
    ) #-> construit l’adresse de la base SQLite à partir du chemin déjà configuré dans DATABASE

    # équivalent de DB = Sequel.connect("sqlite://blog.db")
    app.extensions["sqlalchemy_engine"] = create_engine(database_url) # -> crée le moteur. La connexion réelle s’ouvrira lorsqu’une requête sera exécutée.

    app.teardown_appcontext(close_db)
    app.teardown_appcontext(close_session)
    app.cli.add_command(init_db_command)

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Create or update the database using Alembic migrations; preserve data."""
    init_db()
    click.echo('Initialized the database.')

def get_engine():
    return current_app.extensions["sqlalchemy_engine"]


def get_session():
    if "db_session" not in g:
        g.db_session = Session(get_engine())

    return g.db_session


def close_session(error=None):
    db_session = g.pop("db_session", None)

    if db_session is not None:
        db_session.close()

sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)
