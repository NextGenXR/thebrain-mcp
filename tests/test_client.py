"""Tests for TheBrainAPIClient (with respx mock)."""

import pytest
import respx
from httpx import Response

from thebrain_mcp.client import TheBrainAPIClient
from thebrain_mcp.exceptions import TheBrainAuthError, TheBrainNotFoundError


@respx.mock
@pytest.mark.asyncio
async def test_list_brains_returns_list() -> None:
    respx.get("https://api.bra.in/brains").mock(
        return_value=Response(200, json=[{"id": "b1", "name": "My Brain"}])
    )
    client = TheBrainAPIClient(api_key="test-key")
    try:
        brains = await client.list_brains()
        assert len(brains) == 1
        assert brains[0]["id"] == "b1"
    finally:
        await client.close()


@respx.mock
@pytest.mark.asyncio
async def test_get_thought_404_raises_not_found() -> None:
    respx.get("https://api.bra.in/thoughts/brain1/thought1").mock(
        return_value=Response(404, text="Not Found")
    )
    client = TheBrainAPIClient(api_key="test-key")
    try:
        with pytest.raises(TheBrainNotFoundError):
            await client.get_thought("brain1", "thought1")
    finally:
        await client.close()


@respx.mock
@pytest.mark.asyncio
async def test_401_raises_auth_error() -> None:
    respx.get("https://api.bra.in/brains").mock(
        return_value=Response(401, text="Unauthorized")
    )
    client = TheBrainAPIClient(api_key="bad-key")
    try:
        with pytest.raises(TheBrainAuthError):
            await client.list_brains()
    finally:
        await client.close()
