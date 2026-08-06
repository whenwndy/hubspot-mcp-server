import json
import os
from datetime import datetime, timezone
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
# Write Tools — Companies
# ---------------------------------------------------------------------------

@mcp.tool()
def create_company(
    name: str = Field(description="Company name"),
    city: str = Field(description="City"),
    state: str = Field(default="CA", description="State"),
    account_manager: Optional[str] = Field(default=None, description="Account manager name"),
    lifecycle_stage: str = Field(default="lead", description="lifecycle stage: customer | lead | opportunity"),
    phone: Optional[str] = Field(default=None, description="Phone number"),
    website: Optional[str] = Field(default=None, description="Website URL"),
    tags: Optional[str] = Field(default=None, description="Comma-separated tags, e.g. vip,net30"),
) -> dict:
    """Create a new dispensary account (company). Returns the created record."""
    new_id = f"CMP-{str(len(_db['companies']) + 1).zfill(3)}"
    record = {
        "id": new_id,
        "name": name,
        "city": city,
        "state": state,
        "industry": "Cannabis Retail",
        "lifecycle_stage": lifecycle_stage,
        "account_manager": account_manager,
        "phone": phone,
        "website": website,
        "tags": [t.strip() for t in tags.split(",")] if tags else [],
        "created_date": datetime.now(timezone.utc).date().isoformat(),
        "last_activity_date": datetime.now(timezone.utc).date().isoformat(),
    }
    _db["companies"].append(record)
    return record


@mcp.tool()
def update_company(
    id: str = Field(description="Company ID to update, e.g. CMP-001"),
    lifecycle_stage: Optional[str] = Field(default=None, description="New lifecycle stage: customer | lead | opportunity"),
    account_manager: Optional[str] = Field(default=None, description="New account manager name"),
    tags: Optional[str] = Field(default=None, description="Comma-separated tags to set, e.g. vip,net30"),
    phone: Optional[str] = Field(default=None, description="Updated phone number"),
    website: Optional[str] = Field(default=None, description="Updated website"),
) -> dict:
    """Update an existing company record. Returns the updated record."""
    matches = [r for r in _db["companies"] if r["id"].upper() == id.upper()]
    if not matches:
        return {"error": f"Company {id} not found"}
    record = matches[0]
    if lifecycle_stage:
        record["lifecycle_stage"] = lifecycle_stage
    if account_manager:
        record["account_manager"] = account_manager
    if tags is not None:
        record["tags"] = [t.strip() for t in tags.split(",")]
    if phone:
        record["phone"] = phone
    if website:
        record["website"] = website
    record["last_activity_date"] = datetime.now(timezone.utc).date().isoformat()
    return record


# ---------------------------------------------------------------------------
# Write Tools — Contacts
# ---------------------------------------------------------------------------

@mcp.tool()
def create_contact(
    first_name: str = Field(description="First name"),
    last_name: str = Field(description="Last name"),
    email: str = Field(description="Email address"),
    company_id: str = Field(description="Company ID this contact belongs to, e.g. CMP-001"),
    job_title: Optional[str] = Field(default=None, description="Job title, e.g. Purchasing Manager"),
    phone: Optional[str] = Field(default=None, description="Phone number"),
    preferred_contact_method: str = Field(default="email", description="email | phone | text"),
    notes: Optional[str] = Field(default=None, description="Additional notes"),
) -> dict:
    """Create a new buyer contact. Returns the created record."""
    new_id = f"CON-{str(len(_db['contacts']) + 1).zfill(3)}"
    record = {
        "id": new_id,
        "company_id": company_id,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "job_title": job_title,
        "lifecycle_stage": "lead",
        "created_date": datetime.now(timezone.utc).date().isoformat(),
        "last_contacted_date": None,
        "preferred_contact_method": preferred_contact_method,
        "notes": notes,
    }
    _db["contacts"].append(record)
    return record


@mcp.tool()
def update_contact(
    id: str = Field(description="Contact ID to update, e.g. CON-001"),
    job_title: Optional[str] = Field(default=None, description="Updated job title"),
    email: Optional[str] = Field(default=None, description="Updated email"),
    phone: Optional[str] = Field(default=None, description="Updated phone"),
    lifecycle_stage: Optional[str] = Field(default=None, description="Updated lifecycle stage: customer | lead"),
    preferred_contact_method: Optional[str] = Field(default=None, description="email | phone | text"),
    notes: Optional[str] = Field(default=None, description="Updated notes"),
) -> dict:
    """Update an existing contact record. Returns the updated record."""
    matches = [r for r in _db["contacts"] if r["id"].upper() == id.upper()]
    if not matches:
        return {"error": f"Contact {id} not found"}
    record = matches[0]
    if job_title:
        record["job_title"] = job_title
    if email:
        record["email"] = email
    if phone:
        record["phone"] = phone
    if lifecycle_stage:
        record["lifecycle_stage"] = lifecycle_stage
    if preferred_contact_method:
        record["preferred_contact_method"] = preferred_contact_method
    if notes:
        record["notes"] = notes
    record["last_contacted_date"] = datetime.now(timezone.utc).date().isoformat()
    return record


# ---------------------------------------------------------------------------
# Write Tools — Deals
# ---------------------------------------------------------------------------

