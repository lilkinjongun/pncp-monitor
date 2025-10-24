"""
Módulo de notificações por e-mail
Envia alertas sobre novas contratações
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Optional
import os

logger = logging.getLogger(__name__)


class EmailNotificador:
    """Gerenciador de notificações por e-mail"""
    
    def __init__(
        self,
        smtp_server: str = "smtp.gmail.com",
        smtp_port: int = 587,
        email_remetente: Optional[str] = None,
        senha_remetente: Optional[str] = None
    ):
        """
        Inicializa o notificador de e-mail
        
        Args:
            smtp_server: Servidor SMTP
            smtp_port: Porta SMTP
            email_remetente: E-mail do remetente
            senha_remetente: Senha ou app password do remetente
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_remetente = email_remetente or os.getenv('EMAIL_REMETENTE')
        self.senha_remetente = senha_remetente or os.getenv('SENHA_EMAIL')
        
        if not self.email_remetente or not self.senha_remetente:
            logger.warning(
                "Credenciais de e-mail não configuradas. "
                "Notificações por e-mail não serão enviadas."
            )
    
    def enviar_notificacao_novas_contratacoes(
        self,
        destinatarios: List[str],
        contratacoes: List[Dict],
        municipio: str
    ) -> bool:
        """
        Envia notificação sobre novas contratações
        
        Args:
            destinatarios: Lista de e-mails destinatários
            contratacoes: Lista de contratações para notificar
            municipio: Nome do município
            
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        if not self.email_remetente or not self.senha_remetente:
            logger.warning("Credenciais não configuradas. E-mail não enviado.")
            return False
        
        if not contratacoes:
            logger.info("Nenhuma contratação para notificar.")
            return True
        
        try:
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_remetente
            msg['To'] = ', '.join(destinatarios)
            msg['Subject'] = f"🔔 Novas Contratações - {municipio}"
            
            # Corpo do e-mail em HTML
            html_body = self._gerar_html_notificacao(contratacoes, municipio)
            
            # Corpo do e-mail em texto simples (fallback)
            text_body = self._gerar_texto_notificacao(contratacoes, municipio)
            
            # Anexar ambas as versões
            part1 = MIMEText(text_body, 'plain', 'utf-8')
            part2 = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(part1)
            msg.attach(part2)
            
            # Enviar e-mail
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_remetente, self.senha_remetente)
                server.send_message(msg)
            
            logger.info(
                f"E-mail enviado com sucesso para {len(destinatarios)} destinatário(s)"
            )
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("Erro de autenticação SMTP. Verifique as credenciais.")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"Erro SMTP ao enviar e-mail: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado ao enviar e-mail: {e}")
            return False
    
    def _gerar_html_notificacao(
        self,
        contratacoes: List[Dict],
        municipio: str
    ) -> str:
        """Gera o corpo do e-mail em HTML"""
        
        # Cabeçalho
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px 10px 0 0;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    opacity: 0.9;
                }}
                .content {{
                    background: #f8f9fa;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .contratacao {{
                    background: white;
                    padding: 20px;
                    margin-bottom: 20px;
                    border-radius: 8px;
                    border-left: 4px solid #667eea;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .contratacao h3 {{
                    margin: 0 0 10px 0;
                    color: #667eea;
                    font-size: 16px;
                }}
                .contratacao p {{
                    margin: 5px 0;
                    font-size: 14px;
                }}
                .label {{
                    font-weight: bold;
                    color: #555;
                }}
                .valor {{
                    color: #28a745;
                    font-weight: bold;
                    font-size: 16px;
                }}
                .modalidade {{
                    display: inline-block;
                    background: #e3f2fd;
                    color: #1976d2;
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                .link-btn {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 10px 20px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 10px;
                    font-size: 14px;
                }}
                .link-btn:hover {{
                    background: #5568d3;
                }}
                .footer {{
                    text-align: center;
                    color: #666;
                    font-size: 12px;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔔 Novas Contratações Detectadas</h1>
                <p>{municipio}</p>
            </div>
            <div class="content">
                <p>Foram encontradas <strong>{len(contratacoes)} nova(s) contratação(ões)</strong> no Portal Nacional de Contratações Públicas (PNCP).</p>
                <br>
        """
        
        # Contratações
        for contratacao in contratacoes:
            numero = contratacao.get('numeroCompra', 'N/A')
            ano = contratacao.get('anoCompra', 'N/A')
            objeto = contratacao.get('objetoCompra', 'N/A')
            valor = contratacao.get('valorTotalEstimado', 0)
            modalidade = contratacao.get('_modalidade_nome', 'N/A')
            data_pub = contratacao.get('dataPublicacaoPncp', 'N/A')
            
            # Formatar valor
            valor_formatado = f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            
            # Formatar data
            try:
                data_obj = datetime.fromisoformat(data_pub.replace('Z', '+00:00'))
                data_formatada = data_obj.strftime('%d/%m/%Y às %H:%M')
            except:
                data_formatada = data_pub
            
            # Gerar link
            cnpj = contratacao.get('orgaoEntidade', {}).get('cnpj', '')
            if cnpj and ano != 'N/A' and numero != 'N/A':
                sequencial = contratacao.get('sequencialCompra', '')
                link = f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{sequencial}"
            else:
                link = "https://pncp.gov.br"
            
            html += f"""
                <div class="contratacao">
                    <h3>Contratação Nº {numero}/{ano}</h3>
                    <p><span class="modalidade">{modalidade}</span></p>
                    <p><span class="label">Objeto:</span> {objeto[:200]}{'...' if len(objeto) > 200 else ''}</p>
                    <p><span class="label">Valor Estimado:</span> <span class="valor">{valor_formatado}</span></p>
                    <p><span class="label">Data de Publicação:</span> {data_formatada}</p>
                    <a href="{link}" class="link-btn" target="_blank">Ver no PNCP →</a>
                </div>
            """
        
        # Rodapé
        html += f"""
                <div class="footer">
                    <p>Este é um e-mail automático do Sistema de Monitoramento PNCP.</p>
                    <p>Data de envio: {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _gerar_texto_notificacao(
        self,
        contratacoes: List[Dict],
        municipio: str
    ) -> str:
        """Gera o corpo do e-mail em texto simples"""
        
        texto = f"""
