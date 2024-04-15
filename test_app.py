from app import app

import pytest

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200

def test_callback_route(client):
    response = client.get('/callback')
    assert response.status_code == 302 

def test_logout_route(client):
    response = client.get('/logout')
    assert response.status_code == 200

def test_feed_route(client):
    response = client.get('/feed')
    assert response.status_code == 200

def test_create_route(client):
    response = client.get('/create')
    assert response.status_code == 200
