from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_
from datetime import datetime, timedelta, date

from typing import List
from activities.models import Activity
from activities.utils import set_activity_name_based_on_activity_type, ACTIVITY_NAME_TO_ID
from .schema import (
    WeeklySummaryResponse, MonthlySummaryResponse, YearlySummaryResponse,
    LifetimeSummaryResponse, YearlyTotalItem,
    DaySummary, WeekSummary, MonthSummary, SummaryMetrics, TypeBreakdownItem
)

def _get_type_breakdown(db: Session, user_id: int, start_date: date | None = None, end_date: date | None = None, activity_type: str | None = None) -> List[TypeBreakdownItem]:
    """Helper function to get summary breakdown by activity type, optionally filtered by a specific type and date range."""
    query = db.query(
        Activity.activity_type.label('activity_type'),
        func.coalesce(func.sum(Activity.distance), 0).label('total_distance'),
        func.coalesce(func.sum(Activity.total_timer_time), 0.0).label('total_duration'),
        func.coalesce(func.sum(Activity.elevation_gain), 0).label('total_elevation_gain'),
        func.coalesce(func.sum(Activity.calories), 0).label('total_calories'),
        func.count(Activity.id).label('activity_count')
    ).filter(
        Activity.user_id == user_id
    )

    # Apply date range filter if provided
    if start_date and end_date:
        query = query.filter(
            Activity.start_time >= start_date,
            Activity.start_time < end_date
        )

    # Apply activity type filter if provided
    if activity_type:
        activity_type_id = ACTIVITY_NAME_TO_ID.get(activity_type.lower())
        if activity_type_id is not None:
            query = query.filter(Activity.activity_type == activity_type_id)
        else:
            # If the provided type name is invalid, return no results for the breakdown
            return None

    query = query.group_by(
        Activity.activity_type
    ).order_by(
        func.count(Activity.id).desc(), # Order by count descending
        Activity.activity_type.asc() # Then by type ascending
    )

    type_results = query.all()
    type_breakdown_list = []
    for row in type_results:
        activity_type_name = set_activity_name_based_on_activity_type(row.activity_type) # Keep getting name for now
        type_breakdown_list.append(TypeBreakdownItem(
            activity_type_id=int(row.activity_type), # Add the numeric ID
            activity_type=activity_type_name, # Keep sending the name too
            total_distance=float(row.total_distance),
            total_duration=float(row.total_duration),
            total_elevation_gain=float(row.total_elevation_gain),
            total_calories=float(row.total_calories),
            activity_count=int(row.activity_count)
        ))
    # Return the list (can be empty if filtered type has no activities)
    return type_breakdown_list

def get_weekly_summary(db: Session, user_id: int, target_date: date, activity_type: str | None = None) -> WeeklySummaryResponse:
    start_of_week = target_date - timedelta(days=target_date.weekday())
    end_of_week = start_of_week + timedelta(days=7)

    # Base query for daily breakdown
    query = db.query(
        extract('isodow', Activity.start_time).label('day_of_week'),
        func.coalesce(func.sum(Activity.distance), 0).label('total_distance'),
        func.coalesce(func.sum(Activity.total_timer_time), 0.0).label('total_duration'),
        func.coalesce(func.sum(Activity.elevation_gain), 0).label('total_elevation_gain'),
        func.coalesce(func.sum(Activity.calories), 0).label('total_calories'),
        func.count(Activity.id).label('activity_count')
    ).filter(
        Activity.user_id == user_id,
        Activity.start_time >= start_of_week,
        Activity.start_time < end_of_week
    )

    # Apply activity type filter if provided
    activity_type_id = None
    if activity_type:
        activity_type_id = ACTIVITY_NAME_TO_ID.get(activity_type.lower())
        if activity_type_id is not None:
            query = query.filter(Activity.activity_type == activity_type_id)
        else:
            # If type is invalid, the query will return no results, leading to an empty summary
            query = query.filter(Activity.id == -1) # Force no results

    # Continue with grouping and ordering
    query = query.group_by(
        extract('isodow', Activity.start_time)
    ).order_by(
        extract('isodow', Activity.start_time)
    )

    daily_results = query.all()
    breakdown = []
    overall_metrics = SummaryMetrics()

    day_map = {day.day_of_week: day for day in daily_results}

    for i in range(1, 8): # ISO day 1 (Mon) to 7 (Sun)
        day_data = day_map.get(i)
        if day_data:
            day_summary = DaySummary(
                day_of_week=i - 1, # Adjust to 0-6
                total_distance=float(day_data.total_distance),
                total_duration=float(day_data.total_duration),
                total_elevation_gain=float(day_data.total_elevation_gain),
                total_calories=float(day_data.total_calories),
                activity_count=int(day_data.activity_count)
            )
            breakdown.append(day_summary)
            overall_metrics.total_distance += day_summary.total_distance
            overall_metrics.total_duration += day_summary.total_duration
            overall_metrics.total_elevation_gain += day_summary.total_elevation_gain
            overall_metrics.total_calories += day_summary.total_calories
            overall_metrics.activity_count += day_summary.activity_count
        else:
             breakdown.append(DaySummary(day_of_week=i - 1)) # Add empty summary for days with no activity

    return WeeklySummaryResponse(
        total_distance=overall_metrics.total_distance,
        total_duration=overall_metrics.total_duration,
        total_elevation_gain=overall_metrics.total_elevation_gain,
        total_calories=overall_metrics.total_calories,
        activity_count=overall_metrics.activity_count,
        breakdown=breakdown,
        # Pass filter to type breakdown helper
        type_breakdown=_get_type_breakdown(db, user_id, start_of_week, end_of_week, activity_type)
    )

