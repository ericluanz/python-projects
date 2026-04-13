"""
=============================================================
  ALERTA DE USO DE DISCO
  Monitora partições e alerta quando passar do limite
  Suporta alerta no terminal e por e-mail (opcional)
=============================================================
  Como usar:
    1. Ajuste as configurações abaixo conforme necessário
    2. Execute: python alerta_disco.py
    3. Para monitoramento contínuo, deixe rodando ou agende
       no Agendador de Tarefas do Windows

  Dependência externa (opcional, só para e-mail HTML):
    pip install psutil
=============================================================
"""

import psutil       # Leitura de disco — instale com: pip install psutil
import smtplib      # Envio de e-mail (já vem com Python)
import datetime     # Data e hora dos alertas
import time         # Para o modo de monitoramento contínuo
import os           # Para salvar o log
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# =============================================================
#  CONFIGURAÇÕES — edite conforme sua necessidade
# =============================================================

# Limite de uso (%) a partir do qual o alerta é disparado
LIMITE_ALERTA_PCT = 80      # Alerta em 80% ou mais de uso

# Limite crítico (%) para alerta com urgência máxima
LIMITE_CRITICO_PCT = 90     # Crítico em 90% ou mais

# Intervalo de verificação no modo contínuo (em segundos)
INTERVALO_SEGUNDOS = 60     # Verifica a cada 1 minuto

# Arquivo onde os alertas são registrados
ARQUIVO_LOG = "log_alertas_disco.txt"

# --- Configuração de E-mail (opcional) ---
# Deixe ENVIAR_EMAIL = False para usar só o terminal e o log
ENVIAR_EMAIL = False

EMAIL_REMETENTE  = "seu_email@gmail.com"
EMAIL_SENHA      = "sua_senha_de_app"       # Use senha de app do Gmail
EMAIL_DESTINATARIO = "destino@empresa.com"
EMAIL_SMTP_HOST  = "smtp.gmail.com"
EMAIL_SMTP_PORTA = 587

# =============================================================
#  FUNÇÕES
# =============================================================

def obter_uso_discos():
    """
    Lê todas as partições de disco e retorna uma lista
    com informações de uso de cada uma.
    """
    discos = []
    for particao in psutil.disk_partitions():
        try:
            uso = psutil.disk_usage(particao.mountpoint)
            total_gb = round(uso.total / (1024 ** 3), 1)
            usado_gb = round(uso.used  / (1024 ** 3), 1)
            livre_gb = round(uso.free  / (1024 ** 3), 1)
            discos.append({
                "drive":     particao.device,
                "ponto":     particao.mountpoint,
                "total_gb":  total_gb,
                "usado_gb":  usado_gb,
                "livre_gb":  livre_gb,
                "uso_pct":   uso.percent,
            })
        except PermissionError:
            # Drives de sistema especiais podem bloquear acesso
            continue
    return discos


def classificar_alerta(uso_pct):
    """
    Retorna o nível de alerta baseado no percentual de uso.
    Retorna None se estiver dentro do limite normal.
    """
    if uso_pct >= LIMITE_CRITICO_PCT:
        return "CRITICO"
    elif uso_pct >= LIMITE_ALERTA_PCT:
        return "ALERTA"
    return None


def formatar_linha_log(nivel, disco):
    """Formata uma linha de log para o arquivo de texto."""
    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return (
        f"[{agora}] [{nivel}] "
        f"Drive: {disco['drive']} | "
        f"Uso: {disco['uso_pct']}% | "
        f"Livre: {disco['livre_gb']} GB de {disco['total_gb']} GB"
    )


def registrar_log(linha):
    """Adiciona uma linha ao arquivo de log."""
    with open(ARQUIVO_LOG, "a", encoding="utf-8") as f:
        f.write(linha + "\n")


def exibir_alerta_terminal(nivel, disco):
    """Exibe o alerta formatado no terminal com destaque visual."""
    prefixo = "!!! CRITICO" if nivel == "CRITICO" else ">> ALERTA"
    print(f"\n  {prefixo}: {disco['drive']} ({disco['ponto']})")
    print(f"     Uso atual : {disco['uso_pct']}%")
    print(f"     Usado     : {disco['usado_gb']} GB")
    print(f"     Livre     : {disco['livre_gb']} GB")
    print(f"     Total     : {disco['total_gb']} GB")
    print(f"     Limite    : {LIMITE_CRITICO_PCT if nivel == 'CRITICO' else LIMITE_ALERTA_PCT}%")


