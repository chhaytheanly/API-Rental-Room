from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.config.session import get_db
from src.app.schema.query import QueryParameters
from src.app.schema.tenant import TenantCreate
from src.app.services.tenant import TenantService

tenant_router = APIRouter(prefix="/tenants", tags=["Tenants"])
@tenant_router.post("/")
def create_tenant(data: TenantCreate, db: Session = Depends(get_db)):
    try:
        tenant = TenantService.create_tenant(db, data)
        db.commit()
        db.refresh(tenant)
        return tenant
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
@tenant_router.get("/{tenant_id}")
def get_tenant(tenant_id: int, db: Session = Depends(get_db)):
    try:
        return TenantService.get_tenant_by_id(db, tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@tenant_router.get("/")
def get_tenants(query_params: QueryParameters = Depends(), db: Session = Depends(get_db)):
    return TenantService.get_all_tenants(db, query_params)


@tenant_router.delete("/{tenant_id}")
def remove_tenant_endpoint(tenant_id: int, db: Session = Depends(get_db)):
    try:
        tenant = TenantService.remove_tenant(db, tenant_id)
        db.commit()  
        db.refresh(tenant)  
        return tenant
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))