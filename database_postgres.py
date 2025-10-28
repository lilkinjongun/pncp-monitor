"""Módulo de banco de dados com suporte a PostgreSQL (Supabase)"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        """Inicializar conexão com PostgreSQL"""
        self.database_url = os.getenv('DATABASE_URL')
        
        if not self.database_url:
            raise ValueError("DATABASE_URL não configurada!")
        
        try:
            self.conn = psycopg2.connect(self.database_url)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            logger.info(f"Conectado ao banco de dados PostgreSQL")
            self._criar_tabelas()
        except Exception as e:
            logger.error(f"Erro ao conectar: {e}")
            raise

    def _criar_tabelas(self):
        """Criar tabelas se não existirem"""
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS contratacoes (
                    id SERIAL PRIMARY KEY,
                    numero_compra VARCHAR(50) NOT NULL,
                    ano_compra INTEGER NOT NULL,
                    objeto TEXT NOT NULL,
                    valor_estimado DECIMAL(15, 2),
                    modalidade_codigo INTEGER,
                    modalidade_nome VARCHAR(100),
                    data_publicacao TIMESTAMP,
                    situacao VARCHAR(50),
                    link_pncp TEXT,
                    notificado BOOLEAN DEFAULT FALSE,
                    data_insercao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(numero_compra, ano_compra)
                )
            ''')
            self.conn.commit()
            logger.info("Tabelas criadas/verificadas com sucesso")
        except Exception as e:
            logger.error(f"Erro ao criar tabelas: {e}")
            self.conn.rollback()

    def inserir_contratacao(self, contratacao):
        """Inserir uma contratação"""
        try:
            self.cursor.execute('''
                INSERT INTO contratacoes 
                (numero_compra, ano_compra, objeto, valor_estimado, modalidade_codigo,
                 modalidade_nome, data_publicacao, situacao, link_pncp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (numero_compra, ano_compra) DO NOTHING
            ''', (
                contratacao['numero_compra'],
                contratacao['ano_compra'],
                contratacao['objeto'],
                contratacao['valor_estimado'],
                contratacao['modalidade_codigo'],
                contratacao['modalidade_nome'],
                contratacao['data_publicacao'],
                contratacao['situacao'],
                contratacao['link_pncp']
            ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Erro ao inserir: {e}")
            self.conn.rollback()
            return False

    def buscar_contratacoes(self, limite=50, offset=0):
        """Buscar contratações"""
        try:
            self.cursor.execute('''
                SELECT * FROM contratacoes
                ORDER BY data_publicacao DESC
                LIMIT %s OFFSET %s
            ''', (limite, offset))
            
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Erro ao buscar: {e}")
            return []

    def contar_contratacoes(self):
        """Contar total de contratações"""
        try:
            self.cursor.execute('SELECT COUNT(*) as total FROM contratacoes')
            result = self.cursor.fetchone()
            return result['total'] if result else 0
        except Exception as e:
            logger.error(f"Erro ao contar: {e}")
            return 0

    def obter_estatisticas(self):
        """Obter estatísticas gerais"""
        try:
            # Total e valor
            self.cursor.execute('''
                SELECT 
                    COUNT(*) as total_contratacoes,
                    COALESCE(SUM(valor_estimado), 0) as valor_total_estimado,
                    MAX(data_publicacao) as ultima_atualizacao
                FROM contratacoes
            ''')
            stats = dict(self.cursor.fetchone())
            
            # Por modalidade
            self.cursor.execute('''
                SELECT 
                    modalidade_nome,
                    COUNT(*) as quantidade
                FROM contratacoes
                GROUP BY modalidade_nome
                ORDER BY quantidade DESC
            ''')
            
            por_modalidade = [dict(row) for row in self.cursor.fetchall()]
            stats['por_modalidade'] = por_modalidade
            
            return stats
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {
                'total_contratacoes': 0,
                'valor_total_estimado': 0,
                'ultima_atualizacao': None,
                'por_modalidade': []
            }

    def marcar_notificado(self, numero_compra, ano_compra):
        """Marcar contratação como notificada"""
        try:
            self.cursor.execute('''
                UPDATE contratacoes
                SET notificado = TRUE
                WHERE numero_compra = %s AND ano_compra = %s
            ''', (numero_compra, ano_compra))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Erro ao marcar notificado: {e}")
            self.conn.rollback()
            return False

    def fechar(self):
        """Fechar conexão"""
        try:
            self.cursor.close()
            self.conn.close()
            logger.info("Conexão com banco de dados fechada")
        except Exception as e:
            logger.error(f"Erro ao fechar: {e}")

