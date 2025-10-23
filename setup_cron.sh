#!/bin/bash
# Script para configurar o agendamento automático do monitoramento

echo "========================================="
echo "Configuração do Agendamento Automático"
echo "Sistema de Monitoramento PNCP"
echo "========================================="
echo ""

# Diretório do projeto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/monitor_completo.py"

echo "Diretório do projeto: $SCRIPT_DIR"
echo "Script Python: $PYTHON_SCRIPT"
echo ""

# Verificar se o script existe
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ Erro: Script monitor_completo.py não encontrado!"
    exit 1
fi

# Criar entrada do cron
# Executar todos os dias às 8h da manhã
CRON_SCHEDULE="0 8 * * *"
CRON_COMMAND="cd $SCRIPT_DIR && /usr/bin/python3 $PYTHON_SCRIPT >> $SCRIPT_DIR/cron.log 2>&1"
CRON_ENTRY="$CRON_SCHEDULE $CRON_COMMAND"

echo "Configuração do agendamento:"
echo "  Horário: Todos os dias às 8:00 AM"
echo "  Comando: $CRON_COMMAND"
echo ""

# Verificar se já existe uma entrada similar no cron
if crontab -l 2>/dev/null | grep -q "monitor_completo.py"; then
    echo "⚠️  Já existe uma entrada do monitoramento no cron."
    echo ""
    read -p "Deseja substituir? (s/n): " resposta
    if [ "$resposta" != "s" ] && [ "$resposta" != "S" ]; then
        echo "Operação cancelada."
        exit 0
    fi
    # Remover entrada antiga
    crontab -l 2>/dev/null | grep -v "monitor_completo.py" | crontab -
    echo "✅ Entrada antiga removida."
fi

# Adicionar nova entrada ao cron
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

echo ""
echo "✅ Agendamento configurado com sucesso!"
echo ""
echo "O monitoramento será executado automaticamente todos os dias às 8:00 AM."
echo ""
echo "Para verificar o agendamento:"
echo "  $ crontab -l"
echo ""
echo "Para ver os logs de execução:"
echo "  $ tail -f $SCRIPT_DIR/cron.log"
echo ""
echo "Para remover o agendamento:"
echo "  $ crontab -e"
echo "  (e remova a linha do monitor_completo.py)"
echo ""
echo "========================================="

