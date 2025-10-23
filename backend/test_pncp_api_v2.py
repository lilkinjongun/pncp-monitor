#!/usr/bin/env python3
"""
Script de teste para API do PNCP - Versão 2
Busca contratações de Santo Antônio de Pádua - RJ
Com código de modalidade válido
"""

import requests
import json
from datetime import datetime, timedelta

# Configurações
BASE_URL = "https://pncp.gov.br/api/consulta/v1"
CODIGO_IBGE_SANTO_ANTONIO_PADUA = "3304706"

# Modalidades a serem testadas (principais)
MODALIDADES = {
    6: "Pregão - Eletrônico",
    8: "Dispensa de Licitação",
    9: "Inexigibilidade",
    4: "Concorrência - Eletrônica"
}

# Calcular datas (últimos 180 dias para aumentar chances de encontrar dados)
data_final = datetime.now()
data_inicial = data_final - timedelta(days=180)

# Formatar datas no formato esperado pela API (YYYYMMDD)
data_inicial_str = data_inicial.strftime("%Y%m%d")
data_final_str = data_final.strftime("%Y%m%d")

print("=" * 80)
print("TESTE DA API DO PNCP - VERSÃO 2")
print("=" * 80)
print(f"Município: Santo Antônio de Pádua - RJ")
print(f"Código IBGE: {CODIGO_IBGE_SANTO_ANTONIO_PADUA}")
print(f"Período: {data_inicial.strftime('%d/%m/%Y')} a {data_final.strftime('%d/%m/%Y')}")
print("=" * 80)
print()

# Testar cada modalidade
total_contratacoes = 0
todas_contratacoes = []

for codigo_modalidade, nome_modalidade in MODALIDADES.items():
    print(f"\n{'=' * 80}")
    print(f"TESTANDO MODALIDADE: {nome_modalidade} (código {codigo_modalidade})")
    print("=" * 80)
    
    # Montar URL da requisição
    url = f"{BASE_URL}/contratacoes/publicacao"
    params = {
        "dataInicial": data_inicial_str,
        "dataFinal": data_final_str,
        "codigoMunicipioIbge": CODIGO_IBGE_SANTO_ANTONIO_PADUA,
        "codigoModalidadeContratacao": codigo_modalidade,
        "pagina": 1,
        "tamanhoPagina": 20
    }
    
    try:
        # Fazer requisição
        response = requests.get(url, params=params, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Verificar estrutura da resposta
            if isinstance(data, dict):
                if 'data' in data:
                    contratacoes = data['data']
                    total = data.get('totalElements', len(contratacoes))
                elif 'content' in data:
                    contratacoes = data['content']
                    total = data.get('totalElements', len(contratacoes))
                else:
                    # Tentar encontrar a lista de contratações
                    contratacoes = []
                    for key, value in data.items():
                        if isinstance(value, list) and len(value) > 0:
                            contratacoes = value
                            break
                    total = len(contratacoes)
            elif isinstance(data, list):
                contratacoes = data
                total = len(contratacoes)
            else:
                contratacoes = []
                total = 0
            
            print(f"✅ Contratações encontradas: {len(contratacoes)}")
            
            if len(contratacoes) > 0:
                total_contratacoes += len(contratacoes)
                todas_contratacoes.extend(contratacoes)
                
                print(f"\nPrimeiras contratações desta modalidade:")
                print("-" * 80)
                
                for i, contratacao in enumerate(contratacoes[:3], 1):
                    print(f"\n{i}. ", end="")
                    
                    # Tentar extrair informações principais
                    if 'objetoCompra' in contratacao:
                        print(f"Objeto: {contratacao['objetoCompra'][:80]}...")
                    elif 'objeto' in contratacao:
                        print(f"Objeto: {contratacao['objeto'][:80]}...")
                    
                    if 'valorTotalEstimado' in contratacao:
                        print(f"   Valor: R$ {contratacao['valorTotalEstimado']:,.2f}")
                    elif 'valorTotal' in contratacao:
                        print(f"   Valor: R$ {contratacao['valorTotal']:,.2f}")
                    
                    if 'dataPublicacaoPncp' in contratacao:
                        print(f"   Data: {contratacao['dataPublicacaoPncp']}")
                    elif 'dataPublicacao' in contratacao:
                        print(f"   Data: {contratacao['dataPublicacao']}")
            else:
                print("❌ Nenhuma contratação encontrada para esta modalidade.")
                
        elif response.status_code == 404:
            print("❌ Endpoint não encontrado (404)")
        elif response.status_code == 400:
            print(f"❌ Erro 400: {response.text}")
        else:
            print(f"❌ Erro {response.status_code}: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print("❌ Timeout na requisição")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

print(f"\n\n{'=' * 80}")
print("RESUMO FINAL")
print("=" * 80)
print(f"Total de contratações encontradas: {total_contratacoes}")

if total_contratacoes > 0:
    # Salvar todas as contratações em arquivo
    output_file = "/home/ubuntu/pncp_contratacoes_santo_antonio_padua.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(todas_contratacoes, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Todas as contratações salvas em: {output_file}")
    print(f"\n🎉 SUCESSO! O município de Santo Antônio de Pádua - RJ utiliza o PNCP!")
    print(f"   É possível criar o sistema de monitoramento.")
else:
    print(f"\n⚠️  Nenhuma contratação encontrada no período de {data_inicial.strftime('%d/%m/%Y')} a {data_final.strftime('%d/%m/%Y')}")
    print("   Isso pode significar:")
    print("   - O município não publicou contratações neste período")
    print("   - O município ainda não utiliza o PNCP")
    print("   - Pode ser necessário ampliar o período de busca")

print("=" * 80)

