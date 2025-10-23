# 🚀 Guia Rápido - Sistema de Monitoramento PNCP

## Início Rápido em 3 Passos

### 1️⃣ Executar Monitoramento Agora

```bash
cd /home/ubuntu/pncp_monitor
python3 monitor_completo.py
```

Isso irá:
- ✅ Buscar contratações dos últimos 7 dias
- ✅ Salvar no banco de dados
- ✅ Exibir estatísticas

### 2️⃣ Acessar o Dashboard Web

Abra no navegador:
```
https://3000-iagalkjoima9n1t1hlnzm-4fbfdc77.manusvm.computer
```

Ou execute localmente:
```bash
cd /home/ubuntu/pncp-dashboard
pnpm dev
```

### 3️⃣ Configurar Notificações por E-mail (Opcional)

```bash
cd /home/ubuntu/pncp_monitor
cp config_exemplo.env .env
nano .env  # Edite e adicione suas credenciais
```

Preencha:
```env
EMAIL_REMETENTE=seu_email@gmail.com
SENHA_EMAIL=sua_senha_de_app_do_gmail
DESTINATARIOS=email1@exemplo.com,email2@exemplo.com
```

**Como obter senha de app do Gmail:**
1. Acesse: https://myaccount.google.com/security
2. Ative verificação em 2 etapas
3. Vá em "Senhas de app"
4. Gere uma senha para "E-mail"
5. Use essa senha no arquivo .env

---

## ⏰ Configurar Execução Automática

```bash
cd /home/ubuntu/pncp_monitor
./setup_cron.sh
```

Isso configura o sistema para executar **todos os dias às 8:00 AM**.

---

## 📊 Ver Estatísticas

```bash
cd /home/ubuntu/pncp_monitor
python3 -c "
from database import Database
db = Database()
stats = db.obter_estatisticas()
print(f'Total: {stats[\"total_contratacoes\"]}')
print(f'Valor: R$ {stats[\"valor_total_estimado\"]:,.2f}')
"
```

---

## 📝 Ver Logs

```bash
# Log completo
tail -f /home/ubuntu/pncp_monitor/pncp_monitor_completo.log

# Log do cron (após configurar)
tail -f /home/ubuntu/pncp_monitor/cron.log
```

---

## 🔧 Comandos Úteis

### Verificar agendamento
```bash
crontab -l
```

### Remover agendamento
```bash
crontab -e
# Remova a linha do monitor_completo.py
```

### Limpar banco de dados
```bash
rm /home/ubuntu/pncp_monitor/pncp_monitor.db
python3 /home/ubuntu/pncp_monitor/monitor.py
```

### Testar e-mail
```bash
cd /home/ubuntu/pncp_monitor
python3 -c "
from notificador import EmailNotificador
n = EmailNotificador()
n.enviar_email_teste('seu_email@exemplo.com')
"
```

---

## 📁 Arquivos Importantes

| Arquivo | Descrição |
|---------|-----------|
| `monitor_completo.py` | Script principal (monitoramento + notificações) |
| `monitor.py` | Apenas monitoramento (sem e-mail) |
| `pncp_monitor.db` | Banco de dados SQLite |
| `README.md` | Documentação completa |
| `.env` | Configurações (criar a partir do config_exemplo.env) |

---

## ❓ Problemas Comuns

### E-mail não envia
- ✅ Verifique se usou "Senha de App" do Gmail (não a senha normal)
- ✅ Confirme que o arquivo `.env` existe e está preenchido
- ✅ Veja os logs: `tail -f pncp_monitor_completo.log`

### Nenhuma contratação encontrada
- ✅ Normal! Significa que não há novas contratações no período
- ✅ Tente aumentar `DIAS_RETROATIVOS` no `monitor_completo.py`

### Dashboard não carrega
- ✅ Execute: `cd /home/ubuntu/pncp-dashboard && pnpm dev`
- ✅ Acesse: http://localhost:3000

---

## 📚 Documentação Completa

Para mais detalhes, consulte:
```bash
cat /home/ubuntu/pncp_monitor/README.md
```

---

## 🎯 Próximos Passos Recomendados

1. ✅ Execute o monitoramento manualmente para testar
2. ✅ Acesse o dashboard e explore as funcionalidades
3. ✅ Configure as notificações por e-mail
4. ✅ Configure o agendamento automático
5. ✅ Monitore os logs regularmente

---

**Sistema desenvolvido para promover transparência nas contratações públicas! 🇧🇷**