def get_monthly_summary(db: Session, user_id: int, target_date: date, activity_type: str | None = None) -> MonthlySummaryResponse:
    start_of_month = target_date.replace(day=1)
    next_month = (start_of_month + timedelta(days=32)).replace(day=1)
    end_of_month = next_month

    # Base query for weekly breakdown within the month
    query = db.query(
        extract('week', Activity.start_time).label('week_number'),
        func.coalesce(func.sum(Activity.distance), 0).label('total_distance'),
        func.coalesce(func.sum(Activity.total_timer_time), 0.0).label('total_duration'),
        func.coalesce(func.sum(Activity.elevation_gain), 0).label('total_elevation_gain'),
        func.coalesce(func.sum(Activity.calories), 0).label('total_calories'),
        func.count(Activity.id).label('activity_count')
    ).filter(
        Activity.user_id == user_id,
        Activity.start_time >= start_of_month,
        Activity.start_time < end_of_month
    )

    # Apply activity type filter if provided
    activity_type_id = None
    if activity_type:
        activity_type_id = ACTIVITY_NAME_TO_ID.get(activity_type.lower())
        if activity_type_id is not None:
            query = query.filter(Activity.activity_type == activity_type_id)
        else:
            query = query.filter(Activity.id == -1) # Force no results

    # Continue with grouping and ordering
    query = query.group_by(
        extract('week', Activity.start_time)
    ).order_by(
        extract('week', Activity.start_time)
    )

    weekly_results = query.all()
    breakdown = []
    overall_metrics = SummaryMetrics()

    for week_data in weekly_results:
        week_summary = WeekSummary(
            week_number=int(week_data.week_number),
            total_distance=float(week_data.total_distance),
            total_duration=float(week_data.total_duration),
            total_elevation_gain=float(week_data.total_elevation_gain),
            total_calories=float(week_data.total_calories),
            activity_count=int(week_data.activity_count)
        )
        breakdown.append(week_summary)
        overall_metrics.total_distance += week_summary.total_distance
        overall_metrics.total_duration += week_summary.total_duration
        overall_metrics.total_elevation_gain += week_summary.total_elevation_gain
        overall_metrics.total_calories += week_summary.total_calories
        overall_metrics.activity_count += week_summary.activity_count

    return MonthlySummaryResponse(
        total_distance=overall_metrics.total_distance,
        total_duration=overall_metrics.total_duration,
        total_elevation_gain=overall_metrics.total_elevation_gain,
        total_calories=overall_metrics.total_calories,
        activity_count=overall_metrics.activity_count,
        breakdown=breakdown,
        # Pass filter to type breakdown helper
        type_breakdown=_get_type_breakdown(db, user_id, start_of_month, end_of_month, activity_type)
    )