NOVAS CONTRATAÇÕES DETECTADAS
{municipio}
{'=' * 60}

Foram encontradas {len(contratacoes)} nova(s) contratação(ões) no Portal Nacional 
de Contratações Públicas (PNCP).

"""
        
        for i, contratacao in enumerate(contratacoes, 1):
            numero = contratacao.get('numeroCompra', 'N/A')
            ano = contratacao.get('anoCompra', 'N/A')
            objeto = contratacao.get('objetoCompra', 'N/A')
            valor = contratacao.get('valorTotalEstimado', 0)
            modalidade = contratacao.get('_modalidade_nome', 'N/A')
            
            valor_formatado = f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            
            texto += f"""
{i}. Contratação Nº {numero}/{ano}
   Modalidade: {modalidade}
   Objeto: {objeto[:150]}{'...' if len(objeto) > 150 else ''}
   Valor Estimado: {valor_formatado}
   
"""
        
        texto += f"""
{'=' * 60}
Este é um e-mail automático do Sistema de Monitoramento PNCP.
Data de envio: {datetime.now().strftime('%d/%m/%Y às %H:%M')}
"""
        
        return texto
    
    def enviar_email_teste(self, destinatario: str) -> bool:
        """
        Envia um e-mail de teste
        
        Args:
            destinatario: E-mail do destinatário
            
        Returns:
            True se enviado com sucesso
        """
        if not self.email_remetente or not self.senha_remetente:
            logger.error("Credenciais não configuradas.")
            return False
        
        try:
            msg = MIMEText(
                f"Este é um e-mail de teste do Sistema de Monitoramento PNCP.\n\n"
                f"Se você recebeu esta mensagem, o sistema de notificações está "
                f"funcionando corretamente!\n\n"
                f"Data/hora: {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
                'plain',
                'utf-8'
            )
            msg['From'] = self.email_remetente
            msg['To'] = destinatario
            msg['Subject'] = "✅ Teste - Sistema de Monitoramento PNCP"
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_remetente, self.senha_remetente)
                server.send_message(msg)
            
            logger.info(f"E-mail de teste enviado para {destinatario}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail de teste: {e}")
            return False

