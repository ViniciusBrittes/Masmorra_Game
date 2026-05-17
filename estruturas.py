"""
estruturas.py
Jogo educativo de Estruturas de Dados — versao com penalidades de tempo.

INTERFACE PUBLICA:
fase.move(direcao)        -> navegacao lateral (-1/+1)
fase.entrar()             -> acao especial (marcar origem, selecionar)
fase.sair()               -> cancelar/voltar
fase.apply_selected()     -> executa acao; retorna "win" | penalidade_segundos | None
fase.hint()               -> string de desafio
fase.state_text()         -> string de estado
fase.selected_action()    -> string da acao selecionada
fase.reset()              -> reinicia a fase
fase.get_penalty()        -> retorna ultima penalidade aplicada (em segundos)

NOVO (Fase Grafos):
fase.posicoes             -> dict {nome_no: (x_norm, y_norm)} com coords em [0..1]
                             para layout planar (sem cruzamento de arestas).
"""

import random
import heapq


# ═══════════════════════════════════════════════════════════════════════════
#  CLASSE BASE
# ═══════════════════════════════════════════════════════════════════════════
class FaseBase:
    def __init__(self):
        self.acoes = []
        self.idx_acao = 0
        self.ultima_penalidade = 0
        self.reset()

    def move(self, direcao):
        if not self.acoes:
            return
        self.idx_acao = (self.idx_acao + direcao) % len(self.acoes)

    def entrar(self):
        pass

    def sair(self):
        pass

    def apply_selected(self):
        raise NotImplementedError

    def hint(self):
        raise NotImplementedError

    def state_text(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def selected_action(self):
        if not self.acoes:
            return ""
        return self.acoes[self.idx_acao]

    def get_penalty(self):
        return self.ultima_penalidade


# ═══════════════════════════════════════════════════════════════════════════
#  FASE 1 — PILHA
# ═══════════════════════════════════════════════════════════════════════════
class FasePilha(FaseBase):
    COL_INICIAL = 0
    COL_AUXILIAR = 1
    COL_FINAL = 2
    NOMES_COL = ["INICIAL", "AUXILIAR", "FINAL"]

    def reset(self):
        valores = random.sample(range(1, 10), 4)
        self.meta = list(valores)
        self.inicial = list(valores)
        random.shuffle(self.inicial)
        while self.inicial == self.meta:
            random.shuffle(self.inicial)

        self.auxiliar = []
        self.final = []
        self.movimentos = 0
        self.idx_acao = self.COL_INICIAL
        self.origem = None
        self.acoes = list(self.NOMES_COL)
        self.ultima_penalidade = 0

    def entrar(self):
        if self.origem is None:
            pilha = self._pilha_de(self.idx_acao)
            if pilha:
                self.origem = self.idx_acao

    def sair(self):
        self.origem = None

    def apply_selected(self):
        if self.origem is None:
            self.entrar()
            return None

        destino = self.idx_acao
        if destino == self.origem:
            self.origem = None
            return None

        pilha_origem = self._pilha_de(self.origem)
        pilha_destino = self._pilha_de(destino)

        if not pilha_origem:
            self.origem = None
            return None

        pilha_destino.append(pilha_origem.pop())
        self.movimentos += 1
        self.origem = None

        if self.final == self.meta and not self.inicial and not self.auxiliar:
            return "win"
        return None

    def _pilha_de(self, idx):
        return [self.inicial, self.auxiliar, self.final][idx]

    def hint(self):
        if self.origem is not None:
            return f"ORIGEM: {self.NOMES_COL[self.origem]} -> Escolha destino"
        return "Pressione W para marcar origem"

    def state_text(self):
        return f"Movimentos: {self.movimentos}"

    def selected_action(self):
        return self.NOMES_COL[self.idx_acao]


# ═══════════════════════════════════════════════════════════════════════════
#  FASE 2 — FILA
# ═══════════════════════════════════════════════════════════════════════════
class FaseFila(FaseBase):
    def reset(self):
        self.gabarito = random.sample("ABCDEF", 4)
        extras = random.sample("GHIJKLMN", 3)
        self.esteira = list(self.gabarito) + extras
        random.shuffle(self.esteira)
        self.placar = []
        self.acoes = ["ENVIAR AO PLACAR", "REENFILEIRAR"]
        self.idx_acao = 0
        self.ultima_penalidade = 0

    def apply_selected(self):
        if not self.esteira:
            self.ultima_penalidade = 5
            return 5

        acao = self.selected_action()
        letra = self.esteira.pop(0)

        if acao == "ENVIAR AO PLACAR":
            idx = len(self.placar)
            if idx < len(self.gabarito) and letra == self.gabarito[idx]:
                self.placar.append(letra)
                if self.placar == self.gabarito:
                    return "win"
                return None
            else:
                self.esteira.insert(0, letra)
                self.ultima_penalidade = 3
                return 3
        else:
            self.esteira.append(letra)
            return None

    def hint(self):
        return f"Forme a sequencia: {' '.join(self.gabarito)}"

    def state_text(self):
        return f"Placar: {len(self.placar)}/{len(self.gabarito)}"


# ═══════════════════════════════════════════════════════════════════════════
#  FASE 3 — ARRAY
# ═══════════════════════════════════════════════════════════════════════════
class FaseArray(FaseBase):
    def reset(self):
        self.sequencia = [random.randint(1, 9) for _ in range(5)]
        self.usuario = []
        self.tempo_memorizar = 90
        self.acoes = ["NOVA SEQ"] + [str(i) for i in range(1, 10)]
        self.row = 3
        self.col = 0
        self.ultima_penalidade = 0

    def nova_sequencia(self):
        self.sequencia = [random.randint(1, 9) for _ in range(5)]
        self.usuario = []
        self.tempo_memorizar = 90
        self.ultima_penalidade = 8
        return 8

    def move(self, direcao):
        pass

    def move_2d(self, dx, dy):
        new_row = self.row + dy
        new_col = self.col + dx

        if new_row < 0:
            new_row = 3
        elif new_row > 3:
            new_row = 0

        if new_col < 0:
            new_col = 2
        elif new_col > 2:
            new_col = 0

        if new_row == 3 and new_col != 0:
            return

        if self.row == 3 and new_row != 3:
            new_col = 0

        self.row = new_row
        self.col = new_col
        self._atualizar_idx_acao()

    def _atualizar_idx_acao(self):
        if self.row == 3:
            self.idx_acao = 0
        else:
            digito = 7 - self.row * 3 + self.col
            self.idx_acao = digito

    def apply_selected(self):
        if self.tempo_memorizar > 0:
            return None

        acao = self.selected_action()

        if acao == "NOVA SEQ":
            return self.nova_sequencia()

        valor = int(acao)
        self.usuario.append(valor)
        pos = len(self.usuario) - 1

        if self.usuario[pos] != self.sequencia[pos]:
            self.usuario.pop()
            self.ultima_penalidade = 5
            return 5

        if len(self.usuario) == len(self.sequencia):
            return "win"

        return None

    def hint(self):
        if self.tempo_memorizar > 0:
            self.tempo_memorizar -= 1
            return f"MEMORIZE! ({self.tempo_memorizar // 30 + 1}s)"
        return f"Digite a sequencia - posicao [{len(self.usuario)}/5]"

    def state_text(self):
        if self.tempo_memorizar > 0:
            return " ".join(str(v) for v in self.sequencia)
        return " ".join(
            str(v) if i < len(self.usuario) else "?"
            for i, v in enumerate(self.sequencia)
        )


# ═══════════════════════════════════════════════════════════════════════════
#  FASE 4 — MAPA DO TESOURO (GRAFOS) com LAYOUT PLANAR
#
#  Cada grafo agora carrega um dicionario POSICOES com coordenadas
#  normalizadas (x, y) em [0.0 .. 1.0]. O motor de renderizacao mapeia
#  isso para a area do mapa na tela. Layouts foram desenhados a mao
#  para serem PLANARES (nenhuma aresta cruza outra).
# ═══════════════════════════════════════════════════════════════════════════
class FaseGrafos(FaseBase):

    # Cada entrada: (inicio, alvo, grafo, posicoes)
    GRAFOS = [
        # ─── G0 : LOSANGO (4 nos) ──────────────────────────────────────────
        #         Inicio
        #        /      \
        #     Ponte---Caverna
        #        \      /
        #        Tesouro
        # Arestas Ponte-Caverna eh a horizontal interna; nao cruza nada.
        (
            "Inicio",
            "Tesouro",
            {
                "Inicio": [("Ponte", 2), ("Caverna", 5)],
                "Ponte": [("Inicio", 2), ("Tesouro", 4), ("Caverna", 3)],
                "Caverna": [("Inicio", 5), ("Ponte", 3), ("Tesouro", 1)],
                "Tesouro": [("Ponte", 4), ("Caverna", 1)],
            },
            {
                "Inicio": (0.50, 0.10),
                "Ponte": (0.18, 0.50),
                "Caverna": (0.82, 0.50),
                "Tesouro": (0.50, 0.90),
            },
        ),
        # ─── G1 : DIAMANTE COM CAUDA (5 nos) ───────────────────────────────
        #              Vila
        #             /    \
        #         Inicio   Ruinas --- Tesouro
        #             \    /
        #            Floresta
        # Ruinas-Tesouro fica em coluna mais a direita; Vila e Floresta nao
        # tocam Tesouro diretamente -- evita cruzar arestas.
        (
            "Inicio",
            "Tesouro",
            {
                "Inicio": [("Vila", 3), ("Floresta", 6)],
                "Vila": [("Inicio", 3), ("Ruinas", 2), ("Tesouro", 8)],
                "Floresta": [("Inicio", 6), ("Ruinas", 4)],
                "Ruinas": [("Vila", 2), ("Floresta", 4), ("Tesouro", 3)],
                "Tesouro": [("Vila", 8), ("Ruinas", 3)],
            },
            # Vila-Tesouro contorna por cima; Ruinas-Tesouro reto.
            # Para evitar cruzamento Vila-Tesouro x Floresta-Ruinas,
            # colocamos Vila bem alto e Tesouro deslocado p/ baixo-direita.
            {
                "Inicio": (0.10, 0.50),
                "Vila": (0.40, 0.15),
                "Floresta": (0.40, 0.85),
                "Ruinas": (0.70, 0.50),
                "Tesouro": (0.95, 0.55),
            },
        ),
        # ─── G2 : DESERTO (6 nos) ──────────────────────────────────────────
        #        Oasis ------- Templo
        #       /              /      \
        #   Inicio          (cruza?)  Tesouro
        #       \              \      /
        #        Duna --------- Tumba
        # Reorganizado para fluxo horizontal: Inicio -> {Oasis, Duna} ->
        # Templo (top) / Tumba (bot) -> Tesouro. Arestas Oasis-Templo (top),
        # Duna-Tumba (bot), Duna-Templo (diagonal interna), Templo-Tumba
        # (vertical curta no meio).
        (
            "Inicio",
            "Tesouro",
            {
                "Inicio": [("Oasis", 4), ("Duna", 2)],
                "Oasis": [("Inicio", 4), ("Templo", 5)],
                "Duna": [("Inicio", 2), ("Templo", 8), ("Tumba", 3)],
                "Templo": [("Oasis", 5), ("Duna", 8), ("Tesouro", 6)],
                "Tumba": [("Duna", 3), ("Tesouro", 2)],
                "Tesouro": [("Templo", 6), ("Tumba", 2)],
            },
            # Duna-Templo (diagonal subindo) cruzaria Oasis-? — para evitar,
            # Oasis e Templo ficam alinhados horizontalmente em cima e
            # Duna/Tumba alinhados em baixo. A aresta Duna-Templo eh vertical
            # quase pura (mesma coluna X) e nao cruza Oasis-Templo.
            {
                "Inicio": (0.05, 0.50),
                "Oasis": (0.35, 0.20),
                "Templo": (0.65, 0.20),
                "Duna": (0.35, 0.80),
                "Tumba": (0.65, 0.80),
                "Tesouro": (0.95, 0.50),
            },
        ),
        # ─── G3 : MONTANHA (6 nos) ─────────────────────────────────────────
        #              Pico
        #             /    \
        #         Inicio   Lago --- Tesouro
        #             \    / \
        #              Vale   Gruta
        # Lago eh hub central, Tesouro fica a direita do Lago.
        (
            "Inicio",
            "Tesouro",
            {
                "Inicio": [("Pico", 7), ("Vale", 3)],
                "Pico": [("Inicio", 7), ("Lago", 4), ("Tesouro", 6)],
                "Vale": [("Inicio", 3), ("Lago", 5), ("Gruta", 8)],
                "Lago": [("Pico", 4), ("Vale", 5), ("Tesouro", 2), ("Gruta", 3)],
                "Tesouro": [("Pico", 6), ("Lago", 2)],
                "Gruta": [("Vale", 8), ("Lago", 3)],
            },
            # Pico-Tesouro arco superior, Vale-Gruta arco inferior; Lago no
            # meio. Inicio na esquerda. Sem cruzamentos.
            {
                "Inicio": (0.08, 0.50),
                "Pico": (0.40, 0.15),
                "Vale": (0.40, 0.85),
                "Lago": (0.65, 0.50),
                "Gruta": (0.65, 0.85),
                "Tesouro": (0.92, 0.50),
            },
        ),
        # ─── G4 : MARITIMO (7 nos) ─────────────────────────────────────────
        # Fluxo em 3 colunas: Inicio (esq) -> {Praia/Farol/Porto} ->
        # {Recife/Navio} -> Tesouro (dir).
        # Praia conecta Recife E Navio -- desenhado como duas arestas que
        # saem da Praia em angulos diferentes para evitar sobreposicao.
        (
            "Inicio",
            "Tesouro",
            {
                "Inicio": [("Praia", 4), ("Farol", 6), ("Porto", 5)],
                "Praia": [("Inicio", 4), ("Recife", 7), ("Navio", 8)],
                "Farol": [("Inicio", 6), ("Recife", 3)],
                "Porto": [("Inicio", 5), ("Navio", 4)],
                "Recife": [("Praia", 7), ("Farol", 3), ("Tesouro", 6)],
                "Navio": [("Praia", 8), ("Porto", 4), ("Tesouro", 3)],
                "Tesouro": [("Recife", 6), ("Navio", 3)],
            },
            # Inicio (col 0) -> Farol/Praia/Porto (col 1, distribuidos
            # verticalmente: topo/meio/baixo) -> Recife/Navio (col 2,
            # topo/baixo) -> Tesouro (col 3). A Praia (meio col1) liga em
            # Recife (topo col2) e Navio (baixo col2) por diagonais que
            # nao cruzam outras arestas (sao a unica conexao do "meio").
            {
                "Inicio": (0.05, 0.50),
                "Farol": (0.35, 0.15),
                "Praia": (0.35, 0.50),
                "Porto": (0.35, 0.85),
                "Recife": (0.70, 0.25),
                "Navio": (0.70, 0.75),
                "Tesouro": (0.95, 0.50),
            },
        ),
        # ─── G5 : SUBTERRANEO (8 nos, o mais complexo) ─────────────────────
        # Fluxo em 4 colunas: Inicio -> {Tunel/Mina} -> {Camara/Poço/Abismo}
        # -> {Cripta} -> Tesouro.
        # Camara eh hub conectado a quase tudo -- vai no centro vertical.
        (
            "Inicio",
            "Tesouro",
            {
                "Inicio": [("Tunel", 3), ("Mina", 7)],
                "Tunel": [("Inicio", 3), ("Poço", 6), ("Camara", 2)],
                "Mina": [("Inicio", 7), ("Camara", 5), ("Abismo", 4)],
                "Poço": [("Tunel", 6), ("Cripta", 3)],
                "Camara": [("Tunel", 2), ("Mina", 5), ("Cripta", 8), ("Tesouro", 9)],
                "Abismo": [("Mina", 4), ("Tesouro", 2)],
                "Cripta": [("Poço", 3), ("Camara", 8), ("Tesouro", 4)],
                "Tesouro": [("Camara", 9), ("Abismo", 2), ("Cripta", 4)],
            },
            # Layout em 4 colunas:
            # Col 0: Inicio (meio)
            # Col 1: Tunel (topo), Mina (baixo)
            # Col 2: Poco (topo), Camara (meio), Abismo (baixo)
            # Col 3: Cripta (topo-meio)
            # Col 4: Tesouro (meio-direita)
            #
            # Camara-Tesouro (de col2 a col4, pulando col3) eh a unica aresta
            # longa, mas passa por dentro horizontalmente sem cruzar nada
            # porque Cripta esta acima do meio.
            {
                "Inicio": (0.04, 0.50),
                "Tunel": (0.24, 0.20),
                "Mina": (0.24, 0.80),
                "Poço": (0.46, 0.15),
                "Camara": (0.46, 0.50),
                "Abismo": (0.46, 0.85),
                "Cripta": (0.72, 0.25),
                "Tesouro": (0.95, 0.55),
            },
        ),
    ]

    def _menor_caminho(self):
        fila = [(0, self.inicio)]
        visitados = {}
        while fila:
            custo, no = heapq.heappop(fila)
            if no in visitados:
                continue
            visitados[no] = custo
            if no == self.alvo:
                return custo
            for vizinho, peso in self.grafo[no]:
                if vizinho not in visitados:
                    heapq.heappush(fila, (custo + peso, vizinho))
        return float("inf")

    def reset(self):
        # Desempacota inclusive as posicoes
        self.inicio, self.alvo, self.grafo, self.posicoes = random.choice(self.GRAFOS)
        self.no_atual = self.inicio
        self.caminho = [self.inicio]
        self.custo = 0
        self.ultima_penalidade = 0
        self._custo_minimo = self._menor_caminho()
        self._atualizar_acoes()

    def _atualizar_acoes(self):
        vizinhos = self.grafo[self.no_atual]
        self.acoes = [f"{v} ({w}d)" for v, w in vizinhos]
        self._vizinhos = vizinhos
        if not self.acoes:
            self.idx_acao = 0
        else:
            self.idx_acao = min(self.idx_acao, len(self.acoes) - 1)

    def apply_selected(self):
        if not self._vizinhos:
            return None

        prox, peso = self._vizinhos[self.idx_acao]
        self.no_atual = prox
        self.custo += peso
        self.caminho.append(prox)

        if self.no_atual == self.alvo:
            if self.custo == self._custo_minimo:
                return "win"
            else:
                self.ultima_penalidade = 5
                return 5

        self._atualizar_acoes()
        return None

    def hint(self):
        return f"Encontre a rota mais rapida ate o Tesouro! (Melhor: {self._custo_minimo} dias)"

    def state_text(self):
        return f"Jornada: {' -> '.join(self.caminho)} | Dias: {self.custo}"


def criar_fases():
    return {
        1: FasePilha(),
        2: FaseFila(),
        3: FaseArray(),
        4: FaseGrafos(),
    }
