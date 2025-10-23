# Sistema de Monitoramento de Contratações Públicas - PNCP

Sistema completo para monitoramento automatizado de contratações públicas do município de **Santo Antônio de Pádua - RJ** através do Portal Nacional de Contratações Públicas (PNCP).

## 📋 Funcionalidades

### ✅ Monitoramento Automatizado
- Busca diária de novas contratações na API do PNCP
- Armazenamento em banco de dados SQLite
- Registro de histórico completo de execuções
- Suporte a todas as 13 modalidades de licitação

### ✅ Dashboard Web Interativo
- Visualização em tempo real das contratações
- Estatísticas e gráficos de análise
- Tabela completa com filtros
- Links diretos para o PNCP
- Interface moderna e responsiva (tema escuro)

### ✅ Notificações por E-mail
- Alertas automáticos de novas contratações
- E-mails HTML formatados e profissionais
- Suporte a múltiplos destinatários
- Controle de notificações duplicadas

### ✅ Agendamento Automático
- Execução diária via cron
- Logs detalhados de todas as operações
- Configuração simples e rápida

## 🚀 Instalação

### Requisitos
- Python 3.11+
- Node.js 22+
- Acesso à internet

### Passo 1: Instalar Dependências Python

```bash
cd /home/ubuntu/pncp_monitor
pip3 install requests
```

### Passo 2: Configurar E-mail (Opcional)

Se você deseja receber notificações por e-mail:

1. Copie o arquivo de configuração:
```bash
cp config_exemplo.env .env
```

2. Edite o arquivo `.env` e preencha:
```env
EMAIL_REMETENTE=seu_email@gmail.com
SENHA_EMAIL=sua_senha_de_app
DESTINATARIOS=email1@exemplo.com,email2@exemplo.com
```

**Importante para Gmail:**
- Você precisa criar uma "Senha de App" (não use sua senha normal)
- Acesse: https://myaccount.google.com/security
- Ative a verificação em duas etapas
- Vá em "Senhas de app" e gere uma senha para "E-mail"

### Passo 3: Configurar Agendamento Automático

```bash
cd /home/ubuntu/pncp_monitor
./setup_cron.sh
```

Isso configurará o sistema para executar automaticamente todos os dias às 8:00 AM.

## 📖 Como Usar

### Executar Monitoramento Manualmente

```bash
cd /home/ubuntu/pncp_monitor
python3 monitor_completo.py
```

### Executar Apenas Busca (sem notificações)

```bash
python3 monitor.py
```

### Acessar o Dashboard Web

O dashboard está disponível em:
https://3000-iagalkjoima9n1t1hlnzm-4fbfdc77.manusvm.computer

Ou localmente:
```bash
cd /home/ubuntu/pncp-dashboard
pnpm dev
```

Acesse: http://localhost:3000

## 📁 Estrutura do Projeto

```
pncp_monitor/
├── pncp_api.py              # Cliente da API do PNCP
├── database.py              # Gerenciamento do banco de dados
├── monitor.py               # Script de monitoramento básico
├── notificador.py           # Sistema de notificações por e-mail
├── monitor_completo.py      # Script completo (monitoramento + notificações)
├── setup_cron.sh            # Configuração do agendamento
├── config_exemplo.env       # Exemplo de configuração
├── pncp_monitor.db          # Banco de dados SQLite
├── pncp_monitor.log         # Log do monitoramento
├── pncp_monitor_completo.log # Log completo
└── README.md                # Esta documentação

pncp-dashboard/
├── client/                  # Frontend React
│   ├── src/
│   │   ├── pages/          # Páginas do dashboard
│   │   │   ├── Home.tsx    # Página inicial
│   │   │   ├── Contratacoes.tsx  # Lista de contratações
│   │   │   └── Estatisticas.tsx  # Gráficos e análises
│   │   └── components/     # Componentes reutilizáveis
│   └── public/             # Arquivos estáticos
└── server/                 # Backend (cópia do pncp_monitor)
```

## 🔧 Configurações Avançadas

