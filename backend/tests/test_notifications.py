def test_notifications_require_auth(client):
    assert client.get('/api/v1/notifications').status_code == 401

def test_notification_read_requires_auth(client):
    assert client.post('/api/v1/notifications/read-all').status_code == 401
