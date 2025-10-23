# Backend - Sistema de Monitoramento PNCP

Backend Python para monitoramento automatizado de contratações públicas através da API do PNCP.

## 🐍 Tecnologias

- **Python 3.11+**
- **SQLite** para armazenamento
- **Requests** para chamadas HTTP
- **SMTP** para notificações por e-mail
- **Cron** para agendamento

## 📁 Arquivos

### Principais
- `pncp_api.py` - Cliente da API do PNCP
- `database.py` - Gerenciamento do banco de dados SQLite
- `monitor.py` - Script de monitoramento básico
- `monitor_completo.py` - Script completo com notificações
- `notificador.py` - Sistema de notificações por e-mail

### Configuração
- `config_exemplo.env` - Exemplo de arquivo de configuração
- `setup_cron.sh` - Script para configurar agendamento automático

### Testes
- `test_pncp_api.py` - Testes da API (versão 1)
- `test_pncp_api_v2.py` - Testes da API (versão 2)

## 🚀 Instalação

### 1. Instalar Dependências

```bash
cd backend
pip3 install -r ../requirements.txt
```

### 2. Configurar E-mail (Opcional)

Se você deseja receber notificações por e-mail:

```bash
cp config_exemplo.env .env
nano .env
```

Preencha com suas credenciais:

```env
EMAIL_REMETENTE=seu_email@gmail.com
SENHA_EMAIL=sua_senha_de_app
DESTINATARIOS=email1@exemplo.com,email2@exemplo.com
```

**Para Gmail:**
1. Acesse: https://myaccount.google.com/security
2. Ative a verificação em duas etapas
3. Vá em "Senhas de app" e gere uma senha para "E-mail"
4. Use essa senha no arquivo `.env`

### 3. Configurar Agendamento Automático

```bash
chmod +x setup_cron.sh
./setup_cron.sh
```

Isso configurará o sistema para executar automaticamente todos os dias às 8:00 AM.

## 📖 Como Usar

### Executar Monitoramento Manualmente

```bash
python3 monitor_completo.py
```

### Executar Apenas Busca (sem notificações)

```bash
python3 monitor.py
```

### Testar API do PNCP

```bash
python3 test_pncp_api_v2.py
```

### Ver Estatísticas do Banco

```bash
python3 -c "from database import Database; db = Database(); print(db.obter_estatisticas())"
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

## 📝 Logs

### Ver Logs em Tempo Real

```bash
# Log do monitoramento completo
tail -f pncp_monitor_completo.log

# Log do cron
tail -f cron.log
```

### Verificar Agendamento

```bash
crontab -l
```

## 🔧 Configurações Avançadas

### Alterar Frequência de Monitoramento

Edite o arquivo `setup_cron.sh` e modifique:

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

## 🐛 Solução de Problemas

### E-mails não estão sendo enviados

1. Verifique se o arquivo `.env` está configurado corretamente
2. Confirme que você está usando uma "Senha de App" do Gmail
3. Verifique os logs em `pncp_monitor_completo.log`

### Monitoramento não está executando automaticamente

1. Verifique se o cron está configurado: `crontab -l`
2. Verifique os logs do cron: `tail -f cron.log`
3. Teste a execução manual primeiro: `python3 monitor_completo.py`

### Erro ao conectar com a API do PNCP

1. Verifique sua conexão com a internet
2. Teste a API manualmente: `python3 test_pncp_api_v2.py`
3. Consulte a documentação oficial: https://pncp.gov.br/api/consulta/swagger-ui/index.html

## 📚 API do PNCP

O sistema utiliza a API oficial do PNCP:

- **Documentação**: https://pncp.gov.br/api/consulta/swagger-ui/index.html
- **Manual**: https://www.gov.br/pncp/pt-br/central-de-conteudo/manuais
- **Portal**: https://pncp.gov.br

## 🔌 Integração com Frontend

Para integrar com o frontend React, você pode criar uma API REST usando Flask ou FastAPI:

```python
from flask import Flask, jsonify
from database import Database

app = Flask(__name__)
db = Database()

@app.route('/api/stats')
def get_stats():
    return jsonify(db.obter_estatisticas())

@app.route('/api/contratacoes')
def get_contratacoes():
    return jsonify(db.listar_todas_contratacoes())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

