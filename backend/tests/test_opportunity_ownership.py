def test_company_routes_require_auth(client):
    assert client.get('/api/v1/internships/company/postings').status_code == 401

def test_job_routes_require_auth(client):
    assert client.get('/api/v1/jobs').status_code == 401
