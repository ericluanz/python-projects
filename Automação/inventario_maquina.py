"""
=============================================================
  INVENTÁRIO DE MÁQUINA — WINDOWS
  Coleta informações de hardware e sistema operacional
  e exporta em arquivo CSV para controle de ativos
=============================================================
  Como usar:
    1. Execute: python inventario_maquina.py
    2. O arquivo CSV será salvo na mesma pasta do script
    3. Abra no Excel para visualizar e filtrar os dados

  Dependência externa necessária:
    pip install psutil
=============================================================
"""

import csv          # Para gerar o arquivo CSV
import datetime     # Para registrar data/hora da coleta
import socket       # Para pegar o nome e IP da máquina
import platform     # Para informações do sistema operacional
import os           # Para operações de arquivo e variáveis de ambiente

# psutil é a biblioteca que lê hardware (CPU, RAM, disco)
# Instale com: pip install psutil
try:
    import psutil
except ImportError:
    print("ERRO: A biblioteca 'psutil' não está instalada.")
    print("Execute no terminal: pip install psutil")
    exit(1)

# =============================================================
#  CONFIGURAÇÕES
# =============================================================

ARQUIVO_CSV = "inventario_maquinas.csv"   # Nome do arquivo de saída

# =============================================================
#  FUNÇÕES DE COLETA
# =============================================================

def coletar_sistema_operacional():
    """Retorna informações do sistema operacional."""
    return {
        "so_nome":    platform.system(),                    # Ex: Windows
        "so_versao":  platform.version(),                   # Versão completa
        "so_release": platform.release(),                   # Ex: 10, 11
        "arquitetura": platform.machine(),                  # Ex: AMD64
    }


def coletar_cpu():
    """Retorna informações do processador."""
    return {
        "cpu_modelo":   platform.processor(),               # Nome do processador
        "cpu_nucleos":  psutil.cpu_count(logical=False),    # Núcleos físicos
        "cpu_threads":  psutil.cpu_count(logical=True),     # Threads lógicas
        "cpu_freq_mhz": round(psutil.cpu_freq().max) if psutil.cpu_freq() else "N/A",
    }


def coletar_ram():
    """Retorna informações de memória RAM."""
    ram = psutil.virtual_memory()
    # Converte bytes para GB com 1 casa decimal
    total_gb = round(ram.total / (1024 ** 3), 1)
    usado_gb  = round(ram.used  / (1024 ** 3), 1)
    livre_gb  = round(ram.available / (1024 ** 3), 1)
    return {
        "ram_total_gb": total_gb,
        "ram_usado_gb": usado_gb,
        "ram_livre_gb": livre_gb,
        "ram_uso_pct":  ram.percent,   # Percentual em uso
    }


def coletar_disco():
    """
    Retorna informações das partições de disco.
    Agrupa todos os discos em uma string para caber numa célula do CSV.
    """
    discos = []
    for particao in psutil.disk_partitions():
        try:
            uso = psutil.disk_usage(particao.mountpoint)
            total_gb = round(uso.total / (1024 ** 3), 1)
            livre_gb  = round(uso.free  / (1024 ** 3), 1)
            usado_pct = uso.percent
            discos.append(
                f"{particao.device} {total_gb}GB total / {livre_gb}GB livre ({usado_pct}% usado)"
            )
        except PermissionError:
            # Alguns drives especiais bloqueiam o acesso — pulamos
            continue

    return {
        "discos": " | ".join(discos) if discos else "N/A"
    }


def coletar_rede():
    """Retorna hostname e endereço IP principal da máquina."""
    hostname = socket.gethostname()
    try:
        ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        ip = "N/A"
    return {
        "hostname": hostname,
        "ip":       ip,
    }


def coletar_usuario():
    """Retorna o usuário Windows atualmente logado."""
    usuario = os.environ.get("USERNAME") or os.environ.get("USER") or "N/A"
    dominio  = os.environ.get("USERDOMAIN") or "N/A"
    return {
        "usuario": usuario,
        "dominio": dominio,
    }


def coletar_tudo():
    """
    Chama todas as funções de coleta e junta tudo num único dicionário.
    Cada chave vira uma coluna no CSV.
    """
    dados = {}
    dados["data_coleta"] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Atualiza o dicionário com cada grupo de informações
    dados.update(coletar_rede())
    dados.update(coletar_usuario())
    dados.update(coletar_sistema_operacional())
    dados.update(coletar_cpu())
    dados.update(coletar_ram())
    dados.update(coletar_disco())

    return dados


# =============================================================
#  FUNÇÃO DE EXPORTAÇÃO CSV
# =============================================================

def salvar_csv(dados):
    """
    Salva os dados no arquivo CSV.
    - Se o arquivo não existir, cria com cabeçalho (nomes das colunas).
    - Se já existir, apenas adiciona uma nova linha ao final.
    Isso permite rodar o script em várias máquinas e acumular no mesmo CSV.
    """
    colunas = list(dados.keys())     # Nomes das colunas = chaves do dicionário
    arquivo_novo = not os.path.exists(ARQUIVO_CSV)

    # "a" = append (adiciona sem apagar o que já existe)
    with open(ARQUIVO_CSV, mode="a", newline="", encoding="utf-8-sig") as f:
        # utf-8-sig garante que o Excel abre sem problemas de acentuação
        writer = csv.DictWriter(f, fieldnames=colunas)

        if arquivo_novo:
            writer.writeheader()   # Escreve a linha de cabeçalho só na primeira vez

        writer.writerow(dados)     # Escreve os dados da máquina atual

    print(f"\nDados salvos em: {ARQUIVO_CSV}")


def exibir_resumo(dados):
    """Exibe um resumo legível no terminal antes de salvar."""
    print("\n" + "=" * 55)
    print("  INVENTÁRIO COLETADO")
    print("=" * 55)
    print(f"  Data/Hora  : {dados['data_coleta']}")
    print(f"  Hostname   : {dados['hostname']}")
    print(f"  IP         : {dados['ip']}")
    print(f"  Usuário    : {dados['dominio']}\\{dados['usuario']}")
    print(f"  Sistema    : {dados['so_nome']} {dados['so_release']}")
    print(f"  CPU        : {dados['cpu_modelo']}")
    print(f"             : {dados['cpu_nucleos']} núcleos / {dados['cpu_threads']} threads @ {dados['cpu_freq_mhz']} MHz")
    print(f"  RAM        : {dados['ram_total_gb']} GB total / {dados['ram_livre_gb']} GB livre ({dados['ram_uso_pct']}% em uso)")
    print(f"  Disco(s)   : {dados['discos']}")
    print("=" * 55)


# =============================================================
#  EXECUÇÃO PRINCIPAL
# =============================================================

if __name__ == "__main__":
    print("\nColetando informações da máquina...")

    dados = coletar_tudo()
    exibir_resumo(dados)
    salvar_csv(dados)

    print("\nConcluído! Abra o CSV no Excel para visualizar.")
