from math import log
from typing import Any

import requests
from mcp.server.fastmcp import Context, FastMCP

# Initialize FastMCP server
mcp = FastMCP("intranafri")

# Constants
BASE_URL = "http://staging.intranav.io/api"
TOKEN = "de4038abc355c84e88e3168bb519ffd7fab57cd1"

TEST_UID = "hp"

HEADERS = {
    "Authorization": f"Api-Key {TOKEN}",
    "Content-Type": "application/json"
}

def make_api_request(endpoint: str):
    """
    Perform a GET request on a specific API endpoint.
    """
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("GET request failed:", e)
        return None


@mcp.tool()
async def get_available_assets() -> Any:
    """
    Fetch a list of all available assets.
    """
    endpoint = "/assets?categoryId=8"
    return make_api_request(endpoint)


@mcp.tool()
async def get_position_of_asset_by_uid(uid):
    """
    Fetch position data for a specific UID.
    """
    endpoint = f"positions/{uid}"
    return make_api_request(endpoint)

 
@mcp.tool()
async def get_zone_of_asset_by_uid(uid: str, ctx: Context):
    """
    Fetch zone data for a specific UID.
    """
    await ctx.info(f"UID: {uid}")
    endpoint = f"devices/locators/current-zone/{uid}"
    zone_id = make_api_request(endpoint)
    await ctx.info(f"Zone ID: {zone_id}")
    endpoint = f"zones/{zone_id}"
    zone_data = make_api_request(endpoint)
    await ctx.info(f"Zone data: {zone_data}")
    return zone_data["properties"]["label"] if zone_data else None

# Run the server
if __name__ == "__main__":
    transport = "stdio"
    if transport == "stdio":
        print("Running server with stdio transport")
        mcp.run(transport="stdio")
    elif transport == "sse":
        print("Running server with SSE transport")
        mcp.run(transport="sse")
    else:
        raise ValueError(f"Unknown transport: {transport}")