@mcp.tool()
def create_deal(
    deal_name: str = Field(description="Deal name"),
    company_id: str = Field(description="Company ID, e.g. CMP-001"),
    contact_id: Optional[str] = Field(default=None, description="Contact ID, e.g. CON-001"),
    stage: str = Field(default="prospecting", description="Stage: prospecting | qualification | proposal_sent | contract_sent | closed_won | closed_lost"),
    amount_usd: Optional[float] = Field(default=None, description="Deal value in USD"),
    pipeline: str = Field(default="New Accounts", description="New Accounts | Reactivation | Upsell"),
    owner: Optional[str] = Field(default=None, description="Deal owner name"),
    close_date: Optional[str] = Field(default=None, description="Expected close date, e.g. 2026-08-31"),
    products: Optional[str] = Field(default=None, description="Comma-separated product names, e.g. Heavy Hitters,Almora"),
) -> dict:
    """Create a new deal in the pipeline. Returns the created record."""
    new_id = f"DEAL-{str(len(_db['deals']) + 1).zfill(3)}"
    record = {
        "id": new_id,
        "company_id": company_id,
        "contact_id": contact_id,
        "deal_name": deal_name,
        "stage": stage,
        "amount_usd": amount_usd,
        "pipeline": pipeline,
        "owner": owner,
        "close_date": close_date,
        "products": [p.strip() for p in products.split(",")] if products else [],
        "created_date": datetime.now(timezone.utc).date().isoformat(),
        "last_activity_date": datetime.now(timezone.utc).date().isoformat(),
    }
    _db["deals"].append(record)
    return record


@mcp.tool()
def update_deal(
    id: str = Field(description="Deal ID to update, e.g. DEAL-001"),
    stage: Optional[str] = Field(default=None, description="New stage: prospecting | qualification | proposal_sent | contract_sent | closed_won | closed_lost"),
    amount_usd: Optional[float] = Field(default=None, description="Updated deal value in USD"),
    close_date: Optional[str] = Field(default=None, description="Updated close date, e.g. 2026-08-31"),
    owner: Optional[str] = Field(default=None, description="Updated deal owner"),
    products: Optional[str] = Field(default=None, description="Comma-separated products to set"),
) -> dict:
    """Update an existing deal. Returns the updated record."""
    matches = [r for r in _db["deals"] if r["id"].upper() == id.upper()]
    if not matches:
        return {"error": f"Deal {id} not found"}
    record = matches[0]
    if stage:
        record["stage"] = stage
    if amount_usd is not None:
        record["amount_usd"] = amount_usd
    if close_date:
        record["close_date"] = close_date
    if owner:
        record["owner"] = owner
    if products is not None:
        record["products"] = [p.strip() for p in products.split(",")]
    record["last_activity_date"] = datetime.now(timezone.utc).date().isoformat()
    return record


# ---------------------------------------------------------------------------
# Write Tools — Tickets
# ---------------------------------------------------------------------------

@mcp.tool()
def create_ticket(
    subject: str = Field(description="Ticket subject"),
    company_id: str = Field(description="Company ID, e.g. CMP-001"),
    category: str = Field(description="order_issue | billing | delivery | product_quality | account | compliance"),
    priority: str = Field(default="medium", description="low | medium | high | urgent"),
    contact_id: Optional[str] = Field(default=None, description="Contact ID, e.g. CON-001"),
    description: Optional[str] = Field(default=None, description="Ticket description"),
    owner: Optional[str] = Field(default=None, description="Assigned CX owner"),
) -> dict:
    """Create a new CX support ticket. Returns the created record."""
    new_id = f"TKT-{str(len(_db['tickets']) + 1).zfill(3)}"
    record = {
        "id": new_id,
        "company_id": company_id,
        "contact_id": contact_id,
        "subject": subject,
        "category": category,
        "priority": priority,
        "status": "open",
        "created_date": datetime.now(timezone.utc).date().isoformat(),
        "resolved_date": None,
        "owner": owner,
        "description": description,
        "resolution": None,
    }
    _db["tickets"].append(record)
    return record


@mcp.tool()
def update_ticket(
    id: str = Field(description="Ticket ID to update, e.g. TKT-001"),
    status: Optional[str] = Field(default=None, description="New status: open | in_progress | waiting_on_customer | resolved | closed"),
    priority: Optional[str] = Field(default=None, description="New priority: low | medium | high | urgent"),
    owner: Optional[str] = Field(default=None, description="Reassign to new owner"),
    resolution: Optional[str] = Field(default=None, description="Resolution notes — also marks ticket as resolved"),
) -> dict:
    """Update an existing CX ticket status, priority, owner, or resolution. Returns the updated record."""
    matches = [r for r in _db["tickets"] if r["id"].upper() == id.upper()]
    if not matches:
        return {"error": f"Ticket {id} not found"}
    record = matches[0]
    if status:
        record["status"] = status
    if priority:
        record["priority"] = priority
    if owner:
        record["owner"] = owner
    if resolution:
        record["resolution"] = resolution
        record["status"] = "resolved"
        record["resolved_date"] = datetime.now(timezone.utc).date().isoformat()
    return record


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
