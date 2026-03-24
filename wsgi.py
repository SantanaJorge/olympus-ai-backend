"""
WSGI entrypoint for production (e.g. gunicorn on Cloud Run).
"""

from dotenv import load_dotenv

from tools.env_bootstrap import strip_secret_env_vars

load_dotenv()
strip_secret_env_vars()

from server.server import Server

import agents  # noqa: F401  # Triggers agent auto-registration

server = Server.get_instance()
app = server.app
