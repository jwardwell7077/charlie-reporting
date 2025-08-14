import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone
import uuid

from src.interfaces.rest.main import app

pytestmark = pytest.mark.asyncio


async def test_create_email_persists_and_returns_payload():
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as client:
        payload = {
            "message_id": f"msg-{uuid.uuid4()}",
            "subject": "Test Subject",
            "sender": "sender@example.com",
            "recipients": ["a@example.com", "b@example.com"],
            "sent_date": datetime.now(timezone.utc).isoformat(),
            "body_text": "Hello",
        }
        resp = await client.post("/api/v1/emails/", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    required_keys = [
        "id",
        "message_id",
        "subject",
        "sender",
        "recipients",
        "sent_date",
        "status",
    ]
    for key in required_keys:
        assert key in data
    assert data["message_id"] == payload["message_id"]

    # Fetch back
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as client:
        get_resp = await client.get(f"/api/v1/emails/{data['id']}")
    assert get_resp.status_code == 200, get_resp.text
    fetched = get_resp.json()
    assert fetched["id"] == data["id"]
    assert fetched["message_id"] == data["message_id"]


async def test_get_email_not_found_returns_404():
    missing_id = uuid.uuid4()
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as client:
        resp = await client.get(f"/api/v1/emails/{missing_id}")
    assert resp.status_code == 404
    body = resp.json()
    assert body["detail"] == "Email not found"


async def test_list_emails_returns_created_items():
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as client:
        created_ids = []
        for i in range(2):
            payload = {
                "message_id": f"batch-{i}-{uuid.uuid4()}",
                "subject": f"Sub {i}",
                "sender": "list@example.com",
                "recipients": ["x@example.com"],
                "sent_date": datetime.now(timezone.utc).isoformat(),
                "body_text": "Body",
            }
            resp = await client.post("/api/v1/emails/", json=payload)
            assert resp.status_code == 201, resp.text
            created_ids.append(resp.json()["id"])
        # list
        list_resp = await client.get("/api/v1/emails/")
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert isinstance(items, list)
    returned_ids = {item["id"] for item in items}
    for cid in created_ids:
        assert cid in returned_ids


async def test_create_duplicate_message_id_returns_409():
    message_id = f"dup-{uuid.uuid4()}"
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as client:
        payload = {
            "message_id": message_id,
            "subject": "First",
            "sender": "dup@example.com",
            "recipients": ["r@example.com"],
            "sent_date": datetime.now(timezone.utc).isoformat(),
            "body_text": "One",
        }
        r1 = await client.post("/api/v1/emails/", json=payload)
        assert r1.status_code == 201, r1.text
        r2 = await client.post("/api/v1/emails/", json=payload)
    assert r2.status_code == 409
    assert r2.json()["detail"].startswith("Email with message_id")
