from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.application.services.report_service import ReportService
from app.core.deps import get_current_user, get_db
from app.presentation.schemas.report import (
    DashboardResponse,
    SalesReportFilters,
    SalesReportResponse,
)
