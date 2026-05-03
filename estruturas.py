"""
estruturas.py
Jogo educativo de Estruturas de Dados — versão com penalidades de tempo.

INTERFACE PÚBLICA:
fase.move(direcao) -> navegação lateral (-1/+1)
fase.entrar() -> ação especial (marcar origem, selecionar)
fase.sair() -> cancelar/voltar
fase.apply_selected() -> executa ação; retorna "win" | penalidade_segundos | None
fase.hint() -> string de desafio
fase.state_text() -> string de estado
fase.selected_action() -> string da ação selecionada
fase.reset() -> reinicia a fase
fase.get_penalty() -> retorna última penalidade aplicada (em segundos)
"""

import random


# ═══════════════════════════════════════════════════════════════════════════
# CLASSE BASE
# ═══════════════════════════════════════════════════════════════════════════

class FaseBase:
    """Esqueleto comum."""

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
# FASE 1 — PILHA
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
            return f"ORIGEM: {self.NOMES_COL[self.origem]} → Escolha destino"
        return "Pressione W para marcar origem"

    def state_text(self):
        return f"Movimentos: {self.movimentos}"

    def selected_action(self):
        return self.NOMES_COL[self.idx_acao]


# ═══════════════════════════════════════════════════════════════════════════
# FASE 2 — FILA
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
            # sem mais letras, mas não completou
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
                # letra errada no placar
                self.esteira.insert(0, letra)  # devolve
                self.ultima_penalidade = 3
                return 3
        else:
            # reenfileirar
            self.esteira.append(letra)
            return None

    def hint(self):
        return f"Forme a sequência: {' '.join(self.gabarito)}"

    def state_text(self):
        return f"Placar: {len(self.placar)}/{len(self.gabarito)}"


# ═══════════════════════════════════════════════════════════════════════════
# FASE 3 — ARRAY
# ═══════════════════════════════════════════════════════════════════════════

class FaseArray(FaseBase):
    def reset(self):
        self.sequencia = [random.randint(1, 9) for _ in range(5)]
        self.usuario = []
        self.tempo_memorizar = 90  # 3 segundos a 30fps
        self.acoes = ["NOVA SEQ"] + [str(i) for i in range(1, 10)] + ["APAGAR"]
        self.idx_acao = 1  # começa no "1"
        self.ultima_penalidade = 0

    def nova_sequencia(self):
        """Gera nova sequência e cobra penalidade."""
        self.sequencia = [random.randint(1, 9) for _ in range(5)]
        self.usuario = []
        self.tempo_memorizar = 90
        self.ultima_penalidade = 8
        return 8

    def apagar(self):
        """Remove último dígito."""
        if self.usuario:
            self.usuario.pop()
        return None

    def apply_selected(self):
        if self.tempo_memorizar > 0:
            return None

        acao = self.selected_action()

        if acao == "NOVA SEQ":
            return self.nova_sequencia()

        if acao == "APAGAR":
            return self.apagar()

        # é um dígito
        valor = int(acao)
        self.usuario.append(valor)
        pos = len(self.usuario) - 1

        if self.usuario[pos] != self.sequencia[pos]:
            # erro — penalidade e não avança
            self.usuario.pop()
            self.ultima_penalidade = 3
            return 3

        if len(self.usuario) == len(self.sequencia):
            return "win"

        return None

    def hint(self):
        if self.tempo_memorizar > 0:
            self.tempo_memorizar -= 1
            return f"MEMORIZE! ({self.tempo_memorizar // 30 + 1}s)"
        return f"Digite a sequência — posição [{len(self.usuario)}/5]"

    def state_text(self):
        if self.tempo_memorizar > 0:
            return " ".join(str(v) for v in self.sequencia)
        return " ".join(str(v) if i < len(self.usuario) else "?" 
                        for i, v in enumerate(self.sequencia))


# ═══════════════════════════════════════════════════════════════════════════
# FASE 4 — GRAFOS (múltiplos grafos complexos)
# ═══════════════════════════════════════════════════════════════════════════

class FaseGrafos(FaseBase):
    GRAFOS = [
        # Grafo 1: Simples (4 nós)
        ("A", "D", {
            "A": [("B", 2), ("C", 5)],
            "B": [("A", 2), ("D", 4), ("C", 3)],
            "C": [("A", 5), ("B", 3), ("D", 1)],
            "D": [("B", 4), ("C", 1)],
        }),
        # Grafo 2: Médio (5 nós)
        ("A", "E", {
            "A": [("B", 3), ("C", 6)],
            "B": [("A", 3), ("D", 2), ("E", 8)],
            "C": [("A", 6), ("D", 4)],
            "D": [("B", 2), ("C", 4), ("E", 3)],
            "E": [("B", 8), ("D", 3)],
        }),
        # Grafo 3: Complexo (6 nós)
        ("A", "F", {
            "A": [("B", 4), ("C", 2)],
            "B": [("A", 4), ("D", 5)],
            "C": [("A", 2), ("D", 8), ("E", 3)],
            "D": [("B", 5), ("C", 8), ("F", 6)],
            "E": [("C", 3), ("F", 2)],
            "F": [("D", 6), ("E", 2)],
        }),
    ]

    def reset(self):
        self.inicio, self.alvo, self.grafo = random.choice(self.GRAFOS)
        self.no_atual = self.inicio
        self.caminho = [self.inicio]
        self.custo = 0
        self.ultima_penalidade = 0
        self._atualizar_acoes()

    def _atualizar_acoes(self):
        vizinhos = self.grafo[self.no_atual]
        self.acoes = [f"{v} (+{w})" for v, w in vizinhos]
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
            return "win"

        self._atualizar_acoes()
        return None

    def hint(self):
        return f"Vá de {self.inicio} até {self.alvo} — Custo atual: {self.custo}"

    def state_text(self):
        return f"Caminho: {' → '.join(self.caminho)}"


# ═══════════════════════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════════════════════

def criar_fases():
    return {
        1: FasePilha(),
        2: FaseFila(),
        3: FaseArray(),
        4: FaseGrafos(),
    }