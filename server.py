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
        "Mock HubSpot CRM for Quince B2B sales and marketing. Query contacts, companies, "
        "deals, sales sequences, sequence enrollments, marketing analytics, email campaigns, "
        "and pipeline summary."
    ),
)

# ---------------------------------------------------------------------------
# Contacts
# ---------------------------------------------------------------------------

@mcp.tool()
def get_contacts(
    id: Optional[str] = Field(default=None, description="Filter by contact ID, e.g. CT01"),
    email: Optional[str] = Field(default=None, description="Filter by email (partial match)"),
    last_name: Optional[str] = Field(default=None, description="Filter by last name (partial match)"),
    company: Optional[str] = Field(default=None, description="Filter by company name (partial match)"),
    lifecycle_stage: Optional[str] = Field(default=None, description="Filter by lifecycle stage: subscriber | lead | marketing_qualified_lead | sales_qualified_lead | opportunity | customer"),
    lead_source: Optional[str] = Field(default=None, description="Filter by lead source: organic_search | paid_social | email | referral | trade_show | direct"),
    owner_id: Optional[str] = Field(default=None, description="Filter by owner/rep ID, e.g. REP01"),
    tag: Optional[str] = Field(default=None, description="Filter by tag — checks the tags array (partial match), e.g. boutique"),
) -> list[dict]:
    """List Quince B2B contacts including boutique buyers, department store buyers, and corporate gifting leads. Filter by ID, email, last name, company, lifecycle stage, lead source, owner, or tag."""
    results = _db["contacts"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if email:
        results = [r for r in results if _match(r, "email", email)]
    if last_name:
        results = [r for r in results if _match(r, "last_name", last_name)]
    if company:
        results = [r for r in results if _match(r, "company", company)]
    if lifecycle_stage:
        results = [r for r in results if _match(r, "lifecycle_stage", lifecycle_stage)]
    if lead_source:
        results = [r for r in results if _match(r, "lead_source", lead_source)]
    if owner_id:
        results = [r for r in results if r.get("owner_id", "").upper() == owner_id.upper()]
    if tag:
        results = [r for r in results if _match_array(r, "tags", tag)]
    return results


# ---------------------------------------------------------------------------
# Companies
# ---------------------------------------------------------------------------

@mcp.tool()
def get_companies(
    id: Optional[str] = Field(default=None, description="Filter by company ID, e.g. CO01"),
    name: Optional[str] = Field(default=None, description="Filter by company name (partial match)"),
    company_type: Optional[str] = Field(default=None, description="Filter by type: boutique | department_store | corporate | ecommerce | wholesale_distributor"),
    lifecycle_stage: Optional[str] = Field(default=None, description="Filter by lifecycle stage: lead | marketing_qualified_lead | sales_qualified_lead | opportunity | customer"),
    country: Optional[str] = Field(default=None, description="Filter by country code, e.g. US | GB | CA"),
    owner_id: Optional[str] = Field(default=None, description="Filter by owner/rep ID, e.g. REP01"),
    tag: Optional[str] = Field(default=None, description="Filter by tag — checks the tags array (partial match), e.g. boutique"),
) -> list[dict]:
    """List Quince partner companies including boutiques, department stores, corporate accounts, and wholesale distributors. Filter by ID, name, type, lifecycle stage, country, owner, or tag."""
    results = _db["companies"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if name:
        results = [r for r in results if _match(r, "name", name)]
    if company_type:
        results = [r for r in results if _match(r, "company_type", company_type)]
    if lifecycle_stage:
        results = [r for r in results if _match(r, "lifecycle_stage", lifecycle_stage)]
    if country:
        results = [r for r in results if _match(r, "country", country)]
    if owner_id:
        results = [r for r in results if r.get("owner_id", "").upper() == owner_id.upper()]
    if tag:
        results = [r for r in results if _match_array(r, "tags", tag)]
    return results


# ---------------------------------------------------------------------------
# Deals
# ---------------------------------------------------------------------------

@mcp.tool()
def get_deals(
    id: Optional[str] = Field(default=None, description="Filter by deal ID, e.g. DL01"),
    deal_name: Optional[str] = Field(default=None, description="Filter by deal name (partial match)"),
    company_id: Optional[str] = Field(default=None, description="Filter by company ID, e.g. CO01"),
    contact_id: Optional[str] = Field(default=None, description="Filter by contact ID, e.g. CT01"),
    stage: Optional[str] = Field(default=None, description="Filter by stage: appointment_scheduled | qualified_to_buy | presentation_scheduled | decision_maker_bought_in | contract_sent | closed_won | closed_lost"),
    pipeline: Optional[str] = Field(default=None, description="Filter by pipeline: Wholesale | Corporate_Gifting | Retail_Partnership"),
    owner_id: Optional[str] = Field(default=None, description="Filter by owner/rep ID, e.g. REP01"),
    deal_type: Optional[str] = Field(default=None, description="Filter by deal type: new_business | existing_business"),
    product: Optional[str] = Field(default=None, description="Filter by product — checks the products array (partial match), e.g. Cashmere"),
) -> list[dict]:
    """List Quince B2B deals across Wholesale, Retail Partnership, and Corporate Gifting pipelines. Filter by ID, deal name, company, contact, stage, pipeline, owner, deal type, or product."""
    results = _db["deals"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if deal_name:
        results = [r for r in results if _match(r, "deal_name", deal_name)]
    if company_id:
        results = [r for r in results if (r.get("company_id") or "").upper() == company_id.upper()]
    if contact_id:
        results = [r for r in results if (r.get("contact_id") or "").upper() == contact_id.upper()]
    if stage:
        results = [r for r in results if _match(r, "stage", stage)]
    if pipeline:
        results = [r for r in results if _match(r, "pipeline", pipeline)]
    if owner_id:
        results = [r for r in results if r.get("owner_id", "").upper() == owner_id.upper()]
    if deal_type:
        results = [r for r in results if _match(r, "deal_type", deal_type)]
    if product:
        results = [r for r in results if _match_array(r, "products", product)]
    return results


# ---------------------------------------------------------------------------
# Sequences
# ---------------------------------------------------------------------------

@mcp.tool()
def get_sequences(
    id: Optional[str] = Field(default=None, description="Filter by sequence ID, e.g. SQ01"),
    name: Optional[str] = Field(default=None, description="Filter by sequence name (partial match)"),
    status: Optional[str] = Field(default=None, description="Filter by status: active | paused | draft"),
    created_by: Optional[str] = Field(default=None, description="Filter by creator rep ID, e.g. REP01"),
) -> list[dict]:
    """List Quince sales sequences. Filter by ID, name, status, or creator."""
    results = _db["sequences"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if name:
        results = [r for r in results if _match(r, "name", name)]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    if created_by:
        results = [r for r in results if r.get("created_by", "").upper() == created_by.upper()]
    return results


# ---------------------------------------------------------------------------
# Sequence Enrollments
# ---------------------------------------------------------------------------

@mcp.tool()
def get_sequence_enrollments(
    sequence_id: Optional[str] = Field(default=None, description="Filter by sequence ID, e.g. SQ01"),
    contact_id: Optional[str] = Field(default=None, description="Filter by contact ID, e.g. CT01"),
    company_name: Optional[str] = Field(default=None, description="Filter by company name (partial match)"),
    status: Optional[str] = Field(default=None, description="Filter by enrollment status: active | completed | replied | unsubscribed | paused"),
    reply_received: Optional[bool] = Field(default=None, description="Filter by whether a reply has been received: true | false"),
) -> list[dict]:
    """List sequence enrollment records showing which contacts are enrolled in which sales sequences. Filter by sequence ID, contact ID, company name, status, or reply received."""
    results = _db["sequence_enrollments"]
    if sequence_id:
        results = [r for r in results if r["sequence_id"].upper() == sequence_id.upper()]
    if contact_id:
        results = [r for r in results if r["contact_id"].upper() == contact_id.upper()]
    if company_name:
        results = [r for r in results if _match(r, "company_name", company_name)]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    if reply_received is not None:
        results = [r for r in results if r.get("reply_received") == reply_received]
    return results


# ---------------------------------------------------------------------------
# Marketing Analytics
# ---------------------------------------------------------------------------

@mcp.tool()
def get_marketing_analytics(
    channel: Optional[str] = Field(default=None, description="Filter by channel: organic_search | paid_social | email | referral | paid_search | direct"),
    week_start: Optional[str] = Field(default=None, description="Filter by exact week start date, e.g. 2026-08-04"),
    start_date: Optional[str] = Field(default=None, description="Filter records with week_start >= this date, e.g. 2026-08-01"),
    end_date: Optional[str] = Field(default=None, description="Filter records with week_start <= this date, e.g. 2026-08-28"),
) -> list[dict]:
    """Return weekly marketing analytics records broken down by channel. Filter by channel, exact week, or a date range using start_date and end_date."""
    results = _db["marketing_analytics"]
    if channel:
        results = [r for r in results if _match(r, "channel", channel)]
    if week_start:
        results = [r for r in results if r["week_start"] == week_start]
    if start_date:
        results = [r for r in results if r["week_start"] >= start_date]
    if end_date:
        results = [r for r in results if r["week_start"] <= end_date]
    return results


# ---------------------------------------------------------------------------
# Email Campaigns
# ---------------------------------------------------------------------------

@mcp.tool()
def get_email_campaigns(
    id: Optional[str] = Field(default=None, description="Filter by campaign ID, e.g. EC01"),
    name: Optional[str] = Field(default=None, description="Filter by campaign name (partial match)"),
    type: Optional[str] = Field(default=None, description="Filter by type: newsletter | promotional | nurture | re_engagement | announcement"),
    status: Optional[str] = Field(default=None, description="Filter by status: sent | scheduled | draft"),
    segment: Optional[str] = Field(default=None, description="Filter by segment: all_contacts | boutique_leads | corporate_prospects | customers"),
) -> list[dict]:
    """List Quince email campaigns. Filter by ID, name, type, status, or audience segment."""
    results = _db["email_campaigns"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if name:
        results = [r for r in results if _match(r, "name", name)]
    if type:
        results = [r for r in results if _match(r, "type", type)]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    if segment:
        results = [r for r in results if _match(r, "segment", segment)]
    return results


# ---------------------------------------------------------------------------
# Forms
# ---------------------------------------------------------------------------

@mcp.tool()
def get_forms(
    id: Optional[str] = Field(default=None, description="Filter by form ID, e.g. FM01"),
    name: Optional[str] = Field(default=None, description="Filter by form name (partial match)"),
    type: Optional[str] = Field(default=None, description="Filter by form type: contact | demo_request | wholesale_inquiry | gifting_inquiry"),
) -> list[dict]:
    """List Quince HubSpot forms including wholesale inquiry, gifting inquiry, demo request, and general contact forms. Filter by ID, name, or type."""
    results = _db["forms"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if name:
        results = [r for r in results if _match(r, "name", name)]
    if type:
        results = [r for r in results if _match(r, "type", type)]
    return results


# ---------------------------------------------------------------------------
# Pipeline Summary
# ---------------------------------------------------------------------------

@mcp.tool()
def get_pipeline_summary() -> dict:
    """Return the aggregated pipeline summary including total pipeline value, deal counts by stage and pipeline, weighted pipeline, average deal size, sales cycle, and win rate."""
    return _db["pipeline_summary"]


# ---------------------------------------------------------------------------
# Create Contact
# ---------------------------------------------------------------------------

@mcp.tool()
def create_contact(
    first_name: str = Field(description="Contact first name"),
    last_name: str = Field(description="Contact last name"),
    email: str = Field(description="Contact email address"),
    company: str = Field(description="Company or organization name"),
    job_title: str = Field(description="Contact job title, e.g. Head Buyer"),
    lead_source: str = Field(description="Lead source: organic_search | paid_social | email | referral | trade_show | direct"),
    owner_id: Optional[str] = Field(default=None, description="Assigned rep ID, e.g. REP01"),
    notes: Optional[str] = Field(default=None, description="Initial notes about this contact"),
) -> dict:
    """Create a new B2B contact in HubSpot with lifecycle_stage set to 'lead'."""
    new_id = f"CT{str(len(_db['contacts']) + 1).zfill(2)}"
    now = datetime.now(timezone.utc).isoformat()
    record = {
        "id": new_id,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": None,
        "company": company,
        "job_title": job_title,
        "lifecycle_stage": "lead",
        "lead_source": lead_source,
        "created_at": now,
        "last_activity_at": now,
        "owner_id": owner_id,
        "tags": [],
        "notes": notes,
        "country": None,
    }
    _db["contacts"].append(record)
    return record


# ---------------------------------------------------------------------------
# Update Contact
# ---------------------------------------------------------------------------

@mcp.tool()
def update_contact(
    id: str = Field(description="Contact ID to update, e.g. CT01"),
    lifecycle_stage: Optional[str] = Field(default=None, description="New lifecycle stage: subscriber | lead | marketing_qualified_lead | sales_qualified_lead | opportunity | customer"),
    owner_id: Optional[str] = Field(default=None, description="Reassign to rep ID, e.g. REP02"),
    notes: Optional[str] = Field(default=None, description="Replace the notes field with this text"),
    tag: Optional[str] = Field(default=None, description="Append a tag to the contact's tags array"),
) -> dict:
    """Update a contact's lifecycle stage, owner, notes, or add a tag."""
    matches = [r for r in _db["contacts"] if r["id"].upper() == id.upper()]
    if not matches:
        return {"error": f"Contact {id} not found"}
    record = matches[0]
    if lifecycle_stage:
        record["lifecycle_stage"] = lifecycle_stage
    if owner_id:
        record["owner_id"] = owner_id
    if notes is not None:
        record["notes"] = notes
    if tag:
        if tag not in record.get("tags", []):
            record.setdefault("tags", []).append(tag)
    record["last_activity_at"] = datetime.now(timezone.utc).isoformat()
    return record


# ---------------------------------------------------------------------------
# Create Deal
# ---------------------------------------------------------------------------

@mcp.tool()
def create_deal(
    deal_name: str = Field(description="Name of the deal, e.g. Velvet Thread — Spring Order"),
    company_id: Optional[str] = Field(default=None, description="Associated company ID, e.g. CO01"),
    contact_id: Optional[str] = Field(default=None, description="Associated contact ID, e.g. CT01"),
    pipeline: str = Field(description="Pipeline: Wholesale | Corporate_Gifting | Retail_Partnership"),
    stage: str = Field(description="Initial stage: appointment_scheduled | qualified_to_buy | presentation_scheduled | decision_maker_bought_in | contract_sent"),
    amount_usd: Optional[float] = Field(default=None, description="Deal value in USD"),
    close_date: Optional[str] = Field(default=None, description="Expected close date, e.g. 2026-10-31"),
    owner_id: Optional[str] = Field(default=None, description="Assigned rep ID, e.g. REP01"),
    products_csv: Optional[str] = Field(default=None, description="Comma-separated product names, e.g. 'Cashmere Crewneck Sweater, Linen Relaxed Trouser'"),
    notes: Optional[str] = Field(default=None, description="Deal notes"),
) -> dict:
    """Create a new B2B deal in HubSpot."""
    new_id = f"DL{str(len(_db['deals']) + 1).zfill(2)}"
    now = datetime.now(timezone.utc).isoformat()
    products = [p.strip() for p in products_csv.split(",")] if products_csv else []
    record = {
        "id": new_id,
        "deal_name": deal_name,
        "contact_id": contact_id,
        "company_id": company_id,
        "stage": stage,
        "pipeline": pipeline,
        "amount_usd": amount_usd,
        "close_date": close_date,
        "owner_id": owner_id,
        "created_at": now,
        "last_activity_at": now,
        "deal_type": "new_business",
        "products": products,
        "notes": notes,
    }
    _db["deals"].append(record)
    return record


# ---------------------------------------------------------------------------
# Update Deal
# ---------------------------------------------------------------------------

@mcp.tool()
def update_deal(
    id: str = Field(description="Deal ID to update, e.g. DL01"),
    stage: Optional[str] = Field(default=None, description="New stage: appointment_scheduled | qualified_to_buy | presentation_scheduled | decision_maker_bought_in | contract_sent | closed_won | closed_lost"),
    amount_usd: Optional[float] = Field(default=None, description="Updated deal value in USD"),
    close_date: Optional[str] = Field(default=None, description="Updated expected close date, e.g. 2026-11-15"),
    notes: Optional[str] = Field(default=None, description="Replace the notes field with this text"),
) -> dict:
    """Update a deal's stage, amount, close date, or notes."""
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
    if notes is not None:
        record["notes"] = notes
    record["last_activity_at"] = datetime.now(timezone.utc).isoformat()
    return record


# ---------------------------------------------------------------------------
# Enroll in Sequence
# ---------------------------------------------------------------------------

@mcp.tool()
def enroll_in_sequence(
    sequence_id: str = Field(description="Sequence ID to enroll the contact in, e.g. SQ01"),
    contact_id: str = Field(description="Contact ID to enroll, e.g. CT01"),
    notes: Optional[str] = Field(default=None, description="Notes about this enrollment"),
) -> dict:
    """Enroll a contact in a sales sequence. Creates a new sequence_enrollment record with status 'active' at step 1."""
    seq_matches = [s for s in _db["sequences"] if s["id"].upper() == sequence_id.upper()]
    if not seq_matches:
        return {"error": f"Sequence {sequence_id} not found"}
    contact_matches = [c for c in _db["contacts"] if c["id"].upper() == contact_id.upper()]
    if not contact_matches:
        return {"error": f"Contact {contact_id} not found"}

    seq = seq_matches[0]
    contact = contact_matches[0]
    new_id = f"SE{str(len(_db['sequence_enrollments']) + 1).zfill(2)}"
    now = datetime.now(timezone.utc).isoformat()

    record = {
        "id": new_id,
        "sequence_id": seq["id"],
        "sequence_name": seq["name"],
        "contact_id": contact["id"],
        "contact_name": f"{contact['first_name']} {contact['last_name']}",
        "company_name": contact.get("company"),
        "enrolled_at": now,
        "status": "active",
        "current_step": 1,
        "last_email_sent_at": None,
        "next_email_scheduled_at": None,
        "reply_received": False,
        "notes": notes,
    }
    _db["sequence_enrollments"].append(record)

    # Update sequence active enrollment count
    seq["active_enrollments"] = seq.get("active_enrollments", 0) + 1
    seq["enrolled_contacts"] = seq.get("enrolled_contacts", 0) + 1

    return record


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
