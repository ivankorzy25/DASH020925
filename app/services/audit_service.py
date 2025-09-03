from sqlalchemy.orm import Session
from app.models import AuditLog
import datetime
import json
from typing import Optional, List

def audit_log(
    db: Session,
    entity: str,
    entity_id: int,
    action: str,
    payload: dict,
    actor: str
) -> AuditLog:
    """Create an audit log entry"""
    
    audit_entry = AuditLog(
        entity=entity,
        entity_id=entity_id,
        action=action,
        payload_json=json.dumps(payload),
        actor=actor,
        created_at=datetime.datetime.now()
    )
    
    db.add(audit_entry)
    db.commit()
    
    return audit_entry

def get_audit_logs(
    db: Session,
    entity: Optional[str] = None,
    entity_id: Optional[int] = None,
    action: Optional[str] = None,
    actor: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[AuditLog]:
    """Get audit logs with optional filtering"""
    
    query = db.query(AuditLog)
    
    if entity:
        query = query.filter(AuditLog.entity == entity)
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if actor:
        query = query.filter(AuditLog.actor == actor)
    
    return query.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset).all()
