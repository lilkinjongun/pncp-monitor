#!/usr/bin/env python3
"""
Script de teste para API do PNCP
Busca contratações de Santo Antônio de Pádua - RJ
"""

import requests
import json
from datetime import datetime, timedelta

# Configurações
BASE_URL = "https://pncp.gov.br/api/consulta/v1"
CODIGO_IBGE_SANTO_ANTONIO_PADUA = "3304554"

# Calcular datas (últimos 90 dias)
data_final = datetime.now()
data_inicial = data_final - timedelta(days=90)

# Formatar datas no formato esperado pela API (YYYYMMDD)
data_inicial_str = data_inicial.strftime("%Y%m%d")
data_final_str = data_final.strftime("%Y%m%d")

print("=" * 80)
print("TESTE DA API DO PNCP")
print("=" * 80)
print(f"Município: Santo Antônio de Pádua - RJ")
print(f"Código IBGE: {CODIGO_IBGE_SANTO_ANTONIO_PADUA}")
print(f"Período: {data_inicial.strftime('%d/%m/%Y')} a {data_final.strftime('%d/%m/%Y')}")
print("=" * 80)
print()

# Montar URL da requisição
url = f"{BASE_URL}/contratacoes/publicacao"
params = {
    "dataInicial": data_inicial_str,
    "dataFinal": data_final_str,
    "codigoMunicipioIbge": CODIGO_IBGE_SANTO_ANTONIO_PADUA,
    "codigoModalidadeContratacao": "",  # Vazio para buscar todas as modalidades
    "pagina": 1,
    "tamanhoPagina": 10
}

print(f"URL: {url}")
print(f"Parâmetros: {json.dumps(params, indent=2)}")
print()
print("Fazendo requisição...")
print()

try:
    # Fazer requisição
    response = requests.get(url, params=params, timeout=30)
    
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        
        # Exibir informações sobre a resposta
        print("RESPOSTA RECEBIDA COM SUCESSO!")
        print("=" * 80)
        
        # Verificar estrutura da resposta
        if isinstance(data, dict):
            print(f"Tipo de resposta: Objeto (dict)")
            print(f"Chaves disponíveis: {list(data.keys())}")
            print()
            
            # Verificar se tem dados paginados
            if 'data' in data:
                contratacoes = data['data']
                total = data.get('totalElements', len(contratacoes))
                print(f"Total de contratações encontradas: {total}")
                print(f"Contratações nesta página: {len(contratacoes)}")
            else:
                contratacoes = data
                print(f"Total de contratações encontradas: {len(contratacoes) if isinstance(contratacoes, list) else 1}")
        elif isinstance(data, list):
            print(f"Tipo de resposta: Lista")
            contratacoes = data
            print(f"Total de contratações encontradas: {len(contratacoes)}")
        else:
            print(f"Tipo de resposta inesperado: {type(data)}")
            contratacoes = []
        
        print()
        print("=" * 80)
        
        # Exibir primeiras contratações
        if contratacoes and len(contratacoes) > 0:
            print("PRIMEIRAS CONTRATAÇÕES:")
            print("=" * 80)
            
            for i, contratacao in enumerate(contratacoes[:3], 1):
                print(f"\n{i}. CONTRATAÇÃO:")
                print("-" * 80)
                
                # Exibir campos principais
                campos_principais = [
                    'numeroCompra', 'anoCompra', 'sequencialCompra',
                    'objetoCompra', 'valorTotalEstimado', 'valorTotalHomologado',
                    'modalidadeNome', 'dataPublicacaoPncp', 'situacaoCompra',
                    'orgaoEntidade', 'unidadeOrgao'
                ]
                
                for campo in campos_principais:
                    if campo in contratacao:
                        valor = contratacao[campo]
                        if isinstance(valor, dict):
                            print(f"  {campo}:")
                            for k, v in valor.items():
                                print(f"    - {k}: {v}")
                        else:
                            print(f"  {campo}: {valor}")
                
                # Mostrar todas as chaves disponíveis
                print(f"\n  Todas as chaves: {list(contratacao.keys())}")
        else:
            print("Nenhuma contratação encontrada no período especificado.")
            print()
            print("Isso pode significar:")
            print("- O município não publicou contratações no período")
            print("- O código IBGE está incorreto")
            print("- O município ainda não utiliza o PNCP")
        
        print()
        print("=" * 80)
        
        # Salvar resposta completa em arquivo
        output_file = "/home/ubuntu/pncp_response.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\nResposta completa salva em: {output_file}")
        
    else:
        print(f"ERRO: Status code {response.status_code}")
        print(f"Resposta: {response.text}")
        
except requests.exceptions.Timeout:
    print("ERRO: Timeout na requisição (mais de 30 segundos)")
except requests.exceptions.RequestException as e:
    print(f"ERRO na requisição: {e}")
except json.JSONDecodeError as e:
    print(f"ERRO ao decodificar JSON: {e}")
    print(f"Resposta raw: {response.text[:500]}")
except Exception as e:
    print(f"ERRO inesperado: {e}")

print()
print("=" * 80)
print("FIM DO TESTE")
print("=" * 80)

