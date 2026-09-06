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

def test_effective_role_comes_from_active_membership(client):
    override = client.app.dependency_overrides[get_db]
    db = next(override())
    owner = User(id=uuid.uuid4(), email='owner-role@example.com', password_hash='test-only', role='STUDENT')
    faculty = User(id=uuid.uuid4(), email='faculty-role@example.com', password_hash='test-only', role='STUDENT')
    db.add_all([owner, faculty]); db.commit()
    owner_token = create_access_token(str(owner.id), owner.role)
    created = client.post('/api/v1/organizations', headers={'Authorization': f'Bearer {owner_token}'}, json={'name':'Role Institute','organization_type':'INSTITUTION','slug':'role-institute'})
    assert created.status_code == 201
    organization_id = created.json()['id']
    added = client.post(
        f'/api/v1/organizations/{organization_id}/members',
        headers={'Authorization': f'Bearer {owner_token}'},
        json={'user_id': str(faculty.id), 'role': 'FACULTY'},
    )
    assert added.status_code == 201
    faculty_token = create_access_token(str(faculty.id), faculty.role)
    response = client.get('/api/v1/auth/me', headers={
        'Authorization': f'Bearer {faculty_token}',
        'X-Organization-ID': organization_id,
    })
    assert response.status_code == 200
    body = response.json()['data']
    assert body['role'] == 'STUDENT'
    assert body['effective_role'] == 'FACULTY'
    assert body['active_organization_id'] == organization_id
