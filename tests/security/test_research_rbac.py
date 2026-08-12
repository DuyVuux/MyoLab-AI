from research_rbac import authorize,require
def test_admin(): assert authorize('ADMIN','audit')
def test_viewer(): assert authorize('VIEWER','read') and not authorize('VIEWER','review')
def test_unknown(): assert not authorize('UNKNOWN','read')
def test_require():
 try: require('VIEWER','override'); assert False
 except PermissionError: pass
