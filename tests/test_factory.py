import pytest

from flaskr import create_app

def test_config(monkeypatch):
  monkeypatch.setenv('SECRET_KEY', 'test')
  assert not create_app().testing
  assert create_app({'TESTING': True}).testing


def test_missing_secret_key(monkeypatch):
  monkeypatch.delenv('SECRET_KEY', raising=False)
  with pytest.raises(RuntimeError, match='SECRET_KEY doit être configurée'):
    create_app({'TESTING': True})


def test_hello(client):
  response = client.get('/hello')
  assert response.data == b'Hello, World!'
