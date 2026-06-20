def test_register_login_me_and_case_crud(client):
    register_response = client.post("/api/auth/register", json={"email": "tester@example.com", "password": "Password123!"})
    assert register_response.status_code == 201
    assert register_response.json()["email"] == "tester@example.com"

    me_response = client.get("/api/auth/me")
    assert me_response.status_code == 200

    create_case_response = client.post("/api/cases", json={"title": "Scam case", "description": "Evidence about fraud"})
    assert create_case_response.status_code == 201
    case_id = create_case_response.json()["id"]

    list_cases_response = client.get("/api/cases")
    assert list_cases_response.status_code == 200
    assert len(list_cases_response.json()) == 1

    update_case_response = client.put(f"/api/cases/{case_id}", json={"title": "Updated title"})
    assert update_case_response.status_code == 200
    assert update_case_response.json()["title"] == "Updated title"

    get_case_response = client.get(f"/api/cases/{case_id}")
    assert get_case_response.status_code == 200
    assert get_case_response.json()["title"] == "Updated title"
