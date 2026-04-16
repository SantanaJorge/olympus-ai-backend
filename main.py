"""
Flask Agents Server

Exposes agent tools via HTTP/REST endpoints.
"""

import os

from dotenv import load_dotenv

from tools.env_bootstrap import get_environment, strip_secret_env_vars

load_dotenv()
strip_secret_env_vars()

from server.server import Server

import agents  # Import triggers agent auto-registration


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "6001"))
    environment = get_environment()
    debug = environment == "local"
    server = Server.get_instance()
    server.start(host="0.0.0.0", port=port, debug=debug)
