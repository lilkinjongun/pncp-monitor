"""
Script principal de monitoramento de contratações do PNCP
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Adicionar diretório atual ao path
sys.path.insert(0, str(Path(__file__).parent))

from pncp_api import PNCPClient
from database import Database

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pncp_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PNCPMonitor:
    """Monitor de contratações do PNCP"""
    
    def __init__(
        self,
        codigo_ibge: str,
        nome_municipio: str,
        db_path: str = "pncp_monitor.db"
    ):
        """
        Inicializa o monitor
        
        Args:
            codigo_ibge: Código IBGE do município
            nome_municipio: Nome do município
            db_path: Caminho para o banco de dados
        """
        self.codigo_ibge = codigo_ibge
        self.nome_municipio = nome_municipio
        self.client = PNCPClient()
        self.db = Database(db_path)
        
        logger.info(f"Monitor inicializado para {nome_municipio} ({codigo_ibge})")
    
    def executar_monitoramento(
        self,
        dias_retroativos: int = 7,
        modalidades: list = None
    ) -> dict:
        """
        Executa uma rodada de monitoramento
        
        Args:
            dias_retroativos: Quantos dias para trás buscar
            modalidades: Lista de códigos de modalidade (None = todas)
            
        Returns:
            Dicionário com resultados da execução
        """
        logger.info("=" * 80)
        logger.info(f"Iniciando monitoramento - {datetime.now()}")
        logger.info("=" * 80)
        
        # Definir período de busca
        data_final = datetime.now()
        data_inicial = data_final - timedelta(days=dias_retroativos)
        
        logger.info(
            f"Período: {data_inicial.strftime('%d/%m/%Y')} a "
            f"{data_final.strftime('%d/%m/%Y')}"
        )
        
        try:
            # Buscar contratações
            contratacoes = self.client.buscar_contratacoes_por_municipio(
                codigo_ibge=self.codigo_ibge,
                data_inicial=data_inicial,
                data_final=data_final,
                modalidades=modalidades
            )
            
            logger.info(f"Total de contratações encontradas: {len(contratacoes)}")
            
            # Salvar no banco de dados
            novas = self.db.salvar_contratacoes(contratacoes)
            
            logger.info(f"Novas contratações: {novas}")
            
            # Registrar execução
            self.db.registrar_execucao(
                encontradas=len(contratacoes),
                novas=novas,
                sucesso=True,
                mensagem=f"Monitoramento executado com sucesso"
            )
            
            resultado = {
                'sucesso': True,
                'total_encontradas': len(contratacoes),
                'novas': novas,
                'data_execucao': datetime.now().isoformat()
            }
            
            logger.info("Monitoramento concluído com sucesso")
            return resultado
            
        except Exception as e:
            logger.error(f"Erro durante monitoramento: {e}", exc_info=True)
            
            self.db.registrar_execucao(
                encontradas=0,
                novas=0,
                sucesso=False,
                mensagem=f"Erro: {str(e)}"
            )
            
            return {
                'sucesso': False,
                'erro': str(e),
                'data_execucao': datetime.now().isoformat()
            }
    
    def obter_contratacoes_nao_notificadas(self) -> list:
        """
        Obtém contratações que ainda não foram notificadas
        
        Returns:
            Lista de contratações não notificadas
        """
        return self.db.buscar_contratacoes_nao_notificadas()
    
    def marcar_como_notificado(self, contratacao_id: int):
        """
        Marca uma contratação como notificada
        
        Args:
            contratacao_id: ID da contratação
        """
        self.db.marcar_como_notificado(contratacao_id)
    
    def obter_estatisticas(self) -> dict:
        """
        Obtém estatísticas do monitoramento
        
        Returns:
            Dicionário com estatísticas
        """
        return self.db.obter_estatisticas()
    
    def fechar(self):
        """Fecha conexões e libera recursos"""
        self.db.fechar()


def main():
    """Função principal para execução via linha de comando"""
    # Configuração para Santo Antônio de Pádua - RJ
    CODIGO_IBGE = "3304706"
    NOME_MUNICIPIO = "Santo Antônio de Pádua - RJ"
    
    # Criar monitor
    monitor = PNCPMonitor(
        codigo_ibge=CODIGO_IBGE,
        nome_municipio=NOME_MUNICIPIO
    )
    
    try:
        # Executar monitoramento (últimos 30 dias)
        resultado = monitor.executar_monitoramento(dias_retroativos=30)
        
        if resultado['sucesso']:
            print("\n" + "=" * 80)
            print("RESUMO DO MONITORAMENTO")
            print("=" * 80)
            print(f"Total encontradas: {resultado['total_encontradas']}")
            print(f"Novas contratações: {resultado['novas']}")
            print(f"Data/hora: {resultado['data_execucao']}")
            print("=" * 80)
            
            # Exibir estatísticas
            stats = monitor.obter_estatisticas()
            print("\nESTATÍSTICAS GERAIS")
            print("=" * 80)
            print(f"Total no banco: {stats['total_contratacoes']}")
            print(f"Valor total estimado: R$ {stats['valor_total_estimado']:,.2f}")
            print(f"Última atualização: {stats['ultima_atualizacao']}")
            print("\nPor modalidade:")
            for item in stats['por_modalidade']:
                print(f"  - {item['modalidade_nome']}: {item['quantidade']}")
            print("=" * 80)
        else:
            print(f"\n❌ Erro no monitoramento: {resultado['erro']}")
            sys.exit(1)
            
    finally:
        monitor.fechar()


if __name__ == "__main__":
    main()

