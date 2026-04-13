"""
=============================================================
  SCANNER DE PORTAS
  Verifica quais portas estão abertas em um IP ou hostname
  Útil para troubleshooting e auditoria básica de rede
=============================================================
  Como usar:
    1. Execute: python scanner_portas.py
    2. Informe o IP ou hostname quando solicitado
    3. Escolha o modo de scan
    4. O resultado é exibido e salvo em arquivo .txt

  Não requer instalação de bibliotecas externas.

  ATENÇÃO: Use somente em redes e equipamentos que você
  tem permissão para auditar.
=============================================================
"""

import socket       # Para testar as conexões TCP
import datetime     # Para registrar data/hora
import concurrent.futures  # Para testar várias portas ao mesmo tempo (mais rápido)

# =============================================================
#  CONFIGURAÇÕES
# =============================================================

TIMEOUT_SEGUNDOS = 1        # Tempo de espera por porta (menor = mais rápido)
MAX_THREADS = 100           # Quantas portas testar em paralelo
ARQUIVO_RESULTADO = "resultado_scan.txt"

# Grupos de portas pré-definidos para scan rápido
PORTAS_CONHECIDAS = {
    21:   "FTP",
    22:   "SSH",
    23:   "Telnet",
    25:   "SMTP",
    53:   "DNS",
    80:   "HTTP",
    110:  "POP3",
    135:  "RPC",
    139:  "NetBIOS",
    143:  "IMAP",
    161:  "SNMP",
    389:  "LDAP",
    443:  "HTTPS",
    445:  "SMB",
    636:  "LDAPS",
    1433: "SQL Server",
    1521: "Oracle DB",
    3306: "MySQL",
    3389: "RDP (Área de Trabalho Remota)",
    5432: "PostgreSQL",
    5985: "WinRM HTTP",
    5986: "WinRM HTTPS",
    6379: "Redis",
    8080: "HTTP Alternativo",
    8443: "HTTPS Alternativo",
    9090: "Webmin / Admin Web",
    27017:"MongoDB",
}

# =============================================================
#  FUNÇÕES
# =============================================================

