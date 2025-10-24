"""
Script completo de monitoramento com notificações
Executa monitoramento e envia alertas por e-mail
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

# Adicionar diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

from monitor import PNCPMonitor
from notificador import EmailNotificador

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pncp_monitor_completo.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Função principal"""
    
    # Configurações
    CODIGO_IBGE = "3304706"
    NOME_MUNICIPIO = "Santo Antônio de Pádua - RJ"
    DIAS_RETROATIVOS = 7  # Buscar contratações dos últimos 7 dias
    
    # E-mails para notificação (configurar conforme necessário)
    DESTINATARIOS = [
        # "seu_email@exemplo.com",
    ]
    
    logger.info("=" * 80)
    logger.info("SISTEMA DE MONITORAMENTO PNCP - EXECUÇÃO COMPLETA")
    logger.info("=" * 80)
    logger.info(f"Município: {NOME_MUNICIPIO}")
    logger.info(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    logger.info("=" * 80)
    
    # Criar monitor
    monitor = PNCPMonitor(
        codigo_ibge=CODIGO_IBGE,
        nome_municipio=NOME_MUNICIPIO
    )
    
    try:
        # Executar monitoramento
        logger.info("\n[1/3] Executando monitoramento...")
        resultado = monitor.executar_monitoramento(dias_retroativos=DIAS_RETROATIVOS)
        
        if not resultado['sucesso']:
            logger.error(f"Erro no monitoramento: {resultado.get('erro')}")
            return 1
        
        logger.info(f"✅ Monitoramento concluído!")
        logger.info(f"   Total encontradas: {resultado['total_encontradas']}")
        logger.info(f"   Novas: {resultado['novas']}")
        
        # Verificar se há contratações para notificar
        if resultado['novas'] > 0 and DESTINATARIOS:
            logger.info("\n[2/3] Preparando notificações por e-mail...")
            
            # Buscar contratações não notificadas
            contratacoes_nao_notificadas = monitor.obter_contratacoes_nao_notificadas()
            
            if contratacoes_nao_notificadas:
                # Criar notificador
                notificador = EmailNotificador()
                
                # Converter formato do banco para formato esperado
                contratacoes_para_notificar = []
                for c in contratacoes_nao_notificadas:
                    import json
                    dados_completos = json.loads(c['dados_completos'])
                    contratacoes_para_notificar.append(dados_completos)
                
                # Enviar notificação
                logger.info(f"   Enviando notificação para {len(DESTINATARIOS)} destinatário(s)...")
                sucesso = notificador.enviar_notificacao_novas_contratacoes(
                    destinatarios=DESTINATARIOS,
                    contratacoes=contratacoes_para_notificar,
                    municipio=NOME_MUNICIPIO
                )
                
                if sucesso:
                    logger.info("✅ Notificações enviadas com sucesso!")
                    
                    # Marcar como notificadas
                    logger.info("\n[3/3] Atualizando status das notificações...")
                    for c in contratacoes_nao_notificadas:
                        monitor.marcar_como_notificado(c['id'])
                    logger.info("✅ Status atualizado!")
                else:
                    logger.warning("⚠️  Falha ao enviar notificações.")
            else:
                logger.info("   Nenhuma contratação pendente de notificação.")
        elif resultado['novas'] > 0 and not DESTINATARIOS:
            logger.info("\n[2/3] Notificações desabilitadas (sem destinatários configurados)")
        else:
            logger.info("\n[2/3] Nenhuma nova contratação para notificar")
        
        # Exibir estatísticas
        logger.info("\n" + "=" * 80)
        logger.info("ESTATÍSTICAS GERAIS")
        logger.info("=" * 80)
        stats = monitor.obter_estatisticas()
        logger.info(f"Total no banco: {stats['total_contratacoes']}")
        logger.info(f"Valor total estimado: R$ {stats['valor_total_estimado']:,.2f}")
        logger.info(f"Última atualização: {stats['ultima_atualizacao']}")
        logger.info("\nPor modalidade:")
        for item in stats['por_modalidade']:
            logger.info(f"  - {item['modalidade_nome']}: {item['quantidade']}")
        logger.info("=" * 80)
        
        logger.info("\n✅ EXECUÇÃO CONCLUÍDA COM SUCESSO!")
        return 0
        
    except Exception as e:
        logger.error(f"\n❌ ERRO DURANTE A EXECUÇÃO: {e}", exc_info=True)
        return 1
        
    finally:
        monitor.fechar()


if __name__ == "__main__":
    sys.exit(main())

