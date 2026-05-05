"""
=============================================================
  CARTOLA FC - APP DE TERMINAL
=============================================================
  Autor: Eric (com Claude)
  Descrição: Aplicativo de linha de comando que consome a
  API do Cartola FC para análise de mercado, sugestão de
  escalação e acompanhamento de parciais.

  Como rodar:
      1. Instale as dependências:  pip install requests
      2. Execute:                  python cartola_app.py

  IMPORTANTE: Este script usa endpoints PÚBLICOS da API do
  Cartola FC (sem autenticação). Endpoints que exigem login
  (seu time pessoal, ligas privadas) não estão incluídos.
=============================================================
"""

import requests
import time
from typing import Optional


# ============================================================
# CONFIGURAÇÃO
# ============================================================

API_BASE = "https://api.cartolafc.globo.com"

# Headers ajudam a evitar bloqueios e simulam um navegador comum
HEADERS = {
    "User-Agent": "Mozilla/5.0 (CartolaApp/1.0 - estudo educacional)",
    "Accept": "application/json",
}

# Mapeamento de IDs de posição da API → nome legível
POSICOES = {
    1: "Goleiro",
    2: "Lateral",
    3: "Zagueiro",
    4: "Meia",
    5: "Atacante",
    6: "Técnico",
}

# Status do mercado
STATUS_MERCADO = {
    1: "ABERTO ✅",
    2: "FECHADO 🔒",
    3: "ATUALIZAÇÃO ⚙️",
    4: "MANUTENÇÃO 🛠️",
    6: "ENCERRADO 🏁",
}

# Status do atleta (provável, dúvida, suspenso, etc)
STATUS_ATLETA = {
    2: "Dúvida",
    3: "Suspenso",
    5: "Contundido",
    6: "Nulo",
    7: "Provável",
}


# ============================================================
# FUNÇÕES UTILITÁRIAS DE REQUISIÇÃO
# ============================================================

def fazer_requisicao(endpoint: str) -> Optional[dict]:
    """
    Faz uma requisição GET na API do Cartola FC.

    Args:
        endpoint: caminho da rota (ex: '/mercado/status')

    Returns:
        Dicionário com a resposta JSON, ou None em caso de erro.
    """
    url = f"{API_BASE}{endpoint}"
    try:
        resposta = requests.get(url, headers=HEADERS, timeout=15)
        resposta.raise_for_status()  # levanta erro se status >= 400
        return resposta.json()
    except requests.exceptions.Timeout:
        print(f"⚠️  Timeout ao acessar {endpoint}")
    except requests.exceptions.HTTPError as e:
        print(f"⚠️  Erro HTTP {e.response.status_code} em {endpoint}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Erro de rede: {e}")
    except ValueError:
        print(f"⚠️  Resposta inválida (não é JSON) em {endpoint}")
    return None


def limpar_tela():
    """Imprime linhas em branco pra 'limpar' visualmente o terminal."""
    print("\n" * 2)


def pausar():
    """Aguarda o usuário pressionar Enter."""
    input("\n[ Pressione ENTER para voltar ao menu ]")


# ============================================================
# FUNCIONALIDADE 1: STATUS DO MERCADO
# ============================================================

def ver_status_mercado():
    """Mostra a rodada atual e se o mercado está aberto/fechado."""
    print("\n📊 STATUS DO MERCADO")
    print("=" * 50)

    dados = fazer_requisicao("/mercado/status")
    if not dados:
        return

    status_id = dados.get("status_mercado")
    status_nome = STATUS_MERCADO.get(status_id, f"Desconhecido ({status_id})")

    print(f"  Rodada atual:        {dados.get('rodada_atual')}")
    print(f"  Status do mercado:   {status_nome}")
    print(f"  Times escalados:     {dados.get('times_escalados'):,}".replace(",", "."))

    if dados.get("fechamento"):
        f = dados["fechamento"]
        print(f"  Fechamento:          {f.get('dia'):02d}/{f.get('mes'):02d} "
              f"às {f.get('hora'):02d}:{f.get('minuto'):02d}")

    if dados.get("aviso"):
        print(f"\n  ℹ️  Aviso: {dados['aviso']}")


# ============================================================
# FUNCIONALIDADE 2: MERCADO DE ATLETAS
# ============================================================

def buscar_atletas_mercado() -> Optional[dict]:
    """Busca a lista completa de atletas e clubes do mercado."""
    print("⏳ Carregando mercado de atletas...")
    return fazer_requisicao("/atletas/mercado")


