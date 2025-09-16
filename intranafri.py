from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import psycopg2
import requests

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

PARTS_ASSGINMENT_LIST = (
    "Step 1: Fuselage Shell Assembly\n"
    "Structure: Fuselage Assembly, Panoramic Window, Landing Gear Set, STOL Adjustment Kit, Paint & Exterior Finish, Cargo Floor, Cargo Tie-Down Kit\n"
    "Step 2: Wing Subassembly\n"
    "Structure: Wing Set (Composite), De-icing Boots\n"
    "Step 3: Fan & Ducted Motor Installation\n"
    "Propulsion: Ducted-Fan (Front), Rear Fan\n"
    "Step 4: Engine & Propulsion Integration\n"
    "Propulsion: VTOL Turboshaft Engine\n"
    "Electrical: Battery Pack XL, Heating Unit\n"
    "Step 5: Avionics & Fly-by-Wire Installation\n"
    "Avionics: Fly By Wire Controls, Avionics Suite 600, Camera System, Flight Data Recorder, Weather Radar, IFR Certification Pack, Conference System\n"
    "Electrical: Advanced Wiring Harness, Cabin Lighting System\n"
    "Step 6: Systems Integration & Functional Tests\n"
    "Electrical: All remaining electrical systems\n"
    "Avionics: Integration of all avionics\n"
    "Safety: Pressurization Module, Cabin Emergency System, Oxygen System, Anti-Ice System\n"
    "Step 7: Composite Assembly & Paint\n"
    "Structure: Composite work, Paint & Exterior Finish\n"
    "Step 8: Final Assembly & Pre-Flight Checks\n"
    "Interior: Passenger Seat, Freight Seat, Deluxe Executive Seat, Bar/Refreshment Center\n"
    "Step 9: Ground & Hover Testing\n"
    "All systems: Final checks on propulsion, avionics, electrical, safety\n"
    "Step 10: First Flight & Type Certification\n"
    "Certification: Certification Docs"
)

def make_pg_request(query: str):
    conn = psycopg2.connect(
        dbname="xti_factory_demo",
        user="postgres",
        password="factory123",
        host="staging.intranav.io",
        port="5410"
    )
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            return rows
    finally:
        conn.close()

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
async def get_order_list() -> str:
    """Get a list of all existing customer orders.
    """
    orders = make_pg_request("SELECT order_id, customer_id, order_date, due_date, quantity FROM factory.orders;")
    if not orders:
        return "No orders found."

    order_list = [f"Order ID: {order[0]}, Customer ID: {order[1]}, Order Date: {order[2]}, Due Date: {order[3]}, Quantity: {order[4]}" for order in orders]
    return "\n".join(order_list)

@mcp.tool()
async def get_step_part_list() -> str:
    """Get a list of parts for a each assembly step.
    """
    return PARTS_ASSGINMENT_LIST

@mcp.tool()
async def get_position_of_asset_by_uid(uid):
    """
    Fetch position data for a specific UID.
    """
    endpoint = f"positions/{uid}"
    return make_api_request(endpoint)

async def get_zone_of_asset_by_uid(uid):
    """
    Fetch zone data for a specific UID.
    """
    endpoint = f"devices/locators/current-zone/{uid}"
    return make_api_request(endpoint)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')