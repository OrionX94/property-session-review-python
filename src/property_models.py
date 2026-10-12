from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class MaintenanceRequest:
    property_id: str
    tenant_id: str
    description: str
    priority: str = "normal"


@dataclass(frozen=True)
class TenantDocument:
    tenant_id: str
    document_type: str
    reference: str
    expires_on: date | None = None


@dataclass(frozen=True)
class InspectionReminder:
    property_id: str
    due_on: date
    inspector: str
    notes: str = ""
