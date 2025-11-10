"""
Decoradores de autenticação
"""
from functools import wraps
from flask import session, redirect, url_for, jsonify, request

def login_required(f):
    """
    Decorator para proteger rotas que requerem autenticação

    Usage:
        @app.route('/dashboard')
        @login_required
        def dashboard():
            return render_template('dashboard.html')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verifica se usuário está na sessão
        if 'user' not in session:
            # Se for requisição API, retorna JSON
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Não autenticado'}), 401

            # Se for página web, redireciona para login
            return redirect(url_for('login'))

        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """
    Decorator para rotas que requerem permissão de admin

    Usage:
        @app.route('/admin')
        @admin_required
        def admin_panel():
            return render_template('admin.html')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))

        # Verifica se usuário é admin (pode expandir lógica depois)
        user = session['user']
        admin_emails = [
            'felipidipaula@gmail.com',  # Adicione emails de admins aqui
        ]

        if user.get('email') not in admin_emails:
            return jsonify({'error': 'Permissão negada'}), 403

        return f(*args, **kwargs)

    return decorated_function
