def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'ok'
    assert json_data['student'] == 'Khadija Bukar'

def test_login_logout(client):
    login_res = client.post('/auth/login', data={
        'username': 'test_admin',
        'password': 'AdminPass123!'
    }, follow_redirects=True)
    assert login_res.status_code == 200
    assert b'Welcome back' in login_res.data or b'Command Center' in login_res.data

    logout_res = client.get('/auth/logout', follow_redirects=True)
    assert logout_res.status_code == 200
    assert b'logged out' in logout_res.data
