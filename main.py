"""
Flask Agents Server

Exposes agent tools via HTTP/REST endpoints.
"""

from dotenv import load_dotenv
load_dotenv()

from server.server import Server
import agents  # Importar dispara auto-discovery e registro declarativo de agentes


if __name__ == '__main__':
    # Obter servidor singleton e iniciar
    server = Server.get_instance()
    server.start(host='0.0.0.0', port=6000, debug=True)