def enviar_email(alertas):
    """
    Envia um e-mail com a lista de drives em alerta.
    Só é chamado se ENVIAR_EMAIL = True.
    """
    if not alertas:
        return

    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    hostname = os.environ.get("COMPUTERNAME", "desconhecido")

    # Monta o corpo do e-mail em texto simples
    corpo = f"Alerta de disco — {hostname} — {agora}\n\n"
    for nivel, disco in alertas:
        corpo += (
            f"[{nivel}] {disco['drive']} ({disco['ponto']})\n"
            f"  Uso: {disco['uso_pct']}%  |  "
            f"Livre: {disco['livre_gb']} GB de {disco['total_gb']} GB\n\n"
        )
    corpo += "Verifique o servidor e libere espaço se necessário."

    mensagem = MIMEMultipart()
    mensagem["From"]    = EMAIL_REMETENTE
    mensagem["To"]      = EMAIL_DESTINATARIO
    mensagem["Subject"] = f"[DISCO] Alerta de espaço em {hostname}"
    mensagem.attach(MIMEText(corpo, "plain", "utf-8"))

    try:
        with smtplib.SMTP(EMAIL_SMTP_HOST, EMAIL_SMTP_PORTA) as servidor:
            servidor.starttls()                              # Ativa criptografia
            servidor.login(EMAIL_REMETENTE, EMAIL_SENHA)
            servidor.sendmail(
                EMAIL_REMETENTE,
                EMAIL_DESTINATARIO,
                mensagem.as_string()
            )
        print("  E-mail de alerta enviado.")
    except Exception as erro:
        print(f"  Falha ao enviar e-mail: {erro}")


def verificar_discos():
    """
    Função principal de verificação.
    Lê os discos, classifica, exibe alertas e salva no log.
    Retorna True se encontrou algum alerta.
    """
    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"\n[{agora}] Verificando discos...")

    discos = obter_uso_discos()
    alertas_encontrados = []

    for disco in discos:
        nivel = classificar_alerta(disco["uso_pct"])

        # Exibe status de cada drive (OK ou alerta)
        icone = "OK  " if nivel is None else ("!!  " if nivel == "CRITICO" else ">   ")
        print(f"  {icone} {disco['drive']:10} {disco['uso_pct']:5.1f}%  "
              f"({disco['livre_gb']} GB livres de {disco['total_gb']} GB)")

        if nivel:
            exibir_alerta_terminal(nivel, disco)
            linha_log = formatar_linha_log(nivel, disco)
            registrar_log(linha_log)
            alertas_encontrados.append((nivel, disco))

    if not alertas_encontrados:
        print("  Todos os discos dentro do limite normal.")
    elif ENVIAR_EMAIL:
        enviar_email(alertas_encontrados)

    return len(alertas_encontrados) > 0


def modo_continuo():
    """
    Executa a verificação em loop, aguardando INTERVALO_SEGUNDOS
    entre cada ciclo. Ideal para deixar rodando em background.
    """
    print("=" * 55)
    print("  MONITORAMENTO CONTÍNUO DE DISCO")
    print(f"  Limite de alerta : {LIMITE_ALERTA_PCT}%")
    print(f"  Limite crítico   : {LIMITE_CRITICO_PCT}%")
    print(f"  Intervalo        : {INTERVALO_SEGUNDOS}s")
    print(f"  Log              : {ARQUIVO_LOG}")
    print("  Pressione Ctrl+C para encerrar")
    print("=" * 55)

    try:
        while True:
            verificar_discos()
            print(f"\n  Próxima verificação em {INTERVALO_SEGUNDOS} segundos...")
            time.sleep(INTERVALO_SEGUNDOS)
    except KeyboardInterrupt:
        print("\n\n  Monitoramento encerrado pelo usuário.")


def modo_unico():
    """
    Executa uma única verificação e encerra.
    Ideal para usar com o Agendador de Tarefas do Windows.
    """
    print("=" * 55)
    print("  VERIFICAÇÃO DE DISCO — EXECUÇÃO ÚNICA")
    print(f"  Limite de alerta : {LIMITE_ALERTA_PCT}%")
    print(f"  Limite crítico   : {LIMITE_CRITICO_PCT}%")
    print("=" * 55)
    verificar_discos()
    print(f"\n  Log salvo em: {ARQUIVO_LOG}")
    print("  Concluído.")


# =============================================================
#  EXECUÇÃO PRINCIPAL
# =============================================================

if __name__ == "__main__":
    print("\nEscolha o modo de execução:")
    print("  1 — Verificação única (recomendado para Agendador de Tarefas)")
    print("  2 — Monitoramento contínuo (fica rodando em loop)")

    escolha = input("\nOpção (1 ou 2): ").strip()

    if escolha == "2":
        modo_continuo()
    else:
        modo_unico()
