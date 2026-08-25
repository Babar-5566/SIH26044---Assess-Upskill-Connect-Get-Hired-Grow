def auth_headers(client, email="project-owner@example.com"):
    response = client.post("/api/v1/auth/register/student", json={"email": email, "password": "StrongPass123", "first_name": "Project", "last_name": "Owner"})
    assert response.status_code == 201
    return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}

def test_project_url_create_read_update_and_validation(client):
    headers = auth_headers(client)
    payload = {"title": "Portfolio", "technologies": ["Python"], "project_url": "https://example.com/project"}
    created = client.post("/api/v1/students/me/projects", json=payload, headers=headers)
    assert created.status_code == 201
    project_id = created.json()["data"]["id"]
    assert created.json()["data"]["project_url"] == payload["project_url"]

    read = client.get(f"/api/v1/students/me/projects/{project_id}", headers=headers)
    assert read.status_code == 200
    assert read.json()["data"]["project_url"] == payload["project_url"]

    updated_url = "https://example.org/updated"
    updated = client.patch(f"/api/v1/students/me/projects/{project_id}", json={**payload, "project_url": updated_url}, headers=headers)
    assert updated.status_code == 200
    assert updated.json()["data"]["project_url"] == updated_url

    invalid = client.post("/api/v1/students/me/projects", json={**payload, "project_url": "not-a-url"}, headers=headers)
    assert invalid.status_code == 422
