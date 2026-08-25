def test_sensitive_routes_reject_anonymous_access(client):
    paths = (
        "/api/v1/admin/students",
        "/api/v1/dashboard/student",
        "/api/v1/dashboard/mentor",
        "/api/v1/dashboard/industry",
        "/api/v1/organizations",
        "/api/v1/mentorship/assignments",
        "/api/v1/notifications",
    )

    for path in paths:
        assert client.get(path).status_code == 401, path


def test_invalid_bearer_token_is_rejected(client):
    response = client.get(
        "/api/v1/admin/students",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
