import pytest
import httpx
import logging
from unittest.mock import patch, AsyncMock, MagicMock
from services.webhooks import dispatch_webhook


@pytest.mark.asyncio
async def test_dispatch_webhook_success(caplog):
    # Tell caplog to capture INFO level logs for this test
    caplog.set_level(logging.INFO)

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        await dispatch_webhook("https://fake-erp.com/hook", {"status": "success"})

        mock_post.assert_called_once_with("https://fake-erp.com/hook", json={"status": "success"}, timeout=10.0)
        mock_response.raise_for_status.assert_called_once()
        assert "Successfully dispatched webhook" in caplog.text


@pytest.mark.asyncio
async def test_dispatch_webhook_empty_url():
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        await dispatch_webhook("", {"status": "success"})
        mock_post.assert_not_called()


@pytest.mark.asyncio
async def test_dispatch_webhook_http_error(caplog):
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            message="404 Not Found",
            request=httpx.Request("POST", "https://fake-erp.com/hook"),
            response=mock_response
        )
        mock_post.return_value = mock_response

        await dispatch_webhook("https://fake-erp.com/hook", {"status": "success"})

        assert "Webhook failed with status 404" in caplog.text


@pytest.mark.asyncio
async def test_dispatch_webhook_connection_error(caplog):
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.ConnectError("Failed to resolve host")

        await dispatch_webhook("https://fake-erp.com/hook", {"status": "success"})

        assert "Failed to dispatch webhook to https://fake-erp.com/hook" in caplog.text