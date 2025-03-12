APP_CONFIG = "prod"
wsgi_app = f"backend.server.app:create_app(app_config={APP_CONFIG!r})"
proc_name = "LiftJourney"

bind = "0.0.0.0:3000"
# workers = multiprocessing.cpu_count() * 2 + 1
threads = 1
workers = 1
# Gunicorn Debug Config
if APP_CONFIG.upper() is "debug".upper():
    reload = True
else:
    reload = False