def filtrar_atletas(dados: dict, posicao_id: Optional[int] = None,
                    preco_max: Optional[float] = None,
                    apenas_provaveis: bool = True) -> list:
    """
    Filtra atletas por posição, preço e status.

    Args:
        dados: resposta da API /atletas/mercado
        posicao_id: 1-6 (None = todas)
        preco_max: preço máximo em cartoletas (None = sem limite)
        apenas_provaveis: só retorna jogadores prováveis

    Returns:
        Lista de atletas que passaram nos filtros, ordenada por
        média (maior → menor).
    """
    atletas = dados.get("atletas", [])
    filtrados = []

    for at in atletas:
        if posicao_id and at.get("posicao_id") != posicao_id:
            continue
        if preco_max is not None and at.get("preco_num", 0) > preco_max:
            continue
        if apenas_provaveis and at.get("status_id") != 7:
            continue
        filtrados.append(at)

    # Ordena pela média de pontos (maior primeiro)
    filtrados.sort(key=lambda x: x.get("media_num", 0), reverse=True)
    return filtrados


def listar_top_atletas():
    """Lista os melhores atletas filtrados por posição e preço."""
    print("\n🏆 TOP ATLETAS DO MERCADO")
    print("=" * 50)

    print("\n  Posições disponíveis:")
    for pid, pnome in POSICOES.items():
        print(f"    {pid} - {pnome}")

    try:
        pos = input("\n  Posição (1-6, ou ENTER para todas): ").strip()
        posicao_id = int(pos) if pos else None

        preco = input("  Preço máximo em C$ (ENTER = sem limite): ").strip()
        preco_max = float(preco) if preco else None

        qtd = input("  Quantos exibir? (padrão 10): ").strip()
        qtd = int(qtd) if qtd else 10
    except ValueError:
        print("  ❌ Valor inválido. Tente novamente.")
        return

    dados = buscar_atletas_mercado()
    if not dados:
        return

    clubes = dados.get("clubes", {})
    filtrados = filtrar_atletas(dados, posicao_id, preco_max)[:qtd]

    if not filtrados:
        print("\n  Nenhum atleta encontrado com esses filtros.")
        return

    print(f"\n{'Apelido':<20}{'Pos':<10}{'Clube':<18}{'Preço':>8}{'Média':>8}{'Pts Últ.':>10}")
    print("-" * 74)
    for at in filtrados:
        clube_id = str(at.get("clube_id"))
        clube_nome = clubes.get(clube_id, {}).get("abreviacao", "?")
        pos_nome = POSICOES.get(at.get("posicao_id"), "?")
        print(f"{at.get('apelido', '')[:19]:<20}"
              f"{pos_nome:<10}"
              f"{clube_nome:<18}"
              f"{at.get('preco_num', 0):>7.2f} "
              f"{at.get('media_num', 0):>7.2f} "
              f"{at.get('pontos_num', 0):>9.2f}")


# ============================================================
# FUNCIONALIDADE 3: SUGESTÃO DE ESCALAÇÃO (OTIMIZADOR)
# ============================================================

# Esquemas táticos: (defensores, laterais, meias, atacantes)
# Sempre 1 goleiro + 1 técnico = 12 cartolas no total
ESQUEMAS = {
    "3-4-3": {"zag": 3, "lat": 0, "mei": 4, "ata": 3},
    "3-5-2": {"zag": 3, "lat": 0, "mei": 5, "ata": 2},
    "4-3-3": {"zag": 2, "lat": 2, "mei": 3, "ata": 3},
    "4-4-2": {"zag": 2, "lat": 2, "mei": 4, "ata": 2},
    "4-5-1": {"zag": 2, "lat": 2, "mei": 5, "ata": 1},
    "5-3-2": {"zag": 3, "lat": 2, "mei": 3, "ata": 2},
    "5-4-1": {"zag": 3, "lat": 2, "mei": 4, "ata": 1},
}


def selecionar_melhores_por_posicao(atletas: list, posicao_id: int,
                                     qtd: int) -> list:
    """Pega os N melhores atletas de uma posição (ordenados por média)."""
    da_posicao = [a for a in atletas if a.get("posicao_id") == posicao_id]
    da_posicao.sort(key=lambda x: x.get("media_num", 0), reverse=True)
    return da_posicao[:qtd]


