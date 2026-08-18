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
        "Mock HubSpot Service Hub for Evive Brands franchise support. "
        "Query and manage support tickets, franchise contacts, agents, "
        "knowledge base articles, SLA policies, pipelines, and support metrics."
    ),
)

# ---------------------------------------------------------------------------
# Tickets
# ---------------------------------------------------------------------------

@mcp.tool()
def get_tickets(
    id: Optional[str] = Field(default=None, description="Filter by ticket ID, e.g. TK001"),
    contact_id: Optional[str] = Field(default=None, description="Filter by contact ID, e.g. CT01"),
    owner_id: Optional[str] = Field(default=None, description="Filter by agent/owner ID, e.g. AG01"),
    status: Optional[str] = Field(default=None, description="Filter by status: open | pending | resolved | closed"),
    priority: Optional[str] = Field(default=None, description="Filter by priority: low | medium | high | urgent"),
    pipeline_id: Optional[str] = Field(default=None, description="Filter by pipeline: PL01 (Franchise & Customer Support) | PL02 (Franchise Onboarding & Success)"),
    stage_id: Optional[str] = Field(default=None, description="Filter by stage ID, e.g. ST01"),
    search: Optional[str] = Field(default=None, description="Search by subject or description (partial match)"),
) -> list[dict]:
    """List franchise support tickets. Filter by ID, contact, owner, status, priority, pipeline, stage, or keyword search."""
    results = _db["tickets"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if contact_id:
        results = [r for r in results if r["contact_id"].upper() == contact_id.upper()]
    if owner_id:
        results = [r for r in results if r["owner_id"].upper() == owner_id.upper()]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    if priority:
        results = [r for r in results if _match(r, "priority", priority)]
    if pipeline_id:
        results = [r for r in results if r["pipeline_id"].upper() == pipeline_id.upper()]
    if stage_id:
        results = [r for r in results if r["stage_id"].upper() == stage_id.upper()]
    if search:
        results = [r for r in results if _match(r, "subject", search) or _match(r, "description", search)]
    return results


@mcp.tool()
def create_ticket(
    subject: str = Field(description="Ticket subject"),
    contact_id: str = Field(description="Contact ID, e.g. CT01"),
    priority: str = Field(default="medium", description="low | medium | high | urgent"),
    pipeline_id: str = Field(default="PL01", description="PL01 (Franchise & Customer Support) | PL02 (Franchise Onboarding & Success)"),
    owner_id: Optional[str] = Field(default=None, description="Agent ID to assign, e.g. AG01"),
    description: Optional[str] = Field(default=None, description="Ticket description"),
) -> dict:
    """Create a new franchise support ticket."""
    new_id = f"TK{str(len(_db['tickets']) + 1).zfill(3)}"
    record = {
        "id": new_id,
        "contact_id": contact_id,
        "subject": subject,
        "description": description,
        "priority": priority,
        "status": "open",
        "pipeline_id": pipeline_id,
        "stage_id": "ST01",
        "owner_id": owner_id,
        "notes": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _db["tickets"].append(record)
    return record


@mcp.tool()
def update_ticket(
    id: str = Field(description="Ticket ID to update, e.g. TK001"),
    status: Optional[str] = Field(default=None, description="New status: open | pending | resolved | closed"),
    priority: Optional[str] = Field(default=None, description="New priority: low | medium | high | urgent"),
    stage_id: Optional[str] = Field(default=None, description="New stage ID, e.g. ST02"),
    owner_id: Optional[str] = Field(default=None, description="Reassign to agent ID"),
    note: Optional[str] = Field(default=None, description="Add a note to the ticket"),
    csat_score: Optional[int] = Field(default=None, description="CSAT score 1-5"),
) -> dict:
    """Update a ticket's status, priority, stage, owner, or add a note."""
    matches = [r for r in _db["tickets"] if r["id"].upper() == id.upper()]
    if not matches:
        return {"error": f"Ticket {id} not found"}
    record = matches[0]
    if status:
        record["status"] = status
    if priority:
        record["priority"] = priority
    if stage_id:
        record["stage_id"] = stage_id
    if owner_id:
        record["owner_id"] = owner_id
    if csat_score is not None:
        record["csat_score"] = csat_score
        record["csat_sent"] = True
    if note:
        record["notes"].append({
            "note_id": f"N{str(len(record['notes']) + 1).zfill(3)}",
            "author_id": owner_id or record.get("owner_id"),
            "body": note,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
    record["updated_at"] = datetime.now(timezone.utc).isoformat()
    return record


# ---------------------------------------------------------------------------
# Contacts
# ---------------------------------------------------------------------------

@mcp.tool()
def get_contacts(
    id: Optional[str] = Field(default=None, description="Filter by contact ID, e.g. CT01"),
    last_name: Optional[str] = Field(default=None, description="Filter by last name (partial match)"),
    company: Optional[str] = Field(default=None, description="Filter by franchise/company name (partial match)"),
    email: Optional[str] = Field(default=None, description="Filter by email (partial match)"),
) -> list[dict]:
    """List franchise contacts. Filter by ID, name, company, or email."""
    results = _db["contacts"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if last_name:
        results = [r for r in results if _match(r, "last_name", last_name)]
    if company:
        results = [r for r in results if _match(r, "company", company)]
    if email:
        results = [r for r in results if _match(r, "email", email)]
    return results


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

@mcp.tool()
def get_agents(
    id: Optional[str] = Field(default=None, description="Filter by agent ID, e.g. AG01"),
    name: Optional[str] = Field(default=None, description="Filter by agent name (partial match)"),
    role: Optional[str] = Field(default=None, description="Filter by role (partial match)"),
) -> list[dict]:
    """List support agents. Filter by ID, name, or role."""
    results = _db["agents"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if name:
        results = [r for r in results if _match(r, "name", name)]
    if role:
        results = [r for r in results if _match(r, "role", role)]
    return results


# ---------------------------------------------------------------------------
# Knowledge Base
# ---------------------------------------------------------------------------

@mcp.tool()
def get_knowledge_base_articles(
    id: Optional[str] = Field(default=None, description="Filter by article ID, e.g. KB01"),
    category: Optional[str] = Field(default=None, description="Filter by category (partial match), e.g. Franchise Operations"),
    status: Optional[str] = Field(default=None, description="Filter by status: published | draft"),
    tag: Optional[str] = Field(default=None, description="Filter by tag (checks tags array), e.g. billing"),
    search: Optional[str] = Field(default=None, description="Search by title or summary (partial match)"),
) -> list[dict]:
    """List knowledge base articles. Filter by ID, category, status, tag, or keyword search."""
    results = _db["knowledge_base_articles"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if category:
        results = [r for r in results if _match(r, "category", category)]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    if tag:
        results = [r for r in results if _match_array(r, "tags", tag)]
    if search:
        results = [r for r in results if _match(r, "title", search) or _match(r, "summary", search)]
    return results


# ---------------------------------------------------------------------------
# SLA Policies
# ---------------------------------------------------------------------------

@mcp.tool()
def get_sla_policies(
    ticket_id: Optional[str] = Field(default=None, description="Filter by ticket ID, e.g. TK001"),
    status: Optional[str] = Field(default=None, description="Filter by SLA status: on_track | at_risk | breached | met"),
    policy_name: Optional[str] = Field(default=None, description="Filter by policy name (partial match)"),
) -> list[dict]:
    """List SLA policy records. Filter by ticket, status, or policy name."""
    results = _db["sla_policies"]
    if ticket_id:
        results = [r for r in results if r["ticket_id"].upper() == ticket_id.upper()]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    if policy_name:
        results = [r for r in results if _match(r, "policy_name", policy_name)]
    return results


# ---------------------------------------------------------------------------
# Pipelines
# ---------------------------------------------------------------------------

@mcp.tool()
def get_pipelines(
    id: Optional[str] = Field(default=None, description="Filter by pipeline ID, e.g. PL01"),
    name: Optional[str] = Field(default=None, description="Filter by pipeline name (partial match)"),
) -> list[dict]:
    """List ticket pipelines and their stages."""
    results = _db["pipelines"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if name:
        results = [r for r in results if _match(r, "name", name)]
    return results


# ---------------------------------------------------------------------------
# Support Metrics
# ---------------------------------------------------------------------------

@mcp.tool()
def get_support_metrics() -> dict:
    """Return aggregated support metrics including open/resolved ticket counts, avg response/resolution times, CSAT score, SLA compliance, and top ticket categories."""
    return _db["support_metrics"]


# ---------------------------------------------------------------------------
# CX Daily Report
# ---------------------------------------------------------------------------

@mcp.tool()
def get_cx_daily_report(
    date: Optional[str] = Field(default=None, description="Report date prefix, e.g. 2026-08-18. Defaults to all tickets if not provided."),
) -> dict:
    """Generate a franchise support daily report covering tickets opened, resolved, SLA risks, escalations, top categories, CSAT, and agent workload."""
    from collections import Counter
    tickets = _db["tickets"]

    opened = [t for t in tickets if date and t["created_at"].startswith(date)] if date else tickets
    resolved = [t for t in tickets if t["status"] in ("resolved", "closed") and (not date or t.get("updated_at", "").startswith(date))]
    at_risk = [s for s in _db["sla_policies"] if s["status"] in ("at_risk", "breached")]
    urgent_high = [t for t in tickets if t["priority"] in ("urgent", "high") and t["status"] in ("open", "pending")]

    category_counts = Counter()
    for cat in _db["support_metrics"]["top_categories"]:
        category_counts[cat["category"]] = cat["count"]
    top_categories = [{"category": k, "count": v} for k, v in category_counts.most_common()]

    scored = [t for t in tickets if t.get("csat_score") is not None]
    avg_csat = round(sum(t["csat_score"] for t in scored) / len(scored), 2) if scored else _db["support_metrics"]["csat_avg_score"]

    agent_load = [{"agent": a["name"], "role": a["role"], "open_tickets": a["open_ticket_count"]} for a in _db["agents"]]
    overloaded = [a for a in agent_load if a["open_tickets"] >= 3]
    staffing_rec = f"{len(overloaded)} agent(s) carrying 3+ open tickets — consider redistributing: {', '.join(a['agent'] for a in overloaded)}." if overloaded else "Agent workload is balanced."

    return {
        "report_date": date or "all",
        "tickets_opened": {"count": len(opened), "tickets": [{"id": t["id"], "subject": t["subject"], "priority": t["priority"], "owner_id": t["owner_id"]} for t in opened]},
        "tickets_resolved": {"count": len(resolved), "tickets": [{"id": t["id"], "subject": t["subject"]} for t in resolved]},
        "sla_at_risk": {"count": len(at_risk), "tickets": [{"ticket_id": s["ticket_id"], "policy": s["policy_name"], "status": s["status"]} for s in at_risk]},
        "urgent_high_open": {"count": len(urgent_high), "tickets": [{"id": t["id"], "subject": t["subject"], "priority": t["priority"]} for t in urgent_high]},
        "top_categories": top_categories,
        "csat": {"avg_score": avg_csat, "total_responses": len(scored) or _db["support_metrics"]["csat_responses"]},
        "agent_workload": agent_load,
        "staffing_recommendation": staffing_rec,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
