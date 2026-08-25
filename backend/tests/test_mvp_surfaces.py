def test_skill_gap_requires_auth(client):
    assert client.get('/api/v1/skill-gaps/me?target_role=Data%20Analyst').status_code == 401

def test_mentorship_requires_auth(client):
    assert client.get('/api/v1/mentorship/assignments').status_code == 401

def test_interview_requires_auth(client):
    assert client.get('/api/v1/interviews').status_code == 401