def testar_porta(host, porta):
    """
    Tenta abrir uma conexão TCP na porta informada.
    Retorna True se estiver aberta, False caso contrário.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT_SEGUNDOS)
        resultado = sock.connect_ex((host, porta))  # 0 = sucesso
        sock.close()
        return resultado == 0
    except (socket.error, OSError):
        return False


def resolver_host(host):
    """
    Resolve o hostname para IP.
    Retorna o IP ou None se não conseguir resolver.
    """
    try:
        ip = socket.gethostbyname(host)
        return ip
    except socket.gaierror:
        return None


def scan_lista_portas(host, lista_portas):
    """
    Escaneia uma lista de portas em paralelo usando threads.
    Retorna uma lista de portas abertas.
    """
    abertas = []

    # ThreadPoolExecutor roda múltiplos testes simultaneamente
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        # Cria um "mapa" de porta → resultado futuro
        futuros = {executor.submit(testar_porta, host, p): p for p in lista_portas}

        for futuro in concurrent.futures.as_completed(futuros):
            porta = futuros[futuro]
            try:
                if futuro.result():
                    abertas.append(porta)
            except Exception:
                pass

    return sorted(abertas)  # Retorna em ordem crescente


def obter_servico(porta):
    """Retorna o nome do serviço associado à porta, se conhecido."""
    # Primeiro verifica no nosso dicionário local
    if porta in PORTAS_CONHECIDAS:
        return PORTAS_CONHECIDAS[porta]
    # Depois tenta o banco do próprio sistema
    try:
        return socket.getservbyport(porta)
    except OSError:
        return "Serviço desconhecido"


def exibir_e_salvar(host, ip, portas_abertas, total_testadas, tempo):
    """Formata e exibe o resultado, e salva em arquivo .txt."""
    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    linhas = []

    linhas.append("=" * 55)
    linhas.append("  RESULTADO DO SCAN DE PORTAS")
    linhas.append(f"  Data/Hora  : {agora}")
    linhas.append(f"  Alvo       : {host}")
    linhas.append(f"  IP         : {ip}")
    linhas.append(f"  Testadas   : {total_testadas} portas em {tempo:.1f}s")
    linhas.append(f"  Abertas    : {len(portas_abertas)}")
    linhas.append("=" * 55)

    if portas_abertas:
        linhas.append(f"\n  {'PORTA':<8} {'SERVIÇO'}")
        linhas.append(f"  {'-'*7}  {'-'*30}")
        for porta in portas_abertas:
            servico = obter_servico(porta)
            linhas.append(f"  {porta:<8} {servico}")
    else:
        linhas.append("\n  Nenhuma porta aberta encontrada.")

    linhas.append("\n" + "=" * 55)

    # Exibe no terminal
    for linha in linhas:
        print(linha)

    # Salva em arquivo
    with open(ARQUIVO_RESULTADO, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))

    print(f"\n  Resultado salvo em: {ARQUIVO_RESULTADO}")


def menu_portas():
    """Exibe o menu de escolha e retorna a lista de portas a escanear."""
    print("\n  Escolha o modo de scan:")
    print("  1 — Portas conhecidas (serviços comuns — rápido)")
    print("  2 — Top 1000 portas (mais abrangente)")
    print("  3 — Faixa personalizada (ex: 1-65535)")
    print("  4 — Porta(s) específica(s) (ex: 80,443,3389)")

    modo = input("\n  Opção (1-4): ").strip()

    if modo == "1":
        return list(PORTAS_CONHECIDAS.keys()), "portas conhecidas"

    elif modo == "2":
        return list(range(1, 1001)), "top 1000"

    elif modo == "3":
        faixa = input("  Digite a faixa (ex: 1-1024): ").strip()
        try:
            inicio, fim = map(int, faixa.split("-"))
            return list(range(inicio, fim + 1)), f"faixa {inicio}-{fim}"
        except ValueError:
            print("  Formato inválido. Usando portas conhecidas.")
            return list(PORTAS_CONHECIDAS.keys()), "portas conhecidas"

    elif modo == "4":
        entrada = input("  Digite as portas separadas por vírgula (ex: 80,443,3389): ").strip()
        try:
            portas = [int(p.strip()) for p in entrada.split(",")]
            return portas, f"{len(portas)} porta(s) específica(s)"
        except ValueError:
            print("  Formato inválido. Usando portas conhecidas.")
            return list(PORTAS_CONHECIDAS.keys()), "portas conhecidas"

    else:
        print("  Opção inválida. Usando portas conhecidas.")
        return list(PORTAS_CONHECIDAS.keys()), "portas conhecidas"


# =============================================================
#  EXECUÇÃO PRINCIPAL
# =============================================================

if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  SCANNER DE PORTAS")
    print("=" * 55)

    host = input("\n  IP ou hostname alvo: ").strip()
    if not host:
        print("  Nenhum alvo informado. Encerrando.")
        exit(0)

    # Resolve o hostname para IP
    ip = resolver_host(host)
    if not ip:
        print(f"\n  ERRO: Não foi possível resolver '{host}'.")
        exit(1)

    print(f"  Host resolvido: {ip}")

    lista_portas, descricao = menu_portas()

    print(f"\n  Iniciando scan ({descricao})...")
    print(f"  Testando {len(lista_portas)} porta(s) com {MAX_THREADS} threads...\n")

    inicio = datetime.datetime.now()
    portas_abertas = scan_lista_portas(ip, lista_portas)
    tempo = (datetime.datetime.now() - inicio).total_seconds()

    exibir_e_salvar(host, ip, portas_abertas, len(lista_portas), tempo)
    print("\n  Concluído!")
