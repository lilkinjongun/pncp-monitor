"""
Módulo de gerenciamento de banco de dados
Armazena contratações e controla notificações
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class Database:
    """Gerenciador de banco de dados SQLite"""
    
    def __init__(self, db_path: str = "pncp_monitor.db"):
        """
        Inicializa o banco de dados
        
        Args:
            db_path: Caminho para o arquivo do banco de dados
        """
        self.db_path = db_path
        self.conn = None
        self._conectar()
        self._criar_tabelas()
    
    def _conectar(self):
        """Conecta ao banco de dados"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Permite acesso por nome de coluna
            logger.info(f"Conectado ao banco de dados: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Erro ao conectar ao banco de dados: {e}")
            raise
    
    def _criar_tabelas(self):
        """Cria as tabelas necessárias"""
        cursor = self.conn.cursor()
        
        # Tabela de contratações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contratacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_compra TEXT,
                ano_compra INTEGER,
                sequencial_compra INTEGER,
                codigo_ibge TEXT,
                cnpj_orgao TEXT,
                objeto TEXT,
                valor_estimado REAL,
                valor_homologado REAL,
                modalidade_codigo INTEGER,
                modalidade_nome TEXT,
                data_publicacao TEXT,
                situacao TEXT,
                orgao_nome TEXT,
                link_pncp TEXT,
                dados_completos TEXT,
                data_captura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notificado BOOLEAN DEFAULT 0,
                data_notificacao TIMESTAMP,
                UNIQUE(cnpj_orgao, ano_compra, sequencial_compra)
            )
        """)
        
        # Tabela de configurações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracoes (
                chave TEXT PRIMARY KEY,
                valor TEXT,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de log de execuções
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS log_execucoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_execucao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                contratacoes_encontradas INTEGER,
                contratacoes_novas INTEGER,
                sucesso BOOLEAN,
                mensagem TEXT
            )
        """)
        
        # Índices para melhorar performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_data_publicacao 
            ON contratacoes(data_publicacao)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_notificado 
            ON contratacoes(notificado)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_modalidade 
            ON contratacoes(modalidade_codigo)
        """)
        
        self.conn.commit()
        logger.info("Tabelas criadas/verificadas com sucesso")
    
    def salvar_contratacao(self, contratacao: Dict) -> bool:
        """
        Salva uma contratação no banco de dados
        
        Args:
            contratacao: Dados da contratação
            
        Returns:
            True se foi uma nova contratação, False se já existia
        """
        cursor = self.conn.cursor()
        
        try:
            # Extrair dados principais
            cnpj_orgao = contratacao.get('orgaoEntidade', {}).get('cnpj', '')
            ano_compra = contratacao.get('anoCompra')
            sequencial_compra = contratacao.get('sequencialCompra')
            
            # Verificar se já existe
            cursor.execute("""
                SELECT id FROM contratacoes 
                WHERE cnpj_orgao = ? AND ano_compra = ? AND sequencial_compra = ?
            """, (cnpj_orgao, ano_compra, sequencial_compra))
            
            existe = cursor.fetchone()
            
            if existe:
                logger.debug(f"Contratação já existe: {ano_compra}/{sequencial_compra}")
                return False
            
            # Inserir nova contratação
            cursor.execute("""
                INSERT INTO contratacoes (
                    numero_compra, ano_compra, sequencial_compra,
                    codigo_ibge, cnpj_orgao, objeto,
                    valor_estimado, valor_homologado,
                    modalidade_codigo, modalidade_nome,
                    data_publicacao, situacao, orgao_nome,
                    link_pncp, dados_completos
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                contratacao.get('numeroCompra'),
                ano_compra,
                sequencial_compra,
                contratacao.get('codigoMunicipioIbge'),
                cnpj_orgao,
                contratacao.get('objetoCompra'),
                contratacao.get('valorTotalEstimado'),
                contratacao.get('valorTotalHomologado'),
                contratacao.get('_modalidade_codigo'),
                contratacao.get('_modalidade_nome'),
                contratacao.get('dataPublicacaoPncp'),
                contratacao.get('situacaoCompra'),
                contratacao.get('orgaoEntidade', {}).get('razaoSocial'),
                self._gerar_link_pncp(contratacao),
                json.dumps(contratacao, ensure_ascii=False)
            ))
            
            self.conn.commit()
            logger.info(f"Nova contratação salva: {ano_compra}/{sequencial_compra}")
            return True
            
        except sqlite3.IntegrityError:
            logger.debug("Contratação duplicada (ignorada)")
            return False
        except Exception as e:
            logger.error(f"Erro ao salvar contratação: {e}")
            self.conn.rollback()
            return False
    
    def salvar_contratacoes(self, contratacoes: List[Dict]) -> int:
        """
        Salva múltiplas contratações
        
        Args:
            contratacoes: Lista de contratações
            
        Returns:
            Número de novas contratações salvas
        """
        novas = 0
        for contratacao in contratacoes:
            if self.salvar_contratacao(contratacao):
                novas += 1
        return novas
    
    def buscar_contratacoes_nao_notificadas(self) -> List[Dict]:
        """
        Busca contratações que ainda não foram notificadas
        
        Returns:
            Lista de contratações não notificadas
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM contratacoes 
            WHERE notificado = 0 
            ORDER BY data_publicacao DESC
        """)
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def marcar_como_notificado(self, contratacao_id: int):
        """
        Marca uma contratação como notificada
        
        Args:
            contratacao_id: ID da contratação
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE contratacoes 
            SET notificado = 1, data_notificacao = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (contratacao_id,))
        self.conn.commit()
    
    def buscar_contratacoes(
        self,
        limite: int = 100,
        offset: int = 0,
        modalidade: Optional[int] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None
    ) -> List[Dict]:
        """
        Busca contratações com filtros
        
        Args:
            limite: Número máximo de registros
            offset: Deslocamento para paginação
            modalidade: Filtrar por código de modalidade
            data_inicio: Data inicial (formato ISO)
            data_fim: Data final (formato ISO)
            
        Returns:
            Lista de contratações
        """
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM contratacoes WHERE 1=1"
        params = []
        
        if modalidade is not None:
            query += " AND modalidade_codigo = ?"
            params.append(modalidade)
        
        if data_inicio:
            query += " AND data_publicacao >= ?"
            params.append(data_inicio)
        
        if data_fim:
            query += " AND data_publicacao <= ?"
            params.append(data_fim)
        
        query += " ORDER BY data_publicacao DESC LIMIT ? OFFSET ?"
        params.extend([limite, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def contar_contratacoes(
        self,
        modalidade: Optional[int] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None
    ) -> int:
        """
        Conta o total de contratações com filtros
        
        Args:
            modalidade: Filtrar por código de modalidade
            data_inicio: Data inicial (formato ISO)
            data_fim: Data final (formato ISO)
            
        Returns:
            Número total de contratações
        """
        cursor = self.conn.cursor()
        
        query = "SELECT COUNT(*) as total FROM contratacoes WHERE 1=1"
        params = []
        
        if modalidade is not None:
            query += " AND modalidade_codigo = ?"
            params.append(modalidade)
        
        if data_inicio:
            query += " AND data_publicacao >= ?"
            params.append(data_inicio)
        
        if data_fim:
            query += " AND data_publicacao <= ?"
            params.append(data_fim)
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        return result['total'] if result else 0
    
    def obter_estatisticas(self) -> Dict:
        """
        Obtém estatísticas gerais do banco de dados
        
        Returns:
            Dicionário com estatísticas
        """
        cursor = self.conn.cursor()
        
        # Total de contratações
        cursor.execute("SELECT COUNT(*) as total FROM contratacoes")
        total = cursor.fetchone()['total']
        
        # Contratações por modalidade
        cursor.execute("""
            SELECT modalidade_nome, COUNT(*) as quantidade 
            FROM contratacoes 
            GROUP BY modalidade_nome 
            ORDER BY quantidade DESC
        """)
        por_modalidade = [dict(row) for row in cursor.fetchall()]
        
        # Valor total estimado
        cursor.execute("SELECT SUM(valor_estimado) as total FROM contratacoes")
        valor_total = cursor.fetchone()['total'] or 0
        
        # Última atualização
        cursor.execute("""
            SELECT MAX(data_captura) as ultima_atualizacao 
            FROM contratacoes
        """)
        ultima_atualizacao = cursor.fetchone()['ultima_atualizacao']
        
        return {
            'total_contratacoes': total,
            'por_modalidade': por_modalidade,
            'valor_total_estimado': valor_total,
            'ultima_atualizacao': ultima_atualizacao
        }
    
    def registrar_execucao(
        self,
        encontradas: int,
        novas: int,
        sucesso: bool,
        mensagem: str = ""
    ):
        """
        Registra uma execução do monitoramento
        
        Args:
            encontradas: Número de contratações encontradas
            novas: Número de contratações novas
            sucesso: Se a execução foi bem-sucedida
            mensagem: Mensagem adicional
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO log_execucoes (
                contratacoes_encontradas,
                contratacoes_novas,
                sucesso,
                mensagem
            ) VALUES (?, ?, ?, ?)
        """, (encontradas, novas, sucesso, mensagem))
        self.conn.commit()
    
    def _gerar_link_pncp(self, contratacao: Dict) -> str:
        """Gera o link para a contratação no portal PNCP"""
        cnpj = contratacao.get('orgaoEntidade', {}).get('cnpj', '')
        ano = contratacao.get('anoCompra', '')
        sequencial = contratacao.get('sequencialCompra', '')
        
        if cnpj and ano and sequencial:
            return f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{sequencial}"
        return "N/A"
    
    def fechar(self):
        """Fecha a conexão com o banco de dados"""
        if self.conn:
            self.conn.close()
            logger.info("Conexão com banco de dados fechada")
    
    def __enter__(self):
        """Suporte para context manager"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Suporte para context manager"""
        self.fechar()

