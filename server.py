import json
import os
from pathlib import Path
from typing import Optional
from fastmcp import FastMCP
from pydantic import Field

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

_DATA_PATH = Path(__file__).parent / "data" / "hubspot.json"
_db: dict = json.loads(_DATA_PATH.read_text())


def _match(record: dict, field: str, value: str) -> bool:
    """Case-insensitive substring match on a field."""
    return value.lower() in str(record.get(field, "")).lower()


def _match_array(record: dict, field: str, value: str) -> bool:
    """Case-insensitive substring match against any element of an array field."""
    items = record.get(field, [])
    return any(value.lower() in str(item).lower() for item in items)


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="hubspot-mock",
    version="1.0.0",
    instructions=(
        "Mock HubSpot CRM for Nabis cannabis wholesale distribution. "
        "Query dispensary accounts (companies), buyer contacts, deals pipeline, "
        "and CX support tickets."
    ),
)

# ---------------------------------------------------------------------------
# Companies
# ---------------------------------------------------------------------------

@mcp.tool()
def get_companies(
    id: Optional[str] = Field(default=None, description="Filter by company ID, e.g. CMP-001"),
    name: Optional[str] = Field(default=None, description="Filter by company name (partial match)"),
    city: Optional[str] = Field(default=None, description="Filter by city (partial match)"),
    lifecycle_stage: Optional[str] = Field(default=None, description="Filter by lifecycle stage: customer | lead | opportunity"),
    account_manager: Optional[str] = Field(default=None, description="Filter by account manager name (partial match)"),
    tag: Optional[str] = Field(default=None, description="Filter by tag value, e.g. vip or net30 (checks tags array)"),
) -> list[dict]:
    """List dispensary accounts. Optionally filter by ID, name, city, lifecycle stage, account manager, or tag."""
    results = _db["companies"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if name:
        results = [r for r in results if _match(r, "name", name)]
    if city:
        results = [r for r in results if _match(r, "city", city)]
    if lifecycle_stage:
        results = [r for r in results if _match(r, "lifecycle_stage", lifecycle_stage)]
    if account_manager:
        results = [r for r in results if _match(r, "account_manager", account_manager)]
    if tag:
        results = [r for r in results if _match_array(r, "tags", tag)]
    return results


# ---------------------------------------------------------------------------
# Contacts
# ---------------------------------------------------------------------------

@mcp.tool()
def get_contacts(
    id: Optional[str] = Field(default=None, description="Filter by contact ID, e.g. CON-001"),
    company_id: Optional[str] = Field(default=None, description="Filter by company ID, e.g. CMP-002"),
    last_name: Optional[str] = Field(default=None, description="Filter by last name (partial match)"),
    job_title: Optional[str] = Field(default=None, description="Filter by job title (partial match), e.g. Purchasing Manager"),
    lifecycle_stage: Optional[str] = Field(default=None, description="Filter by lifecycle stage: customer | lead"),
) -> list[dict]:
    """List buyer contacts. Optionally filter by ID, company, last name, job title, or lifecycle stage."""
    results = _db["contacts"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if company_id:
        results = [r for r in results if r["company_id"].upper() == company_id.upper()]
    if last_name:
        results = [r for r in results if _match(r, "last_name", last_name)]
    if job_title:
        results = [r for r in results if _match(r, "job_title", job_title)]
    if lifecycle_stage:
        results = [r for r in results if _match(r, "lifecycle_stage", lifecycle_stage)]
    return results


# ---------------------------------------------------------------------------
# Deals
# ---------------------------------------------------------------------------

@mcp.tool()
def get_deals(
    id: Optional[str] = Field(default=None, description="Filter by deal ID, e.g. DEAL-001"),
    company_id: Optional[str] = Field(default=None, description="Filter by company ID, e.g. CMP-001"),
    stage: Optional[str] = Field(default=None, description="Filter by stage: prospecting | qualification | proposal_sent | contract_sent | closed_won | closed_lost"),
    pipeline: Optional[str] = Field(default=None, description="Filter by pipeline: New Accounts | Reactivation | Upsell"),
    owner: Optional[str] = Field(default=None, description="Filter by deal owner name (partial match)"),
    product: Optional[str] = Field(default=None, description="Filter by product name (partial match, checks products array), e.g. Heavy Hitters"),
) -> list[dict]:
    """List sales pipeline deals. Optionally filter by ID, company, stage, pipeline, owner, or product."""
    results = _db["deals"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if company_id:
        results = [r for r in results if r["company_id"].upper() == company_id.upper()]
    if stage:
        results = [r for r in results if _match(r, "stage", stage)]
    if pipeline:
        results = [r for r in results if _match(r, "pipeline", pipeline)]
    if owner:
        results = [r for r in results if _match(r, "owner", owner)]
    if product:
        results = [r for r in results if _match_array(r, "products", product)]
    return results


# ---------------------------------------------------------------------------
# Tickets
# ---------------------------------------------------------------------------

@mcp.tool()
def get_tickets(
    id: Optional[str] = Field(default=None, description="Filter by ticket ID, e.g. TKT-001"),
    company_id: Optional[str] = Field(default=None, description="Filter by company ID, e.g. CMP-002"),
    category: Optional[str] = Field(default=None, description="Filter by category: order_issue | billing | delivery | product_quality | account | compliance"),
    priority: Optional[str] = Field(default=None, description="Filter by priority: low | medium | high | urgent"),
    status: Optional[str] = Field(default=None, description="Filter by status: open | in_progress | waiting_on_customer | resolved | closed"),
    owner: Optional[str] = Field(default=None, description="Filter by ticket owner name (partial match)"),
) -> list[dict]:
    """List CX support tickets. Optionally filter by ID, company, category, priority, status, or owner."""
    results = _db["tickets"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if company_id:
        results = [r for r in results if r["company_id"].upper() == company_id.upper()]
    if category:
        results = [r for r in results if _match(r, "category", category)]
    if priority:
        results = [r for r in results if _match(r, "priority", priority)]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    if owner:
        results = [r for r in results if _match(r, "owner", owner)]
    return results


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
