"""
Módulo de integração com a API do PNCP
Portal Nacional de Contratações Públicas
"""

import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PNCPClient:
    """Cliente para interagir com a API do PNCP"""
    
    BASE_URL = "https://pncp.gov.br/api/consulta/v1"
    
    # Códigos de modalidade de contratação
    MODALIDADES = {
        1: "Leilão - Eletrônico",
        2: "Diálogo Competitivo",
        3: "Concurso",
        4: "Concorrência - Eletrônica",
        5: "Concorrência - Presencial",
        6: "Pregão - Eletrônico",
        7: "Pregão - Presencial",
        8: "Dispensa de Licitação",
        9: "Inexigibilidade",
        10: "Manifestação de Interesse",
        11: "Pré-qualificação",
        12: "Credenciamento",
        13: "Leilão - Presencial"
    }
    
    def __init__(self, timeout: int = 30, retry_attempts: int = 3):
        """
        Inicializa o cliente PNCP
        
        Args:
            timeout: Timeout para requisições em segundos
            retry_attempts: Número de tentativas em caso de falha
        """
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.session = requests.Session()
        
    def buscar_contratacoes_por_municipio(
        self,
        codigo_ibge: str,
        data_inicial: datetime,
        data_final: datetime,
        modalidades: Optional[List[int]] = None,
        pagina: int = 1,
        tamanho_pagina: int = 50
    ) -> List[Dict]:
        """
        Busca contratações de um município específico
        
        Args:
            codigo_ibge: Código IBGE do município (7 dígitos)
            data_inicial: Data inicial da busca
            data_final: Data final da busca
            modalidades: Lista de códigos de modalidade (None = todas)
            pagina: Número da página
            tamanho_pagina: Quantidade de registros por página
            
        Returns:
            Lista de contratações encontradas
        """
        if modalidades is None:
            # Buscar todas as modalidades
            modalidades = list(self.MODALIDADES.keys())
        
        todas_contratacoes = []
        
        for codigo_modalidade in modalidades:
            logger.info(
                f"Buscando modalidade {codigo_modalidade} "
                f"({self.MODALIDADES.get(codigo_modalidade, 'Desconhecida')})"
            )
            
            try:
                contratacoes = self._buscar_por_modalidade(
                    codigo_ibge=codigo_ibge,
                    data_inicial=data_inicial,
                    data_final=data_final,
                    codigo_modalidade=codigo_modalidade,
                    pagina=pagina,
                    tamanho_pagina=tamanho_pagina
                )
                
                if contratacoes:
                    # Adicionar informação da modalidade
                    for contratacao in contratacoes:
                        contratacao['_modalidade_codigo'] = codigo_modalidade
                        contratacao['_modalidade_nome'] = self.MODALIDADES[codigo_modalidade]
                    
                    todas_contratacoes.extend(contratacoes)
                    logger.info(f"Encontradas {len(contratacoes)} contratações")
                else:
                    logger.info("Nenhuma contratação encontrada")
                    
                # Pequeno delay para não sobrecarregar a API
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(
                    f"Erro ao buscar modalidade {codigo_modalidade}: {e}"
                )
                continue
        
        logger.info(f"Total de contratações encontradas: {len(todas_contratacoes)}")
        return todas_contratacoes
    
    def _buscar_por_modalidade(
        self,
        codigo_ibge: str,
        data_inicial: datetime,
        data_final: datetime,
        codigo_modalidade: int,
        pagina: int = 1,
        tamanho_pagina: int = 50
    ) -> List[Dict]:
        """
        Busca contratações de uma modalidade específica
        
        Args:
            codigo_ibge: Código IBGE do município
            data_inicial: Data inicial da busca
            data_final: Data final da busca
            codigo_modalidade: Código da modalidade
            pagina: Número da página
            tamanho_pagina: Quantidade de registros por página
            
        Returns:
            Lista de contratações
        """
        url = f"{self.BASE_URL}/contratacoes/publicacao"
        
        params = {
            "dataInicial": data_inicial.strftime("%Y%m%d"),
            "dataFinal": data_final.strftime("%Y%m%d"),
            "codigoMunicipioIbge": codigo_ibge,
            "codigoModalidadeContratacao": codigo_modalidade,
            "pagina": pagina,
            "tamanhoPagina": tamanho_pagina
        }
        
        for tentativa in range(self.retry_attempts):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._extrair_contratacoes(data)
                    
                elif response.status_code == 422:
                    logger.warning(f"Código IBGE inválido: {codigo_ibge}")
                    return []
                    
                elif response.status_code == 404:
                    logger.warning("Endpoint não encontrado")
                    return []
                    
                else:
                    logger.warning(
                        f"Status {response.status_code}: {response.text[:200]}"
                    )
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout na tentativa {tentativa + 1}")
                if tentativa < self.retry_attempts - 1:
                    time.sleep(2 ** tentativa)  # Backoff exponencial
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Erro na requisição: {e}")
                if tentativa < self.retry_attempts - 1:
                    time.sleep(2 ** tentativa)
                    
        return []
    
    def _extrair_contratacoes(self, data: Dict) -> List[Dict]:
        """
        Extrai a lista de contratações da resposta da API
        
        Args:
            data: Dados retornados pela API
            
        Returns:
            Lista de contratações
        """
        if isinstance(data, list):
            return data
            
        if isinstance(data, dict):
            # Tentar diferentes estruturas de resposta
            if 'data' in data:
                return data['data']
            elif 'content' in data:
                return data['content']
            elif 'items' in data:
                return data['items']
            else:
                # Procurar por uma lista dentro do dict
                for value in data.values():
                    if isinstance(value, list) and len(value) > 0:
                        return value
        
        return []
    
    def buscar_detalhes_contratacao(
        self,
        cnpj: str,
        ano: int,
        sequencial: int
    ) -> Optional[Dict]:
        """
        Busca detalhes de uma contratação específica
        
        Args:
            cnpj: CNPJ do órgão
            ano: Ano da compra
            sequencial: Número sequencial da compra
            
        Returns:
            Detalhes da contratação ou None
        """
        url = f"{self.BASE_URL}/orgaos/{cnpj}/compras/{ano}/{sequencial}"
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(
                    f"Erro ao buscar detalhes: {response.status_code}"
                )
                return None
                
        except Exception as e:
            logger.error(f"Erro ao buscar detalhes: {e}")
            return None
    
    def formatar_contratacao(self, contratacao: Dict) -> Dict:
        """
        Formata uma contratação para exibição
        
        Args:
            contratacao: Dados brutos da contratação
            
        Returns:
            Contratação formatada
        """
        return {
            'numero': contratacao.get('numeroCompra', 'N/A'),
            'ano': contratacao.get('anoCompra', 'N/A'),
            'sequencial': contratacao.get('sequencialCompra', 'N/A'),
            'objeto': contratacao.get('objetoCompra', 'N/A'),
            'valor_estimado': contratacao.get('valorTotalEstimado', 0),
            'valor_homologado': contratacao.get('valorTotalHomologado', 0),
            'modalidade': contratacao.get('_modalidade_nome', 'N/A'),
            'modalidade_codigo': contratacao.get('_modalidade_codigo', 0),
            'data_publicacao': contratacao.get('dataPublicacaoPncp', 'N/A'),
            'situacao': contratacao.get('situacaoCompra', 'N/A'),
            'orgao': self._extrair_orgao(contratacao),
            'link_pncp': self._gerar_link_pncp(contratacao)
        }
    
    def _extrair_orgao(self, contratacao: Dict) -> str:
        """Extrai o nome do órgão da contratação"""
        orgao = contratacao.get('orgaoEntidade', {})
        if isinstance(orgao, dict):
            return orgao.get('razaoSocial', 'N/A')
        return 'N/A'
    
    def _gerar_link_pncp(self, contratacao: Dict) -> str:
        """Gera o link para a contratação no portal PNCP"""
        cnpj = contratacao.get('orgaoEntidade', {}).get('cnpj', '')
        ano = contratacao.get('anoCompra', '')
        sequencial = contratacao.get('sequencialCompra', '')
        
        if cnpj and ano and sequencial:
            return f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{sequencial}"
        return "N/A"

