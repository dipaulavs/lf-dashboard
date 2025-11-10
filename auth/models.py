"""
Models de usuário para autenticação
"""
from datetime import datetime
from typing import Optional, Dict, Any

class UserModel:
    """
    Classe para gerenciar usuários OAuth no banco de dados
    """

    def __init__(self, db):
        """
        Args:
            db: Instância LeadsDatabase
        """
        self.db = db
        self._criar_tabela_users()

    def _criar_tabela_users(self):
        """Cria tabela de usuários se não existir"""
        conn = self.db._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                google_id TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                picture TEXT,
                access_token TEXT,
                refresh_token TEXT,
                token_expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)

        # Índices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_google_id ON users(google_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_email ON users(email)")

        conn.commit()
        conn.close()

    def criar_ou_atualizar(self, user_info: Dict[str, Any], token: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria novo usuário ou atualiza existente

        Args:
            user_info: Dados do usuário do Google (sub, email, name, picture)
            token: Token OAuth (access_token, refresh_token, expires_at)

        Returns:
            Dict com success e user_id
        """
        conn = self.db._get_connection()
        cursor = conn.cursor()

        google_id = user_info['sub']
        email = user_info['email']
        name = user_info.get('name', '')
        picture = user_info.get('picture', '')

        access_token = token.get('access_token')
        refresh_token = token.get('refresh_token')
        expires_at = token.get('expires_at')

        now = datetime.now().isoformat()

        try:
            # Tenta atualizar
            cursor.execute("""
                UPDATE users
                SET name = ?, picture = ?, access_token = ?,
                    refresh_token = COALESCE(?, refresh_token),
                    token_expires_at = ?, last_login = ?
                WHERE google_id = ?
            """, (name, picture, access_token, refresh_token, expires_at, now, google_id))

            if cursor.rowcount == 0:
                # Se não atualizou, cria novo
                cursor.execute("""
                    INSERT INTO users
                    (google_id, email, name, picture, access_token, refresh_token, token_expires_at, created_at, last_login)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (google_id, email, name, picture, access_token, refresh_token, expires_at, now, now))

                user_id = cursor.lastrowid
            else:
                # Busca ID do usuário atualizado
                cursor.execute("SELECT id FROM users WHERE google_id = ?", (google_id,))
                user_id = cursor.fetchone()['id']

            conn.commit()

            return {
                'success': True,
                'user_id': user_id
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            conn.close()

    def buscar_por_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Busca usuário por email"""
        conn = self.db._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        conn.close()
        return dict(user) if user else None

    def buscar_por_google_id(self, google_id: str) -> Optional[Dict[str, Any]]:
        """Busca usuário por Google ID"""
        conn = self.db._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE google_id = ?", (google_id,))
        user = cursor.fetchone()

        conn.close()
        return dict(user) if user else None

    def listar_todos(self) -> list:
        """Lista todos os usuários"""
        conn = self.db._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, google_id, email, name, picture, created_at, last_login
            FROM users
            ORDER BY last_login DESC
        """)

        users = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return users
