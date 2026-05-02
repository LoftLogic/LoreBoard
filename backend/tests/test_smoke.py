"""Smoke tests — verify the API is wired up and basic CRUD works."""
import pytest
from httpx import AsyncClient


async def test_health(client: AsyncClient) -> None:
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


async def test_create_and_get_story(client: AsyncClient) -> None:
    r = await client.post("/api/v1/stories", json={"title": "Test Story"})
    assert r.status_code == 201
    story_id = r.json()["id"]

    r = await client.get(f"/api/v1/stories/{story_id}")
    assert r.status_code == 200
    assert r.json()["title"] == "Test Story"


async def test_chapter_marked_stale_on_edit(client: AsyncClient) -> None:
    r = await client.post("/api/v1/stories", json={"title": "Stale Test"})
    story_id = r.json()["id"]

    r = await client.post("/api/v1/chapters", json={
        "story_id": story_id, "order": 1, "title": "Chapter 1", "content": "Original."
    })
    assert r.status_code == 201
    chapter_id = r.json()["id"]
    assert r.json()["analysis_state"] == "pending"

    r = await client.patch(f"/api/v1/chapters/{chapter_id}/content", json={"content": "Edited."})
    assert r.status_code == 200
    assert r.json()["analysis_state"] == "stale"


async def test_chapter_override_roundtrip(client: AsyncClient) -> None:
    r = await client.post("/api/v1/stories", json={"title": "Override Test"})
    story_id = r.json()["id"]
    r = await client.post("/api/v1/chapters", json={"story_id": story_id, "order": 1})
    chapter_id = r.json()["id"]

    await client.post(f"/api/v1/chapters/{chapter_id}/overrides", json={"key": "pov", "value": "unreliable"})
    r = await client.get(f"/api/v1/chapters/{chapter_id}/overrides")
    assert r.json()["overrides"]["pov"] == "unreliable"


async def test_404_on_missing_story(client: AsyncClient) -> None:
    import uuid
    r = await client.get(f"/api/v1/stories/{uuid.uuid4()}")
    assert r.status_code == 404
