
import pytest

from bmw_analyst.mcp_client.client import MCPClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_mcp_vehicle_sales():

    client = MCPClient()

    response = await client.get_vehicle_sales()

    assert response.success is True
    assert response.tool == "vehicle_sales"
    assert isinstance(response.data, list)

