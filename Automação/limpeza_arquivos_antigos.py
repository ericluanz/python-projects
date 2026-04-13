"""
=============================================================
  LIMPEZA DE ARQUIVOS ANTIGOS
  Varre uma pasta e move ou apaga arquivos com mais de X dias
  Ideal para pastas de log, backups temporários e downloads
=============================================================
  Como usar:
    1. Configure as variáveis abaixo
    2. Execute: python limpeza_arquivos_antigos.py
    3. Confira o log gerado antes de ativar a exclusão real

  Não requer instalação de bibliotecas externas.
=============================================================
"""

import os           # Para listar e apagar arquivos
import shutil       # Para mover arquivos
import datetime     # Para calcular a idade dos arquivos
import time         # Para ler a data de modificação

# =============================================================
#  CONFIGURAÇÕES
# =============================================================

# Pasta que será varrida (use barras normais / ou duplas \\)
PASTA_ALVO = "C:/Logs"

# Arquivos com mais de X dias serão processados
DIAS_LIMITE = 30

# O que fazer com os arquivos antigos:
#   "apagar" — exclui permanentemente
#   "mover"  — move para PASTA_DESTINO
ACAO = "mover"

# Usado apenas quando ACAO = "mover"
PASTA_DESTINO = "C:/Logs/Antigos"

# Extensões de arquivo a considerar (lista)
# Use ["*"] para processar todos os tipos
EXTENSOES = [".log", ".txt", ".bak", ".tmp"]

# Se True, varre também subpastas dentro de PASTA_ALVO
INCLUIR_SUBPASTAS = True

# Se True, apenas simula as ações sem alterar nada (modo seguro)
# Recomendado deixar True na primeira execução para revisar
MODO_SIMULACAO = True

ARQUIVO_LOG = "log_limpeza.txt"

# =============================================================
#  FUNÇÕES
# =============================================================

def calcular_idade_dias(caminho_arquivo):
    """Retorna quantos dias se passaram desde a última modificação."""
    timestamp = os.path.getmtime(caminho_arquivo)
    data_modificacao = datetime.datetime.fromtimestamp(timestamp)
    agora = datetime.datetime.now()
    return (agora - data_modificacao).days


def extensao_permitida(nome_arquivo):
    """Verifica se a extensão do arquivo está na lista configurada."""
    if EXTENSOES == ["*"]:
        return True
    _, ext = os.path.splitext(nome_arquivo)
    return ext.lower() in [e.lower() for e in EXTENSOES]


def registrar_log(linhas):
    """Salva as linhas de resultado no arquivo de log."""
    with open(ARQUIVO_LOG, "a", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")


def processar_arquivo(caminho, idade_dias, stats):
    """
    Executa a ação configurada (apagar ou mover) num arquivo.
    Em modo simulação, apenas registra o que faria.
    """
    nome = os.path.basename(caminho)

    if MODO_SIMULACAO:
        stats["simulados"] += 1
        return f"  [SIMULAÇÃO] {ACAO.upper()} → {caminho} ({idade_dias} dias)"

    try:
        if ACAO == "apagar":
            os.remove(caminho)
            stats["processados"] += 1
            return f"  [APAGADO] {caminho} ({idade_dias} dias)"

        elif ACAO == "mover":
            # Cria a pasta destino se não existir
            os.makedirs(PASTA_DESTINO, exist_ok=True)
            destino = os.path.join(PASTA_DESTINO, nome)

            # Se já existe um arquivo com o mesmo nome no destino,
            # adiciona timestamp para não sobrescrever
            if os.path.exists(destino):
                base, ext = os.path.splitext(nome)
                ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                destino = os.path.join(PASTA_DESTINO, f"{base}_{ts}{ext}")

            shutil.move(caminho, destino)
            stats["processados"] += 1
            return f"  [MOVIDO] {caminho} → {destino} ({idade_dias} dias)"

    except Exception as erro:
        stats["erros"] += 1
        return f"  [ERRO] {caminho} — {erro}"


def varrer_pasta(pasta, stats, linhas_log):
    """
    Varre a pasta recursivamente (ou não) e processa arquivos antigos.
    """
    try:
        entradas = os.listdir(pasta)
    except PermissionError:
        linhas_log.append(f"  [SEM ACESSO] {pasta}")
        return

    for entrada in entradas:
        caminho = os.path.join(pasta, entrada)

        # Se for subpasta e INCLUIR_SUBPASTAS estiver ativo, entra recursivamente
        if os.path.isdir(caminho):
            if INCLUIR_SUBPASTAS:
                varrer_pasta(caminho, stats, linhas_log)
            continue

        # Ignora se a extensão não estiver na lista
        if not extensao_permitida(entrada):
            stats["ignorados"] += 1
            continue

        idade = calcular_idade_dias(caminho)
        stats["total"] += 1

        if idade >= DIAS_LIMITE:
            resultado = processar_arquivo(caminho, idade, stats)
            linhas_log.append(resultado)
            print(resultado)
        else:
            stats["dentro_do_prazo"] += 1


def executar_limpeza():
    """Função principal que orquestra toda a limpeza."""
    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    print("\n" + "=" * 55)
    print("  LIMPEZA DE ARQUIVOS ANTIGOS")
    if MODO_SIMULACAO:
        print("  *** MODO SIMULAÇÃO — nenhum arquivo será alterado ***")
    print("=" * 55)
    print(f"  Pasta alvo   : {PASTA_ALVO}")
    print(f"  Ação         : {ACAO.upper()}")
    print(f"  Limite       : arquivos com mais de {DIAS_LIMITE} dias")
    print(f"  Extensões    : {', '.join(EXTENSOES)}")
    print(f"  Subpastas    : {'Sim' if INCLUIR_SUBPASTAS else 'Não'}")
    print("=" * 55 + "\n")

    if not os.path.exists(PASTA_ALVO):
        print(f"ERRO: A pasta '{PASTA_ALVO}' não existe.")
        return

    stats = {
        "total": 0,
        "processados": 0,
        "simulados": 0,
        "dentro_do_prazo": 0,
        "ignorados": 0,
        "erros": 0,
    }
    linhas_log = [
        "=" * 55,
        f"LIMPEZA — {agora}",
        f"Pasta: {PASTA_ALVO} | Ação: {ACAO} | Limite: {DIAS_LIMITE} dias",
        f"Modo simulação: {'SIM' if MODO_SIMULACAO else 'NÃO'}",
        "=" * 55,
    ]

    varrer_pasta(PASTA_ALVO, stats, linhas_log)

    # Resumo final
    processados = stats["simulados"] if MODO_SIMULACAO else stats["processados"]
    resumo = [
        "",
        "-" * 45,
        f"Arquivos verificados     : {stats['total']}",
        f"Processados/Simulados    : {processados}",
        f"Dentro do prazo          : {stats['dentro_do_prazo']}",
        f"Ignorados (ext.)         : {stats['ignorados']}",
        f"Erros                    : {stats['erros']}",
        "-" * 45,
    ]

    print("\n" + "\n".join(resumo))
    linhas_log.extend(resumo)
    registrar_log(linhas_log)

    print(f"\n  Log salvo em: {ARQUIVO_LOG}")
    if MODO_SIMULACAO:
        print("\n  Para executar de verdade, mude MODO_SIMULACAO = False")
    print("\n  Concluído!")


# =============================================================
#  EXECUÇÃO PRINCIPAL
# =============================================================

if __name__ == "__main__":
    executar_limpeza()
