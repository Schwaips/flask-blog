import sqlite3

import pytest
from flaskr import create_app
from flaskr.db import get_db


def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)

def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('flaskr.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called


def test_init_db_creates_latest_schema(tmp_path):
    app = create_app({
        'TESTING': True,
        'SECRET_KEY': 'test',
        'DATABASE': str(tmp_path / 'fresh.sqlite'),
    })
    try:
        result = app.test_cli_runner().invoke(args=['init-db'])
        assert result.exit_code == 0, result.output

        with app.app_context():
            db = get_db()
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                ('new-user', 'test-hash'),
            )
            db.execute(
                'INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)',
                ('new post', 'body', 1),
            )
            db.commit()
            post = db.execute('SELECT * FROM post').fetchone()
            assert post['is_published'] == 1
            assert post['created'] is not None
            assert db.execute('SELECT version_num FROM alembic_version').fetchone() is not None
    finally:
        app.extensions['sqlalchemy_engine'].dispose()


def test_init_db_preserves_data_on_repeated_calls(app, runner):
    with app.app_context():
        users_before = [tuple(row) for row in get_db().execute('SELECT * FROM user ORDER BY id')]
        posts_before = [tuple(row) for row in get_db().execute('SELECT * FROM post ORDER BY id')]

    for _ in range(2):
        result = runner.invoke(args=['init-db'])
        assert result.exit_code == 0, result.output

    with app.app_context():
        assert [tuple(row) for row in get_db().execute('SELECT * FROM user ORDER BY id')] == users_before
        assert [tuple(row) for row in get_db().execute('SELECT * FROM post ORDER BY id')] == posts_before
