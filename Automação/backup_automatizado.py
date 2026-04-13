"""
=============================================================
  BACKUP AUTOMATIZADO
  Compacta uma pasta em .zip com data/hora no nome
  e salva em outro diretório
=============================================================
  Como usar:
    1. Configure as variáveis abaixo
    2. Execute: python backup_automatizado.py
    3. O .zip será criado na pasta de destino
    4. Opcionalmente, agende no Agendador de Tarefas

  Não requer instalação de bibliotecas externas.
=============================================================
"""

import os           # Para verificar pastas e arquivos
import zipfile      # Para criar o arquivo .zip
import datetime     # Para o timestamp no nome do backup
import shutil       # Para calcular tamanho de pasta
import time         # Para medir tempo de execução

# =============================================================
#  CONFIGURAÇÕES
# =============================================================

# Lista de pastas para fazer backup
# Cada item tem: nome amigável, pasta de origem e pasta de destino
BACKUPS = [
    {
        "nome":    "Documentos",
        "origem":  "C:/Users/SeuUsuario/Documents",
        "destino": "D:/Backups/Documentos",
    },
    {
        "nome":    "Configurações do Sistema",
        "origem":  "C:/Configs",
        "destino": "D:/Backups/Configs",
    },
    # Adicione mais entradas conforme necessário
]

# Manter apenas os N backups mais recentes por pasta
# Use 0 para manter todos
MANTER_ULTIMOS = 5

# Extensões a IGNORAR no backup (arquivos temporários)
IGNORAR_EXTENSOES = [".tmp", ".temp", ".log", "~"]

# Arquivo de log de execuções
ARQUIVO_LOG = "log_backup.txt"

# =============================================================
#  FUNÇÕES
# =============================================================

def tamanho_legivel(bytes_):
    """Converte bytes para formato legível (KB, MB, GB)."""
    for unidade in ["B", "KB", "MB", "GB"]:
        if bytes_ < 1024:
            return f"{bytes_:.1f} {unidade}"
        bytes_ /= 1024
    return f"{bytes_:.1f} TB"


def gerar_nome_zip(nome_backup):
    """
    Gera o nome do arquivo .zip com timestamp.
    Exemplo: Documentos_2025-04-13_14-30-00.zip
    """
    agora = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # Remove espaços e caracteres inválidos do nome
    nome_limpo = nome_backup.replace(" ", "_")
    return f"{nome_limpo}_{agora}.zip"


def deve_ignorar(nome_arquivo):
    """Retorna True se o arquivo deve ser ignorado no backup."""
    _, ext = os.path.splitext(nome_arquivo)
    return ext.lower() in [e.lower() for e in IGNORAR_EXTENSOES]


