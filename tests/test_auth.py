def test_registration(client):
    r=client.post('/api/v1/auth/register/student',json={'email':'x@example.com','password':'StrongPass123','first_name':'X','last_name':'Y'})
    assert r.status_code in (201,409)
