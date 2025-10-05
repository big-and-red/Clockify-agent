from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class ClockifyTimeEntry(BaseModel):
    id: str
    description: Optional[str] = None
    tagIds: Optional[List[str]] = None
    userId: str
    billable: bool
    taskId: Optional[str] = None
    projectId: Optional[str] = None
    workspaceId: str
    timeInterval: Dict[str, Any]
    customFieldValues: Optional[List[Any]] = None
    type: str
    kioskId: Optional[str] = None
    hourlyRate: Optional[Dict[str, Any]] = None
    costRate: Optional[Dict[str, Any]] = None
    isLocked: bool

class ClockifyProject(BaseModel):
    id: str
    name: str
    hourlyRate: Optional[Dict[str, Any]] = None
    clientId: Optional[str] = None
    workspaceId: str
    billable: bool
    memberships: Optional[List[Any]] = None
    color: str
    estimate: Optional[Dict[str, Any]] = None
    archived: bool
    duration: Optional[str] = None
    clientName: Optional[str] = None
    note: Optional[str] = None
    costRate: Optional[Dict[str, Any]] = None
    timeEstimate: Optional[Dict[str, Any]] = None
    budgetEstimate: Optional[Dict[str, Any]] = None
    estimateReset: Optional[Dict[str, Any]] = None
    public: bool
    template: bool
