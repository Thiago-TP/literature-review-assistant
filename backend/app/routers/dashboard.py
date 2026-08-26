from __future__ import annotations

from fastapi import APIRouter

from app.deps import SessionDep, get_project_or_404
from app.schemas import DashboardStats
from app.services.dashboard import compute_dashboard_stats

router = APIRouter(prefix="/api/projects/{project_id}/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardStats)
def get_dashboard(project_id: int, session: SessionDep) -> DashboardStats:
    get_project_or_404(project_id, session)
    return compute_dashboard_stats(session, project_id)
