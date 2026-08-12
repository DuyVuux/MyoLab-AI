ROLE_PERMISSIONS={'ADMIN':{'read','review','override','reprocess','finalize','audit'},'REVIEWER':{'read','review','override','reprocess','finalize'},'VIEWER':{'read'}, 'TECHNICAL_REVIEWER':{'read','review','override','reprocess'}}
def authorize(role,permission): return permission in ROLE_PERMISSIONS.get(role,set())
def require(role,permission):
    if not authorize(role,permission): raise PermissionError('RBAC_FORBIDDEN')
