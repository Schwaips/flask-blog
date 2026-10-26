import pytest
from flaskr.db import get_db


def test_index(client, auth):
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'test title' in response.data
    assert b'by test on 2018-01-01' in response.data
    assert b'test\nbody' in response.data
    assert b'href="/1/update"' in response.data

@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login"


def test_author_required(app, client, auth):
    # change the post author to another user
    with app.app_context():
        db = get_db()
        db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
        db.commit()

    auth.login()
    # current user can't modify other user's post
    assert client.post('/1/update').status_code == 403
    assert client.post('/1/delete').status_code == 403
    # current user doesn't see edit link
    assert b'href="/1/update"' not in client.get('/').data


@pytest.mark.parametrize('path', (
    '/2/update',
    '/2/delete',
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404

def test_create(client, auth, app):
    auth.login()
    assert client.get('/create').status_code == 200
    client.post('/create', data={'title': 'created', 'body': ''})

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert count == 2


def test_update(client, auth, app):
    auth.login()
    assert client.get('/1/update').status_code == 200
    client.post('/1/update', data={'title': 'updated', 'body': ''})

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post['title'] == 'updated'


@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={'title': '', 'body': ''})
    assert b'Title is required.' in response.data

def test_delete(client, auth, app):
    auth.login()
    response = client.post('/1/delete')
    assert response.headers["Location"] == "/"

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post is None


@pytest.mark.parametrize('published', (False, True))
def test_create_publication_status(client, auth, app, published):
    auth.login()
    data = {'title': 'new article', 'body': 'article body'}
    if published:
        data['is_published'] = 'on'

    response = client.post('/create', data=data)
    assert response.status_code == 302

    with app.app_context():
        post = get_db().execute(
            'SELECT is_published FROM post WHERE title = ?', ('new article',)
        ).fetchone()
        assert bool(post['is_published']) is published


def test_draft_visibility(client, auth):
    auth.login()
    client.post('/create', data={'title': 'private draft', 'body': 'secret content'})
    response = client.get('/')
    assert b'private draft' in response.data
    assert b'Brouillon' in response.data

    auth.logout()
    response = client.get('/')
    assert b'private draft' not in response.data
    assert b'secret content' not in response.data
    assert b'test title' in response.data

    client.post(
        '/auth/register',
        data={'username': 'reader', 'password': 'reader-password'},
    )
    response = auth.login(username='reader', password='reader-password')
    assert response.headers["Location"] == "/"
    response = client.get('/')
    assert b'private draft' not in response.data
    assert b'secret content' not in response.data
    assert client.get('/2/update').status_code == 403
    assert client.post('/2/delete').status_code == 403


def test_publish_and_unpublish(client, auth, app):
    auth.login()
    data = {'title': 'publication example', 'body': 'example body'}

    # An unchecked checkbox is absent from the submitted form.
    client.post('/1/update', data=data)
    auth.logout()
    assert b'publication example' not in client.get('/').data

    auth.login()
    client.post('/1/update', data={**data, 'is_published': 'on'})
    auth.logout()
    assert b'publication example' in client.get('/').data

    with app.app_context():
        post = get_db().execute('SELECT is_published FROM post WHERE id = 1').fetchone()
        assert post['is_published'] == 1


@pytest.mark.parametrize('path', ('/create', '/1/update'))
@pytest.mark.parametrize('published', (False, True))
def test_publication_checkbox_preserved_on_error(client, auth, path, published):
    auth.login()
    data = {'title': '', 'body': 'body'}
    if published:
        data['is_published'] = 'on'
    response = client.post(path, data=data)
    assert b'Title is required.' in response.data
    checkbox = response.data.split(b'id="is_published"', 1)[1].split(b'>', 1)[0]
    assert (b'checked' in checkbox) is published
