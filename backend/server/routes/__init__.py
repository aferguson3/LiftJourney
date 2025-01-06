from backend.server.routes.auth import login_bp
from backend.server.routes.database import database_bp
from backend.server.routes.mapping import mapping_bp
from backend.server.routes.service import service_bp
from backend.server.routes.status_codes import statues_bp

__all__ = ["mapping_bp", "database_bp", "service_bp", "statues_bp", "login_bp"]