### Alterar Frequência de Monitoramento

Edite o arquivo `setup_cron.sh` e modifique a linha:
```bash
CRON_SCHEDULE="0 8 * * *"  # Formato: minuto hora dia mês dia_da_semana
```

Exemplos:
- `0 */6 * * *` - A cada 6 horas
- `0 8,14,20 * * *` - Às 8h, 14h e 20h
- `0 9 * * 1-5` - Às 9h, apenas dias úteis

### Alterar Período de Busca

Edite `monitor_completo.py` e modifique:
```python
DIAS_RETROATIVOS = 7  # Número de dias para buscar
```

### Usar Outro Provedor de E-mail

Edite `notificador.py` e modifique:
```python
smtp_server = "smtp.seuservidor.com"
smtp_port = 587
```

## 📊 Dados Coletados

O sistema coleta as seguintes informações de cada contratação:

- Número e ano da compra
- Objeto da contratação
- Valor estimado e homologado
- Modalidade de licitação
- Data de publicação
- Situação da compra
- Órgão responsável
- Link direto no PNCP

## 🔍 Modalidades Suportadas

O sistema monitora todas as 13 modalidades de contratação:

1. Leilão - Eletrônico
2. Diálogo Competitivo
3. Concurso
4. Concorrência - Eletrônica
5. Concorrência - Presencial
6. Pregão - Eletrônico
7. Pregão - Presencial
8. Dispensa de Licitação
9. Inexigibilidade
10. Manifestação de Interesse
11. Pré-qualificação
12. Credenciamento
13. Leilão - Presencial

## 📝 Logs e Monitoramento

### Ver Logs em Tempo Real

```bash
# Log do monitoramento completo
tail -f /home/ubuntu/pncp_monitor/pncp_monitor_completo.log

# Log do cron
tail -f /home/ubuntu/pncp_monitor/cron.log
```

### Verificar Agendamento

```bash
crontab -l
```

### Estatísticas do Banco de Dados

```bash
cd /home/ubuntu/pncp_monitor
python3 -c "from database import Database; db = Database(); print(db.obter_estatisticas())"
```

## 🐛 Solução de Problemas

### E-mails não estão sendo enviados

1. Verifique se o arquivo `.env` está configurado corretamente
2. Confirme que você está usando uma "Senha de App" do Gmail
3. Verifique os logs em `pncp_monitor_completo.log`

### Monitoramento não está executando automaticamente

1. Verifique se o cron está configurado: `crontab -l`
2. Verifique os logs do cron: `tail -f /home/ubuntu/pncp_monitor/cron.log`
3. Teste a execução manual primeiro: `python3 monitor_completo.py`

### Dashboard não está carregando dados

1. Verifique se o banco de dados existe: `ls -la pncp_monitor.db`
2. Execute o monitoramento manualmente para popular o banco
3. Verifique os logs do navegador (F12 > Console)

## 📚 API do PNCP

O sistema utiliza a API oficial do PNCP:
- **Documentação**: https://pncp.gov.br/api/consulta/swagger-ui/index.html
- **Manual**: https://www.gov.br/pncp/pt-br/central-de-conteudo/manuais
- **Portal**: https://pncp.gov.br

## 🤝 Suporte

Para dúvidas ou problemas:
1. Verifique os logs do sistema
2. Consulte esta documentação
3. Teste a API manualmente: `python3 test_pncp_api_v2.py`

## 📄 Licença

Este projeto foi desenvolvido para fins de transparência e controle social das contratações públicas.

## 🎯 Próximos Passos

Sugestões de melhorias futuras:
- [ ] Adicionar filtros avançados no dashboard
- [ ] Implementar notificações via Telegram/WhatsApp
- [ ] Criar relatórios mensais em PDF
- [ ] Adicionar comparação de valores entre contratações similares
- [ ] Implementar alertas para contratações acima de determinado valor
- [ ] Adicionar gráficos de evolução temporal

---

**Desenvolvido com ❤️ para promover a transparência pública**

