from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.analytics import analytics_service
from app.schemas.analytics import AnalyticsResponse

router = APIRouter(tags=["Analytics"])


@router.get("/analytics", response_model=AnalyticsResponse)
def get_analytics(db: Session = Depends(get_db)):
    return analytics_service.get_system_analytics(db)


@router.get("/suggestions", response_model=List[str])
def get_query_suggestions(db: Session = Depends(get_db)):
    return analytics_service.get_query_suggestions(db)
