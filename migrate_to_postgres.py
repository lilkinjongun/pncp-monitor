"""Script para migrar dados de SQLite para PostgreSQL (Supabase)"""

import sqlite3
import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv

load_dotenv()

# Configurações
SQLITE_DB = 'pncp_monitor.db'
POSTGRES_URL = os.getenv('DATABASE_URL')  # Supabase fornece isso

if not POSTGRES_URL:
    print("❌ Erro: DATABASE_URL não configurada!")
    print("Configure a variável de ambiente DATABASE_URL com a URL do Supabase")
    exit(1)

print("🔄 Iniciando migração SQLite → PostgreSQL...")
print()

try:
    # Conectar ao SQLite
    print("📖 Lendo dados do SQLite...")
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    # Buscar dados
    sqlite_cursor.execute('SELECT * FROM contratacoes')
    contratacoes = sqlite_cursor.fetchall()
    print(f"✓ {len(contratacoes)} contratações encontradas")
    
    sqlite_conn.close()
    
    # Conectar ao PostgreSQL
    print("🔗 Conectando ao Supabase...")
    postgres_conn = psycopg2.connect(POSTGRES_URL)
    postgres_cursor = postgres_conn.cursor()
    
    # Criar tabela no PostgreSQL
    print("📋 Criando tabela no PostgreSQL...")
    postgres_cursor.execute('''
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
    postgres_conn.commit()
    print("✓ Tabela criada")
    
    # Inserir dados
    print("📤 Inserindo dados no PostgreSQL...")
    
    data_to_insert = []
    for row in contratacoes:
        data_to_insert.append((
            row['numero_compra'],
            row['ano_compra'],
            row['objeto'],
            row['valor_estimado'],
            row['modalidade_codigo'],
            row['modalidade_nome'],
            row['data_publicacao'],
            row['situacao'],
            row['link_pncp'],
            row['notificado'],
            row['data_insercao']
        ))
    
    insert_query = '''
        INSERT INTO contratacoes 
        (numero_compra, ano_compra, objeto, valor_estimado, modalidade_codigo, 
         modalidade_nome, data_publicacao, situacao, link_pncp, notificado, data_insercao)
        VALUES %s
        ON CONFLICT (numero_compra, ano_compra) DO NOTHING
    '''
    
    execute_values(postgres_cursor, insert_query, data_to_insert)
    postgres_conn.commit()
    print(f"✓ {len(data_to_insert)} registros inseridos")
    
    # Verificar
    postgres_cursor.execute('SELECT COUNT(*) FROM contratacoes')
    count = postgres_cursor.fetchone()[0]
    print(f"✓ Total no banco: {count}")
    
    postgres_cursor.close()
    postgres_conn.close()
    
    print()
    print("=" * 60)
    print("✅ Migração concluída com sucesso!")
    print("=" * 60)
    
except Exception as e:
    print(f"❌ Erro: {e}")
    exit(1)

