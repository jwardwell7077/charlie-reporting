"""Dataset header schemas & role rules per spec."""
from __future__ import annotations

ACQ_HEADERS = [
    "Interval Start",
    "Interval End",
    "Interval Complete",
    "Filters",
    "Media Type",
    "Agent Id",
    "Agent Name",
    "Handle",
]
PRODUCTIVITY_HEADERS = [
    "Interval Start",
    "Interval End",
    "Interval Complete",
    "Filters",
    "Agent Id",
    "Agent Name",
    "Logged In",
    "On Queue",
    "Idle",
    "Off Queue",
    "Interacting",
]
QCBS_HEADERS = [
    "Interval Start",
    "Interval End",
    "Interval Complete",
    "Filters",
    "Media Type",
    "Agent Id",
    "Agent Name",
    "Handle",
]
RESC_HEADERS = [
    "Interval Start",
    "Interval End",
    "Interval Complete",
    "Filters",
    "Media Type",
    "Agent Id",
    "Agent Name",
    "Handle",
]
CAMPAIGN_INTERACTIONS_HEADERS = [
    "Full Export Completed",
    "Partial Result Timestamp",
    "Filters",
    "Users",
    "Date",
    "Initial Direction",
    "First Queue",
]
DIALS_HEADERS = [
    "Interval Start",
    "Interval End",
    "Interval Complete",
    "Filters",
    "Media Type",
    "Agent Id",
    "Agent Name",
    "Handle",
    "Avg Handle",
    "Avg Talk",
    "Avg Hold",
    "Avg ACW",
    "Total Handle",
    "Total Talk",
    "Total Hold",
    "Total ACW",
]
IB_CALLS_HEADERS = [
    "Interval Start",
    "Interval End",
    "Interval Complete",
    "Filters",
    "Media Type",
    "Agent Id",
    "Agent Name",
    "Handle",
    "Avg Handle",
]

ROLE_RULES = {
    "ACQ": {"inbound","hybrid"},
    "Productivity": {"inbound","hybrid"},
    "RESC": {"inbound","hybrid"},
    "IB_Calls": {"inbound","hybrid"},
    "QCBS": {"outbound","hybrid"},
    "Dials": {"outbound","hybrid"},
    "Campaign_Interactions": {"inbound","outbound","hybrid"},
}

__all__ = [
    "ACQ_HEADERS","PRODUCTIVITY_HEADERS","QCBS_HEADERS","RESC_HEADERS","CAMPAIGN_INTERACTIONS_HEADERS","DIALS_HEADERS","IB_CALLS_HEADERS","ROLE_RULES"
]