def sugerir_escalacao():
    """
    Algoritmo guloso (greedy) para sugerir escalação dentro do orçamento.

    Estratégia:
      1. Para cada posição, pega os jogadores mais bem ranqueados por média
      2. Tenta encaixar no orçamento priorizando os de maior média
      3. Se estourar, troca pelo próximo mais barato da mesma posição
    """
    print("\n🎯 SUGESTÃO DE ESCALAÇÃO")
    print("=" * 50)

    print("\n  Esquemas disponíveis:")
    for esq in ESQUEMAS:
        print(f"    - {esq}")

    esquema = input("\n  Escolha o esquema (padrão 3-4-3): ").strip() or "3-4-3"
    if esquema not in ESQUEMAS:
        print(f"  ❌ Esquema inválido. Usando 3-4-3.")
        esquema = "3-4-3"

    try:
        orcamento = float(input("  Orçamento em C$ (padrão 105): ").strip() or "105")
    except ValueError:
        print("  ❌ Orçamento inválido. Usando 105.")
        orcamento = 105.0

    dados = buscar_atletas_mercado()
    if not dados:
        return

    clubes = dados.get("clubes", {})
    # Só consideramos jogadores prováveis e com média > 0
    provaveis = [a for a in dados.get("atletas", [])
                 if a.get("status_id") == 7 and a.get("media_num", 0) > 0]

    if not provaveis:
        print("  ⚠️  Nenhum jogador provável encontrado (mercado pode estar fechado).")
        return

    formacao = ESQUEMAS[esquema]
    necessarios = {
        1: 1,                        # 1 goleiro
        2: formacao["lat"],          # laterais
        3: formacao["zag"],          # zagueiros
        4: formacao["mei"],          # meias
        5: formacao["ata"],          # atacantes
        6: 1,                        # 1 técnico
    }

    # Pega um pool 3x maior do que precisa pra ter folga na otimização
    pool = {}
    for pos_id, qtd in necessarios.items():
        if qtd > 0:
            pool[pos_id] = selecionar_melhores_por_posicao(provaveis, pos_id, qtd * 3)

    # Estratégia gulosa: pega os melhores; se estourar, troca pelo mais barato
    escalacao = {}
    for pos_id, qtd in necessarios.items():
        if qtd == 0:
            continue
        escalacao[pos_id] = pool[pos_id][:qtd]

    # Calcula custo
    def custo_total(esc):
        return sum(at.get("preco_num", 0)
                   for lista in esc.values() for at in lista)

    custo = custo_total(escalacao)

    # Se estourou, troca os mais caros por opções mais baratas (e ainda boas)
    tentativas = 0
    while custo > orcamento and tentativas < 30:
        # Acha o jogador "mais caro vs custo-benefício" pra trocar
        pior = None
        pior_pos = None
        pior_idx = None
        pior_cb = float("inf")
        for pos_id, lista in escalacao.items():
            for idx, at in enumerate(lista):
                # custo-benefício: preço por unidade de média
                preco = at.get("preco_num", 0.01)
                media = at.get("media_num", 0.01)
                cb = preco / max(media, 0.01)  # quanto menor, melhor
                # queremos trocar quem tem PIOR custo-benefício (cb mais alto)
                # então invertemos: marcamos o de maior cb
                if cb > -pior_cb:
                    pior_cb = -cb
                    pior = at
                    pior_pos = pos_id
                    pior_idx = idx

        # Tenta substituir por alguém mais barato no pool
        atual_id = pior.get("atleta_id")
        em_uso = {a.get("atleta_id") for lst in escalacao.values() for a in lst}
        substitutos = [a for a in pool[pior_pos]
                       if a.get("atleta_id") not in em_uso
                       and a.get("preco_num", 0) < pior.get("preco_num", 0)]
        if not substitutos:
            break  # não dá pra otimizar mais
        substitutos.sort(key=lambda x: x.get("media_num", 0), reverse=True)
        escalacao[pior_pos][pior_idx] = substitutos[0]
        custo = custo_total(escalacao)
        tentativas += 1

    # === Apresenta o resultado ===
    print(f"\n  📋 Escalação sugerida ({esquema})")
    print("  " + "─" * 60)

    media_total = 0
    for pos_id in [1, 3, 2, 4, 5, 6]:  # ordem visual: GOL, ZAG, LAT, MEI, ATA, TEC
        if pos_id not in escalacao:
            continue
        for at in escalacao[pos_id]:
            clube_nome = clubes.get(str(at.get("clube_id")), {}).get("abreviacao", "?")
            pos_nome = POSICOES[pos_id]
            print(f"  {pos_nome:<10} {at.get('apelido', '')[:18]:<19} "
                  f"{clube_nome:<5}  C$ {at.get('preco_num', 0):>6.2f}  "
                  f"média {at.get('media_num', 0):>5.2f}")
            media_total += at.get("media_num", 0)

    print("  " + "─" * 60)
    print(f"  💰 Custo total:     C$ {custo:>7.2f} / C$ {orcamento:.2f}")
    print(f"  📈 Média esperada:  {media_total:>10.2f} pts")

    if custo > orcamento:
        print(f"\n  ⚠️  Não foi possível ficar dentro do orçamento (faltou C$ "
              f"{custo - orcamento:.2f}).")
        print("     Tente um esquema diferente ou aumentar o orçamento.")


