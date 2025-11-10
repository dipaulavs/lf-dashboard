"""
Módulo de autenticação OAuth Google
"""
from .google_oauth import init_oauth
from .decorators import login_required, admin_required
from .models import UserModel

__all__ = ['init_oauth', 'login_required', 'admin_required', 'UserModel']
