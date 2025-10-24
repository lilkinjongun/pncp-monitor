"""API Flask para o sistema PNCP Monitor"""

import os
import sys
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent))

from monitor import PNCPMonitor
from database import Database

app = Flask(__name__)
CORS(app)

# Configurações
CODIGO_IBGE = "3304706"
NOME_MUNICIPIO = "Santo Antônio de Pádua - RJ"

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Retorna estatísticas gerais"""
    try:
        db = Database()
        stats = db.obter_estatisticas()
        db.fechar()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contratacoes', methods=['GET'])
def get_contratacoes():
    """Retorna lista de contratações"""
    try:
        limite = request.args.get('limite', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        db = Database()
        contratacoes = db.buscar_contratacoes(limite=limite, offset=offset)
        total = db.contar_contratacoes()
        db.fechar()
        
        return jsonify({
            'total': total,
            'limite': limite,
            'offset': offset,
            'contratacoes': contratacoes
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/monitor', methods=['POST'])
def run_monitor():
    """Executa monitoramento"""
    try:
        monitor = PNCPMonitor(CODIGO_IBGE, NOME_MUNICIPIO)
        resultado = monitor.executar_monitoramento(dias_retroativos=7)
        monitor.fechar()
        
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e), 'sucesso': False}), 500

@app.route('/api/monitor/auto', methods=['POST'])
def run_monitor_auto():
    """Executa monitoramento automático (para cron)"""
    try:
        # Verificar token
        token = request.headers.get('X-Cron-Token')
        if token != os.getenv('CRON_TOKEN', 'default-token'):
            return jsonify({'error': 'Unauthorized'}), 401
        
        monitor = PNCPMonitor(CODIGO_IBGE, NOME_MUNICIPIO)
        resultado = monitor.executar_monitoramento(dias_retroativos=7)
        monitor.fechar()
        
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e), 'sucesso': False}), 500

@app.route('/', methods=['GET'])
def index():
    """Página inicial da API"""
    return jsonify({
        'nome': 'PNCP Monitor API',
        'municipio': NOME_MUNICIPIO,
        'endpoints': {
            'GET /health': 'Health check',
            'GET /api/stats': 'Estatísticas gerais',
            'GET /api/contratacoes': 'Lista de contratações',
            'POST /api/monitor': 'Executar monitoramento',
            'POST /api/monitor/auto': 'Executar monitoramento (cron)'
        }
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

