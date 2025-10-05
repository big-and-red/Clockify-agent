from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import date

class TimeBlock(BaseModel):
    start_time: str  # "HH:MM" format
    end_time: str    # "HH:MM" format  
    duration: str    # "HH:MM:SS" format
    description: Optional[str] = None  # Описание того, что делалось

class ProjectSummary(BaseModel):
    hours: float         # 18.2
    formatted: str       # "18h 12m"

class ProjectData(BaseModel):
    total_hours: float
    time_blocks: List[TimeBlock]
    description: Optional[str] = None  # Описание проекта

class DayData(BaseModel):
    projects: Dict[str, ProjectData]
    day_total: float

class ProjectDayData(BaseModel):
    total_hours: float
    time_blocks: List[TimeBlock]

class DailySummary(BaseModel):
    period: str
    active_days: int
    total_time: str              # "25h 30m"
    project_totals: Dict[str, ProjectSummary]

class ProjectTimelineSummary(BaseModel):
    period: str
    active_days: int
    total_time: str              # "18h 12m"
    avg_daily: str               # "2h 36m"
    longest_session: str         # "04:12:00"
    avg_session: str             # "01:15:30"

class DailyTimelineResponse(BaseModel):
    days: Dict[str, DayData]
    summary: DailySummary

class ProjectTimelineResponse(BaseModel):
    project_name: str
    days: Dict[str, ProjectDayData]
    summary: ProjectTimelineSummary