def get_yearly_summary(db: Session, user_id: int, year: int, activity_type: str | None = None) -> YearlySummaryResponse:
    start_of_year = date(year, 1, 1)
    end_of_year = date(year + 1, 1, 1)

    # Base query for monthly breakdown within the year
    query = db.query(
        extract('month', Activity.start_time).label('month_number'),
        func.coalesce(func.sum(Activity.distance), 0).label('total_distance'),
        func.coalesce(func.sum(Activity.total_timer_time), 0.0).label('total_duration'),
        func.coalesce(func.sum(Activity.elevation_gain), 0).label('total_elevation_gain'),
        func.coalesce(func.sum(Activity.calories), 0).label('total_calories'),
        func.count(Activity.id).label('activity_count')
    ).filter(
        Activity.user_id == user_id,
        Activity.start_time >= start_of_year,
        Activity.start_time < end_of_year
    )

    # Apply activity type filter if provided
    activity_type_id = None
    if activity_type:
        activity_type_id = ACTIVITY_NAME_TO_ID.get(activity_type.lower())
        if activity_type_id is not None:
            query = query.filter(Activity.activity_type == activity_type_id)
        else:
            query = query.filter(Activity.id == -1) # Force no results

    # Continue with grouping and ordering
    query = query.group_by(
        extract('month', Activity.start_time)
    ).order_by(
        extract('month', Activity.start_time)
    )

    monthly_results = query.all()
    breakdown = []
    overall_metrics = SummaryMetrics()

    month_map = {month.month_number: month for month in monthly_results}

    for i in range(1, 13): # Month 1 (Jan) to 12 (Dec)
        month_data = month_map.get(i)
        if month_data:
            month_summary = MonthSummary(
                month_number=i,
                total_distance=float(month_data.total_distance),
                total_duration=float(month_data.total_duration),
                total_elevation_gain=float(month_data.total_elevation_gain),
                total_calories=float(month_data.total_calories),
                activity_count=int(month_data.activity_count)
            )
            breakdown.append(month_summary)
            overall_metrics.total_distance += month_summary.total_distance
            overall_metrics.total_duration += month_summary.total_duration
            overall_metrics.total_elevation_gain += month_summary.total_elevation_gain
            overall_metrics.total_calories += month_summary.total_calories
            overall_metrics.activity_count += month_summary.activity_count
        else:
            breakdown.append(MonthSummary(month_number=i)) # Add empty summary for months with no activity

    return YearlySummaryResponse(
        total_distance=overall_metrics.total_distance,
        total_duration=overall_metrics.total_duration,
        total_elevation_gain=overall_metrics.total_elevation_gain,
        total_calories=overall_metrics.total_calories,
        activity_count=overall_metrics.activity_count,
        breakdown=breakdown,
        # Pass filter to type breakdown helper
        type_breakdown=_get_type_breakdown(db, user_id, start_of_year, end_of_year, activity_type)
    )

def get_lifetime_summary(db: Session, user_id: int, activity_type: str | None = None) -> LifetimeSummaryResponse:
    """
    Retrieves a lifetime summary of all activities for a user, broken down by year.
    """
    # Query for yearly breakdown
    yearly_query = db.query(
        extract('year', Activity.start_time).label('year'),
        func.coalesce(func.sum(Activity.distance), 0).label('total_distance'),
        func.coalesce(func.sum(Activity.total_timer_time), 0.0).label('total_duration'),
        func.coalesce(func.sum(Activity.elevation_gain), 0).label('total_elevation_gain'),
        func.coalesce(func.sum(Activity.calories), 0).label('total_calories'),
        func.count(Activity.id).label('activity_count')
    ).filter(
        Activity.user_id == user_id
    )

    # Apply activity type filter if provided for the yearly breakdown
    activity_type_id = None
    if activity_type:
        activity_type_id = ACTIVITY_NAME_TO_ID.get(activity_type.lower())
        if activity_type_id is not None:
            yearly_query = yearly_query.filter(Activity.activity_type == activity_type_id)
        else:
            # If type is invalid, the query will return no results for yearly breakdown
            yearly_query = yearly_query.filter(Activity.id == -1) # Force no results

    yearly_query = yearly_query.group_by(
        extract('year', Activity.start_time)
    ).order_by(
        extract('year', Activity.start_time).desc() # Show most recent year first
    )

    yearly_results = yearly_query.all()
    breakdown = []
    overall_metrics = SummaryMetrics()

    for row in yearly_results:
        year_summary = YearlyTotalItem(
            year=int(row.year),
            total_distance=float(row.total_distance),
            total_duration=float(row.total_duration),
            total_elevation_gain=float(row.total_elevation_gain),
            total_calories=float(row.total_calories),
            activity_count=int(row.activity_count)
        )
        breakdown.append(year_summary)
        overall_metrics.total_distance += year_summary.total_distance
        overall_metrics.total_duration += year_summary.total_duration
        overall_metrics.total_elevation_gain += year_summary.total_elevation_gain
        overall_metrics.total_calories += year_summary.total_calories
        overall_metrics.activity_count += year_summary.activity_count

    return LifetimeSummaryResponse(
        total_distance=overall_metrics.total_distance,
        total_duration=overall_metrics.total_duration,
        total_elevation_gain=overall_metrics.total_elevation_gain,
        total_calories=overall_metrics.total_calories,
        activity_count=overall_metrics.activity_count,
        breakdown=breakdown,
        type_breakdown=_get_type_breakdown(db, user_id, None, None, activity_type) # Pass None for dates for lifetime type breakdown
    )