# ============================================================
# FUNCIONALIDADE 4: PARCIAIS DA RODADA (AO VIVO)
# ============================================================

def ver_parciais():
    """Mostra os atletas que mais pontuaram na rodada em andamento."""
    print("\n🔴 PARCIAIS AO VIVO")
    print("=" * 50)

    # Primeiro, confirma se o mercado está fechado (rodada em andamento)
    status = fazer_requisicao("/mercado/status")
    if status and status.get("status_mercado") != 2:
        print("  ℹ️  Mercado não está fechado. Parciais só ficam disponíveis")
        print("     quando uma rodada está em andamento.")
        return

    dados = fazer_requisicao("/atletas/pontuados")
    if not dados:
        return

    atletas = dados.get("atletas", {})
    clubes = dados.get("clubes", {})

    if not atletas:
        print("  Nenhum atleta pontuou ainda.")
        return

    # Converte dict em lista e ordena por pontuação
    lista = []
    for atleta_id, info in atletas.items():
        info["atleta_id"] = atleta_id
        lista.append(info)
    lista.sort(key=lambda x: x.get("pontuacao", 0), reverse=True)

    print(f"  Rodada: {dados.get('rodada')}")
    print(f"\n  {'Apelido':<22}{'Pos':<10}{'Clube':<10}{'Pontos':>8}")
    print("  " + "-" * 50)
    for at in lista[:20]:  # top 20
        clube_id = str(at.get("clube_id"))
        clube_nome = clubes.get(clube_id, {}).get("abreviacao", "?")
        pos_nome = POSICOES.get(at.get("posicao_id"), "?")
        print(f"  {at.get('apelido', '')[:21]:<22}"
              f"{pos_nome:<10}"
              f"{clube_nome:<10}"
              f"{at.get('pontuacao', 0):>7.2f}")


# ============================================================
# FUNCIONALIDADE 5: BUSCAR TIME PELO SLUG
# ============================================================

def buscar_time():
    """Busca um time específico do Cartola pelo slug do nome."""
    print("\n🔍 BUSCAR TIME DE UM CARTOLEIRO")
    print("=" * 50)
    print("  Dica: o slug é o nome do time em minúsculas com hífens.")
    print("  Ex: 'Hassel Domingues FC' → 'hassel-domingues-fc'")

    slug = input("\n  Digite o slug do time: ").strip().lower().replace(" ", "-")
    if not slug:
        print("  ❌ Slug vazio.")
        return

    dados = fazer_requisicao(f"/time/slug/{slug}")
    if not dados:
        print("  ❌ Time não encontrado.")
        return

    info = dados.get("time", {})
    print(f"\n  Nome:           {info.get('nome')}")
    print(f"  Cartoleiro:     {info.get('nome_cartola')}")
    print(f"  Patrimônio:     C$ {info.get('patrimonio', 0):.2f}")
    print(f"  Pontos rodada:  {dados.get('pontos', 0):.2f}")
    print(f"  Pontos camp.:   {dados.get('pontos_campeonato', 0):.2f}")

    atletas = dados.get("atletas", [])
    if atletas:
        print(f"\n  Escalação ({len(atletas)} atletas):")
        for at in atletas:
            pos_nome = POSICOES.get(at.get("posicao_id"), "?")
            print(f"    • {pos_nome:<10} {at.get('apelido', '')}")


# ============================================================
# MENU PRINCIPAL
# ============================================================

def menu():
    """Loop principal do app."""
    opcoes = {
        "1": ("Ver status do mercado", ver_status_mercado),
        "2": ("Top atletas (filtrar mercado)", listar_top_atletas),
        "3": ("Sugerir escalação (otimizador)", sugerir_escalacao),
        "4": ("Parciais ao vivo da rodada", ver_parciais),
        "5": ("Buscar time pelo slug", buscar_time),
        "0": ("Sair", None),
    }

    while True:
        limpar_tela()
        print("=" * 50)
        print("       🏆 CARTOLA FC - APP DE TERMINAL 🏆")
        print("=" * 50)
        for k, (nome, _) in opcoes.items():
            print(f"  [{k}] {nome}")
        print("=" * 50)

        escolha = input("\n  Escolha uma opção: ").strip()

        if escolha == "0":
            print("\n  👋 Até a próxima rodada, Eric!")
            break
        if escolha not in opcoes:
            print("  ❌ Opção inválida.")
            time.sleep(1)
            continue

        try:
            opcoes[escolha][1]()
        except KeyboardInterrupt:
            print("\n  Operação cancelada.")
        except Exception as e:
            print(f"\n  ❌ Erro inesperado: {e}")

        pausar()


# ============================================================
# PONTO DE ENTRADA
# ============================================================

if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print("\n\n  👋 Encerrado pelo usuário.")
