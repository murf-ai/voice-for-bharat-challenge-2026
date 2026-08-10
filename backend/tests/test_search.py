import pytest
import json
from unittest.mock import AsyncMock, patch
from agent import Assistant

@pytest.mark.asyncio
async def test_search_products_tool() -> None:
    """Test the search_products tool functionality directly."""
    assistant = Assistant()
    
    # Mock the API response
    mock_response = {
        "products": [
            {"title": "Test Product", "brand": "Test Brand", "price": 10.0, "stock": 5, "rating": 4.0, "category": "test", "availabilityStatus": "In Stock"}
        ]
    }
    
    # We need to mock the urllib call inside search_products
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__.return_value.read.return_value = json.dumps(mock_response).encode("utf-8")
        
        # We need a context for the tool
        # The agent.py doesn't seem to use the 'context' argument, so an empty mock should work
        result = await assistant.search_products(context=AsyncMock(), query="test")
        
        data = json.loads(result)
        assert data["status"] == "success"
        assert len(data["products"]) == 1
        assert data["products"][0]["product_name"] == "Test Product"
        assert data["products"][0]["price"] == "₹850"
