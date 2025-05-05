from pydantic import BaseModel
from typing import List, Optional

class SummaryMetrics(BaseModel):
    total_distance: float = 0.0
    total_duration: float = 0.0
    total_elevation_gain: float = 0.0
    activity_count: int = 0
    total_calories: float = 0.0

class DaySummary(SummaryMetrics):
    day_of_week: int # 0=Monday, 6=Sunday

class WeekSummary(SummaryMetrics):
    week_number: int

class MonthSummary(SummaryMetrics):
    month_number: int # 1=January, 12=December

class TypeBreakdownItem(SummaryMetrics):
    """Schema for breakdown by activity type."""
    activity_type_id: int # Added numeric ID
    activity_type: str

class WeeklySummaryResponse(SummaryMetrics):
    breakdown: List[DaySummary]
    type_breakdown: List[TypeBreakdownItem] | None = None # Added type breakdown

class MonthlySummaryResponse(SummaryMetrics):
    breakdown: List[WeekSummary]
    type_breakdown: List[TypeBreakdownItem] | None = None # Added type breakdown

class YearlySummaryResponse(SummaryMetrics):
    breakdown: List[MonthSummary]
    type_breakdown: List[TypeBreakdownItem] | None = None # Added type breakdown

class SummaryParams(BaseModel):
    user_id: int
    start_date: str
    end_date: str
