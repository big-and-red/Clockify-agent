from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date, datetime

class DailyTimelineRequest(BaseModel):
    start_date: str
    end_date: str
    
    @field_validator('start_date', 'end_date')
    @classmethod
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')

class ProjectTimelineRequest(BaseModel):
    start_date: str
    end_date: str
    project: str
    
    @field_validator('start_date', 'end_date')
    @classmethod
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')
    
    @field_validator('project')
    @classmethod
    def validate_project_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Project name cannot be empty')
        return v.strip()

class ErrorResponse(BaseModel):
    error: str
    message: str
    code: str
