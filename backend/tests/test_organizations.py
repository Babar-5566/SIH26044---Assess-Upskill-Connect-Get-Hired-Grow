import uuid
from app.models import User
from app.core.security import create_access_token
from app.db.session import get_db

def test_organization_requires_auth(client):
    assert client.get('/api/v1/organizations').status_code == 401

def test_create_organization(client):
    override = client.app.dependency_overrides[get_db]
    db = next(override())
    user = User(id=uuid.uuid4(), email='owner@example.com', password_hash='test-only', role='STUDENT')
    db.add(user); db.commit()
    token = create_access_token(str(user.id), user.role)
    response = client.post('/api/v1/organizations', headers={'Authorization': f'Bearer {token}'}, json={'name':'Example Institute','organization_type':'INSTITUTION','slug':'example-institute'})
    assert response.status_code == 201
    assert response.json()['organization_type'] == 'INSTITUTION'
