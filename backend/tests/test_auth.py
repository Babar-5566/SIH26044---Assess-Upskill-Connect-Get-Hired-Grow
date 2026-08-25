def payload(email):
    return {'email': email, 'password': 'StrongPass123', 'first_name': 'X', 'last_name': 'Y'}

def test_new_unique_student_can_register(client):
    response = client.post('/api/v1/auth/register/student', json=payload('unique@example.com'))
    assert response.status_code == 201
    assert response.json()['data']['user']['email'] == 'unique@example.com'

def test_registering_same_email_twice_returns_409(client):
    data = payload('duplicate@example.com')
    assert client.post('/api/v1/auth/register/student', json=data).status_code == 201
    assert client.post('/api/v1/auth/register/student', json=data).status_code == 409

def test_two_different_emails_can_register(client):
    assert client.post('/api/v1/auth/register/student', json=payload('first@example.com')).status_code == 201
    assert client.post('/api/v1/auth/register/student', json=payload('second@example.com')).status_code == 201
