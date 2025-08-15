from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple
import calendar

@dataclass
class Filters:
    period_label: str = "Current Month"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    transaction_types: List[str] = None
    categories: List[str] = None
    payment_methods: List[str] = None
    
    def __post_init__(self):
        if self.transaction_types is None:
            self.transaction_types = ["Income", "Expense"]
        if self.categories is None:
            self.categories = []
        if self.payment_methods is None:
            self.payment_methods = []

def get_period_range(period_label: str) -> Tuple[date, date]:
    """Convert period label to date range"""
    today = date.today()
    
    if period_label == "This Week":
        start_date = today - timedelta(days=today.weekday())
        return (start_date, today)
    elif period_label == "Last Week":
        start_date = today - timedelta(days=today.weekday() + 7)
        end_date = today - timedelta(days=today.weekday() + 1)
        return (start_date, end_date)
    elif period_label == "Last 3 Months":
        start_date = today - timedelta(days=90)
        return (start_date, today)
    elif period_label == "Last 6 Months":
        start_date = today - timedelta(days=180)
        return (start_date, today)
    elif period_label == "Year to Date":
        start_date = date(today.year, 1, 1)
        return (start_date, today)
    elif period_label == "Last 12 Months":
        start_date = today - timedelta(days=365)
        return (start_date, today)
    elif period_label == "This Year":
        start_date = date(today.year, 1, 1)
        end_date = date(today.year, 12, 31)
        return (start_date, min(end_date, today))
    else:
        # Handle specific month (e.g., "August 2025")
        try:
            parts = period_label.split()
            if len(parts) == 2:
                month_name, year_str = parts
                year = int(year_str)
                month = datetime.strptime(month_name, '%B').month
                start_date = date(year, month, 1)
                last_day = calendar.monthrange(year, month)[1]
                end_date = date(year, month, last_day)
                return (start_date, end_date)
        except (ValueError, IndexError):
            pass
        
        # Default to current month
        start_date = date(today.year, today.month, 1)
        last_day = calendar.monthrange(today.year, today.month)[1]
        end_date = date(today.year, today.month, last_day)
        return (start_date, end_date)