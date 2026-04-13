"""
=============================================================
  VERIFICADOR DE CONECTIVIDADE
  Testa ping e porta em uma lista de servidores
  e gera relatório em arquivo .txt
=============================================================
  Como usar:
    1. Edite a lista SERVIDORES abaixo com seus hosts
    2. Execute: python verificador_conectividade.py
    3. Veja o relatório gerado em: relatorio_conectividade.txt
=============================================================
"""

import subprocess   # Para executar comandos do sistema (ping)
import socket       # Para testar conexão em portas
import datetime     # Para registrar data e hora no relatório
import platform     # Para detectar se é Windows ou Linux

# =============================================================
#  CONFIGURAÇÕES — edite aqui conforme sua necessidade
# =============================================================

SERVIDORES = [
    {"nome": "Google DNS",       "host": "8.8.8.8",        "porta": 53},
    {"nome": "Cloudflare DNS",   "host": "1.1.1.1",        "porta": 53},
    {"nome": "Google Web",       "host": "google.com",     "porta": 443},
    {"nome": "Servidor Interno", "host": "192.168.1.1",    "porta": 80},
    # Adicione mais servidores no mesmo formato:
    # {"nome": "Nome Amigável", "host": "IP ou hostname", "porta": NUMERO},
]

TIMEOUT_SEGUNDOS = 3       # Tempo máximo de espera por resposta
ARQUIVO_RELATORIO = "relatorio_conectividade.txt"  # Nome do arquivo de saída

# =============================================================
#  FUNÇÕES PRINCIPAIS
# =============================================================

def testar_ping(host):
    """
    Testa se o host responde ao ping.
    Retorna True se responder, False se não.
    """
    # O comando de ping é diferente no Windows e no Linux/Mac
    sistema = platform.system().lower()
    if sistema == "windows":
        comando = ["ping", "-n", "1", "-w", str(TIMEOUT_SEGUNDOS * 1000), host]
    else:
        comando = ["ping", "-c", "1", "-W", str(TIMEOUT_SEGUNDOS), host]

    try:
        # subprocess.run executa o comando e captura o resultado
        resultado = subprocess.run(
            comando,
            stdout=subprocess.DEVNULL,  # Esconde a saída do ping na tela
            stderr=subprocess.DEVNULL,  # Esconde erros na tela
            timeout=TIMEOUT_SEGUNDOS + 2
        )
        # Código 0 significa sucesso no ping
        return resultado.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False


def testar_porta(host, porta):
    """
    Testa se uma porta específica está acessível no host.
    Retorna True se a porta estiver aberta, False caso contrário.
    """
    try:
        # Cria uma conexão TCP simples para testar a porta
        conexao = socket.create_connection((host, porta), timeout=TIMEOUT_SEGUNDOS)
        conexao.close()  # Fecha a conexão logo após o teste
        return True
    except (socket.timeout, socket.error, OSError):
        return False


def verificar_servidor(servidor):
    """
    Executa os testes de ping e porta para um servidor.
    Retorna um dicionário com os resultados.
    """
    nome  = servidor["nome"]
    host  = servidor["host"]
    porta = servidor["porta"]

    print(f"  Testando {nome} ({host})...", end=" ", flush=True)

    ping_ok  = testar_ping(host)
    porta_ok = testar_porta(host, porta)

    # Define o status geral: OK somente se ambos passarem
    if ping_ok and porta_ok:
        status = "OK"
    elif ping_ok and not porta_ok:
        status = "PING OK / PORTA FECHADA"
    elif not ping_ok and porta_ok:
        status = "PING FALHOU / PORTA ABERTA"
    else:
        status = "FALHOU"

    print(status)

    return {
        "nome":     nome,
        "host":     host,
        "porta":    porta,
        "ping":     "OK" if ping_ok  else "FALHOU",
        "porta_ok": "ABERTA" if porta_ok else "FECHADA",
        "status":   status,
    }


def gerar_relatorio(resultados):
    """
    Grava os resultados em um arquivo .txt formatado.
    """
    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Conta quantos servidores passaram e quantos falharam
    total   = len(resultados)
    ok      = sum(1 for r in resultados if r["status"] == "OK")
    falha   = total - ok

    linhas = []
    linhas.append("=" * 60)
    linhas.append("  RELATÓRIO DE CONECTIVIDADE")
    linhas.append(f"  Gerado em: {agora}")
    linhas.append("=" * 60)
    linhas.append(f"  Total de servidores testados : {total}")
    linhas.append(f"  Com conectividade OK         : {ok}")
    linhas.append(f"  Com falha                    : {falha}")
    linhas.append("=" * 60)
    linhas.append("")

    for r in resultados:
        linhas.append(f"Servidor : {r['nome']}")
        linhas.append(f"  Host   : {r['host']}")
        linhas.append(f"  Porta  : {r['porta']}")
        linhas.append(f"  Ping   : {r['ping']}")
        linhas.append(f"  Porta  : {r['porta_ok']}")
        linhas.append(f"  Status : {r['status']}")
        linhas.append("-" * 40)

    linhas.append("")
    linhas.append("Fim do relatório.")

    # Escreve tudo no arquivo
    with open(ARQUIVO_RELATORIO, "w", encoding="utf-8") as arquivo:
        arquivo.write("\n".join(linhas))

    print(f"\nRelatório salvo em: {ARQUIVO_RELATORIO}")


# =============================================================
#  EXECUÇÃO PRINCIPAL
# =============================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  VERIFICADOR DE CONECTIVIDADE")
    print("=" * 60)
    print(f"  Testando {len(SERVIDORES)} servidor(es)...\n")

    resultados = []
    for servidor in SERVIDORES:
        resultado = verificar_servidor(servidor)
        resultados.append(resultado)

    gerar_relatorio(resultados)
    print("\nConcluído!")
