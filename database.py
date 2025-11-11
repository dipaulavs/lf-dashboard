"""
Sistema de Banco de Dados para Leads
Gerencia score, histórico e agendamentos
"""
import sqlite3
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path

# Fuso horário de Brasília (UTC-3)
BRASILIA_TZ = timezone(timedelta(hours=-3))

def now_brasilia():
    """Retorna datetime atual no horário de Brasília (sem timezone para evitar conversão no frontend)"""
    # Retorna datetime "naive" no horário de Brasília (sem info de timezone)
    return datetime.now(BRASILIA_TZ).replace(tzinfo=None)

class LeadsDatabase:
    def __init__(self, db_path: str = "data/dashboard.db"):
        self.db_path = db_path
        self._criar_tabelas()

    def _get_connection(self):
        """Cria conexão com SQLite"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Retorna dicts
        return conn

    def _criar_tabelas(self):
        """Cria estrutura do banco de dados"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Tabela principal de leads
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                whatsapp TEXT UNIQUE NOT NULL,
                nome TEXT NOT NULL,
                imovel_id INTEGER,
                score INTEGER CHECK(score >= 0 AND score <= 100) DEFAULT 0,
                agendou_visita BOOLEAN DEFAULT 0,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Histórico de mudanças de score
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS score_historico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                whatsapp TEXT NOT NULL,
                score_anterior INTEGER,
                score_novo INTEGER,
                motivo TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (whatsapp) REFERENCES leads(whatsapp)
            )
        """)

        # Tabela de agendamentos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agendamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_cliente TEXT NOT NULL,
                whatsapp TEXT NOT NULL,
                imovel_id INTEGER NOT NULL,
                data_visita DATE NOT NULL,
                hora_visita TIME NOT NULL,
                status TEXT CHECK(status IN ('agendado', 'confirmado', 'realizado', 'cancelado')) DEFAULT 'agendado',
                observacoes TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabela de configurações (para observações da agenda)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracoes (
                chave TEXT PRIMARY KEY,
                valor TEXT,
                atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Índices para performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_whatsapp ON leads(whatsapp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_score ON leads(score)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_imovel ON leads(imovel_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agendou ON leads(agendou_visita)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agendamentos_data ON agendamentos(data_visita)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agendamentos_status ON agendamentos(status)")

        conn.commit()
        conn.close()

    def registrar_lead(self, whatsapp: str, nome: str, imovel_id: int,
                      score: int, agendou_visita: bool) -> Dict[str, Any]:
        """
        Registra ou atualiza lead no sistema

        Args:
            whatsapp: Número WhatsApp (apenas dígitos)
            nome: Nome do cliente
            imovel_id: ID do imóvel de interesse
            score: Score de 0 a 100
            agendou_visita: True se marcou visita

        Returns:
            Dict com success, lead_id, e acao (created/updated)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Validações
        if not whatsapp or not nome:
            return {"success": False, "error": "whatsapp e nome são obrigatórios"}

        if score < 0 or score > 100:
            return {"success": False, "error": "score deve estar entre 0 e 100"}

        # Verifica se lead já existe
        cursor.execute("SELECT id, score FROM leads WHERE whatsapp = ?", (whatsapp,))
        lead_existente = cursor.fetchone()

        timestamp = now_brasilia().isoformat()

        if lead_existente:
            # Atualiza lead existente
            score_anterior = lead_existente['score']
            lead_id = lead_existente['id']

            cursor.execute("""
                UPDATE leads
                SET nome = ?, imovel_id = ?, score = ?,
                    agendou_visita = ?, atualizado_em = ?
                WHERE whatsapp = ?
            """, (nome, imovel_id, score, agendou_visita, timestamp, whatsapp))

            # Registra histórico se score mudou
            if score_anterior != score:
                motivo = f"Score atualizado de {score_anterior} para {score}"
                cursor.execute("""
                    INSERT INTO score_historico
                    (whatsapp, score_anterior, score_novo, motivo)
                    VALUES (?, ?, ?, ?)
                """, (whatsapp, score_anterior, score, motivo))

            acao = "updated"
        else:
            # Cria novo lead
            cursor.execute("""
                INSERT INTO leads
                (whatsapp, nome, imovel_id, score, agendou_visita, criado_em, atualizado_em)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (whatsapp, nome, imovel_id, score, agendou_visita, timestamp, timestamp))

            lead_id = cursor.lastrowid

            # Registra no histórico
            cursor.execute("""
                INSERT INTO score_historico
                (whatsapp, score_anterior, score_novo, motivo)
                VALUES (?, ?, ?, ?)
            """, (whatsapp, 0, score, "Lead criado"))

            acao = "created"

        conn.commit()
        conn.close()

        return {
            "success": True,
            "lead_id": lead_id,
            "acao": acao,
            "score": score
        }

    def listar_leads(self, filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Lista leads com filtros opcionais

        Filtros disponíveis:
            - score_min: Score mínimo
            - score_max: Score máximo
            - imovel_id: ID do imóvel
            - agendou_visita: True/False
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM leads WHERE 1=1"
        params = []

        if filtros:
            if 'score_min' in filtros:
                query += " AND score >= ?"
                params.append(filtros['score_min'])

            if 'score_max' in filtros:
                query += " AND score <= ?"
                params.append(filtros['score_max'])

            if 'imovel_id' in filtros:
                query += " AND imovel_id = ?"
                params.append(filtros['imovel_id'])

            if 'agendou_visita' in filtros:
                query += " AND agendou_visita = ?"
                params.append(1 if filtros['agendou_visita'] else 0)

        query += " ORDER BY score DESC, atualizado_em DESC"

        cursor.execute(query, params)
        leads = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return leads

    def buscar_lead(self, whatsapp: str) -> Optional[Dict[str, Any]]:
        """Busca lead específico por WhatsApp"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM leads WHERE whatsapp = ?", (whatsapp,))
        lead = cursor.fetchone()

        conn.close()
        return dict(lead) if lead else None

    def obter_historico(self, whatsapp: str) -> List[Dict[str, Any]]:
        """Obtém histórico de score de um lead"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM score_historico
            WHERE whatsapp = ?
            ORDER BY timestamp DESC
        """, (whatsapp,))

        historico = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return historico

    def obter_estatisticas(self) -> Dict[str, Any]:
        """Retorna estatísticas agregadas para gráficos"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Total de leads
        cursor.execute("SELECT COUNT(*) as total FROM leads")
        total = cursor.fetchone()['total']

        # Distribuição por score (frio/morno/quente)
        cursor.execute("""
            SELECT
                COUNT(CASE WHEN score >= 0 AND score <= 30 THEN 1 END) as frios,
                COUNT(CASE WHEN score >= 31 AND score <= 60 THEN 1 END) as mornos,
                COUNT(CASE WHEN score >= 61 AND score <= 100 THEN 1 END) as quentes
            FROM leads
        """)
        distribuicao = dict(cursor.fetchone())

        # Leads por imóvel
        cursor.execute("""
            SELECT imovel_id, COUNT(*) as count
            FROM leads
            WHERE imovel_id IS NOT NULL
            GROUP BY imovel_id
            ORDER BY count DESC
        """)
        por_imovel = [dict(row) for row in cursor.fetchall()]

        # Taxa de agendamento
        cursor.execute("""
            SELECT
                COUNT(*) as total_agendamentos,
                ROUND(CAST(COUNT(*) AS FLOAT) / ? * 100, 2) as taxa_agendamento
            FROM leads
            WHERE agendou_visita = 1
        """, (total if total > 0 else 1,))
        agendamentos = dict(cursor.fetchone())

        # Score médio
        cursor.execute("SELECT AVG(score) as score_medio FROM leads")
        score_medio = cursor.fetchone()['score_medio'] or 0

        conn.close()

        return {
            "total_leads": total,
            "distribuicao": distribuicao,
            "por_imovel": por_imovel,
            "agendamentos": agendamentos,
            "score_medio": round(score_medio, 2)
        }

    # ==================== MÉTODOS DE AGENDAMENTOS ====================

    def criar_agendamento(self, nome_cliente: str, whatsapp: str, imovel_id: int,
                         data_visita: str, hora_visita: str, observacoes: str = None,
                         status: str = 'agendado') -> Dict[str, Any]:
        """Cria novo agendamento de visita"""
        conn = self._get_connection()
        cursor = conn.cursor()

        timestamp = now_brasilia().isoformat()

        try:
            cursor.execute("""
                INSERT INTO agendamentos
                (nome_cliente, whatsapp, imovel_id, data_visita, hora_visita, status, observacoes, criado_em, atualizado_em)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (nome_cliente, whatsapp, imovel_id, data_visita, hora_visita, status, observacoes, timestamp, timestamp))

            agendamento_id = cursor.lastrowid
            conn.commit()

            return {
                "success": True,
                "agendamento_id": agendamento_id,
                "message": "Agendamento criado com sucesso"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            conn.close()

    def listar_agendamentos(self, filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Lista agendamentos com filtros opcionais"""
        conn = self._get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM agendamentos WHERE 1=1"
        params = []

        if filtros:
            if 'status' in filtros:
                query += " AND status = ?"
                params.append(filtros['status'])

            if 'data_inicio' in filtros:
                query += " AND data_visita >= ?"
                params.append(filtros['data_inicio'])

            if 'data_fim' in filtros:
                query += " AND data_visita <= ?"
                params.append(filtros['data_fim'])

            if 'imovel_id' in filtros:
                query += " AND imovel_id = ?"
                params.append(filtros['imovel_id'])

        query += " ORDER BY data_visita ASC, hora_visita ASC"

        cursor.execute(query, params)
        agendamentos = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return agendamentos

    def atualizar_agendamento(self, agendamento_id: int, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Atualiza agendamento existente"""
        conn = self._get_connection()
        cursor = conn.cursor()

        campos_atualizaveis = ['nome_cliente', 'whatsapp', 'imovel_id', 'data_visita',
                               'hora_visita', 'status', 'observacoes']

        updates = []
        params = []

        for campo in campos_atualizaveis:
            if campo in dados:
                updates.append(f"{campo} = ?")
                params.append(dados[campo])

        if not updates:
            return {"success": False, "error": "Nenhum campo para atualizar"}

        updates.append("atualizado_em = ?")
        params.append(now_brasilia().isoformat())
        params.append(agendamento_id)

        query = f"UPDATE agendamentos SET {', '.join(updates)} WHERE id = ?"

        try:
            cursor.execute(query, params)
            conn.commit()

            if cursor.rowcount == 0:
                return {"success": False, "error": "Agendamento não encontrado"}

            return {
                "success": True,
                "message": "Agendamento atualizado com sucesso"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            conn.close()

    def deletar_agendamento(self, agendamento_id: int) -> Dict[str, Any]:
        """Deleta agendamento"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM agendamentos WHERE id = ?", (agendamento_id,))
            conn.commit()

            if cursor.rowcount == 0:
                return {"success": False, "error": "Agendamento não encontrado"}

            return {
                "success": True,
                "message": "Agendamento deletado com sucesso"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            conn.close()

    def obter_estatisticas_agenda(self) -> Dict[str, Any]:
        """Retorna estatísticas da agenda"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Total de visitas
        cursor.execute("SELECT COUNT(*) as total FROM agendamentos")
        total = cursor.fetchone()['total']

        # Visitas hoje
        hoje = now_brasilia().date().isoformat()
        cursor.execute("SELECT COUNT(*) as hoje FROM agendamentos WHERE data_visita = ?", (hoje,))
        hoje_count = cursor.fetchone()['hoje']

        # Próximos 7 dias
        from datetime import timedelta
        proximos_7 = (now_brasilia().date() + timedelta(days=7)).isoformat()
        cursor.execute("""
            SELECT COUNT(*) as proximos7
            FROM agendamentos
            WHERE data_visita BETWEEN ? AND ?
        """, (hoje, proximos_7))
        proximos7_count = cursor.fetchone()['proximos7']

        # Por status
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM agendamentos
            GROUP BY status
        """)
        por_status = {row['status']: row['count'] for row in cursor.fetchall()}

        conn.close()

        return {
            "total": total,
            "hoje": hoje_count,
            "proximos_7_dias": proximos7_count,
            "por_status": por_status
        }

    def salvar_configuracao(self, chave: str, valor: str) -> Dict[str, Any]:
        """Salva configuração (ex: observações da agenda)"""
        conn = self._get_connection()
        cursor = conn.cursor()

        timestamp = now_brasilia().isoformat()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO configuracoes (chave, valor, atualizado_em)
                VALUES (?, ?, ?)
            """, (chave, valor, timestamp))

            conn.commit()

            return {
                "success": True,
                "message": "Configuração salva com sucesso"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            conn.close()

    def obter_configuracao(self, chave: str) -> Optional[str]:
        """Obtém configuração salva"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT valor FROM configuracoes WHERE chave = ?", (chave,))
        resultado = cursor.fetchone()

        conn.close()
        return resultado['valor'] if resultado else None

    def deletar_lead(self, whatsapp: str) -> Dict[str, Any]:
        """Deleta um lead e seu histórico"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Verificar se lead existe
            cursor.execute("SELECT id FROM leads WHERE whatsapp = ?", (whatsapp,))
            if not cursor.fetchone():
                conn.close()
                return {
                    "success": False,
                    "error": "Lead não encontrado"
                }

            # Deletar histórico primeiro (foreign key)
            cursor.execute("DELETE FROM score_historico WHERE whatsapp = ?", (whatsapp,))

            # Deletar lead
            cursor.execute("DELETE FROM leads WHERE whatsapp = ?", (whatsapp,))

            conn.commit()
            conn.close()

            return {
                "success": True,
                "message": "Lead deletado com sucesso"
            }

        except Exception as e:
            conn.close()
            return {
                "success": False,
                "error": str(e)
            }
