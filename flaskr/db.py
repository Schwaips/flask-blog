import sqlite3
from datetime import datetime

import click
from flask import current_app, g
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
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

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
def init_db_command():
    """Clear the existing data and create new tables."""
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
