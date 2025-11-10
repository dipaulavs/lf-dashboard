"""
Configuração OAuth 2.0 com Google usando Authlib
"""
from authlib.integrations.flask_client import OAuth
from flask import Flask
import json
from pathlib import Path

def init_oauth(app: Flask):
    """
    Inicializa OAuth com credenciais Google

    Args:
        app: Instância Flask

    Returns:
        Cliente OAuth configurado para Google
    """
    # Carregar credenciais OAuth
    config_path = Path(__file__).parent.parent / 'config' / 'oauth_credentials.json'

    with open(config_path, 'r') as f:
        credentials = json.load(f)['web']

    # Configurar OAuth
    app.config['GOOGLE_CLIENT_ID'] = credentials['client_id']
    app.config['GOOGLE_CLIENT_SECRET'] = credentials['client_secret']

    oauth = OAuth(app)

    # Registrar provedor Google
    google = oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile',
            'prompt': 'select_account'  # Sempre pedir para escolher conta
        }
    )

    return google