def compactar_pasta(origem, caminho_zip):
    """
    Percorre toda a pasta de origem e adiciona ao .zip.
    Mantém a estrutura de subpastas dentro do arquivo.
    Retorna contagem de arquivos e tamanho total.
    """
    total_arquivos = 0
    total_bytes = 0

    with zipfile.ZipFile(caminho_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for raiz, pastas, arquivos in os.walk(origem):
            for arquivo in arquivos:
                if deve_ignorar(arquivo):
                    continue

                caminho_completo = os.path.join(raiz, arquivo)

                # arcname = caminho relativo dentro do .zip
                # Isso preserva a estrutura de pastas
                arcname = os.path.relpath(caminho_completo, origem)

                try:
                    zf.write(caminho_completo, arcname)
                    total_bytes += os.path.getsize(caminho_completo)
                    total_arquivos += 1
                except (PermissionError, OSError) as e:
                    print(f"    [AVISO] Não foi possível incluir: {caminho_completo} — {e}")

    return total_arquivos, total_bytes


def limpar_backups_antigos(pasta_destino, nome_backup):
    """
    Mantém apenas os N backups mais recentes.
    Remove os mais antigos se MANTER_ULTIMOS > 0.
    """
    if MANTER_ULTIMOS <= 0:
        return

    nome_limpo = nome_backup.replace(" ", "_")

    # Lista todos os .zip desta origem na pasta de destino
    todos = [
        f for f in os.listdir(pasta_destino)
        if f.startswith(nome_limpo) and f.endswith(".zip")
    ]

    # Ordena do mais antigo para o mais novo
    todos.sort()

    # Se tiver mais que o limite, apaga os mais antigos
    excesso = len(todos) - MANTER_ULTIMOS
    if excesso > 0:
        for arquivo in todos[:excesso]:
            caminho = os.path.join(pasta_destino, arquivo)
            os.remove(caminho)
            print(f"    [REMOVIDO] Backup antigo: {arquivo}")


def executar_backup(config):
    """
    Executa o backup de uma entrada da lista BACKUPS.
    Retorna um dicionário com o resultado.
    """
    nome    = config["nome"]
    origem  = config["origem"]
    destino = config["destino"]

    print(f"\n  Backup: {nome}")
    print(f"  Origem : {origem}")
    print(f"  Destino: {destino}")

    # Verificações iniciais
    if not os.path.exists(origem):
        mensagem = f"ERRO: Pasta de origem não encontrada — {origem}"
        print(f"  {mensagem}")
        return {"nome": nome, "status": "ERRO", "detalhe": mensagem}

    # Cria a pasta de destino se não existir
    os.makedirs(destino, exist_ok=True)

    nome_zip     = gerar_nome_zip(nome)
    caminho_zip  = os.path.join(destino, nome_zip)

    inicio = time.time()
    print(f"  Compactando...", end=" ", flush=True)

    try:
        qtd_arquivos, tamanho_original = compactar_pasta(origem, caminho_zip)
        tamanho_zip = os.path.getsize(caminho_zip)
        tempo = time.time() - inicio

        print(f"concluído em {tempo:.1f}s")
        print(f"  Arquivo  : {nome_zip}")
        print(f"  Arquivos : {qtd_arquivos}")
        print(f"  Original : {tamanho_legivel(tamanho_original)}")
        print(f"  ZIP      : {tamanho_legivel(tamanho_zip)}")

        # Remove backups antigos se configurado
        limpar_backups_antigos(destino, nome)

        return {
            "nome":      nome,
            "status":    "OK",
            "arquivo":   nome_zip,
            "arquivos":  qtd_arquivos,
            "tamanho":   tamanho_legivel(tamanho_zip),
            "tempo_s":   round(tempo, 1),
        }

    except Exception as erro:
        # Remove o .zip incompleto se houve falha
        if os.path.exists(caminho_zip):
            os.remove(caminho_zip)
        mensagem = str(erro)
        print(f"ERRO: {mensagem}")
        return {"nome": nome, "status": "ERRO", "detalhe": mensagem}


def registrar_log(resultados, tempo_total):
    """Salva o resumo da execução no arquivo de log."""
    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    linhas = [
        "",
        "=" * 55,
        f"BACKUP — {agora} — {tempo_total:.1f}s total",
    ]
    for r in resultados:
        if r["status"] == "OK":
            linhas.append(
                f"  [OK] {r['nome']} — {r['arquivo']} — "
                f"{r['arquivos']} arquivos — {r['tamanho']} — {r['tempo_s']}s"
            )
        else:
            linhas.append(f"  [ERRO] {r['nome']} — {r.get('detalhe', '')}")

    with open(ARQUIVO_LOG, "a", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")


# =============================================================
#  EXECUÇÃO PRINCIPAL
# =============================================================

if __name__ == "__main__":
    inicio_geral = time.time()

    print("\n" + "=" * 55)
    print("  BACKUP AUTOMATIZADO")
    print("=" * 55)
    print(f"  {len(BACKUPS)} pasta(s) configurada(s) para backup")
    print(f"  Manter últimos: {MANTER_ULTIMOS if MANTER_ULTIMOS > 0 else 'todos'}")
    print("=" * 55)

    resultados = []
    for config in BACKUPS:
        resultado = executar_backup(config)
        resultados.append(resultado)

    tempo_total = time.time() - inicio_geral
    ok    = sum(1 for r in resultados if r["status"] == "OK")
    erros = len(resultados) - ok

    print("\n" + "=" * 55)
    print(f"  RESUMO: {ok} OK | {erros} erro(s) | {tempo_total:.1f}s total")
    print("=" * 55)

    registrar_log(resultados, tempo_total)
    print(f"\n  Log salvo em: {ARQUIVO_LOG}")
    print("\n  Concluído!")
