"""
estruturas.py
Jogo educativo de Estruturas de Dados — versao com 5 botoes.

INTERFACE PUBLICA (todas as fases respondem a estes metodos):
fase.move(direcao) -> Esquerda(-1) / Direita(+1): navegacao lateral
fase.entrar() -> Cima: focar / subir nivel hierarquico
fase.sair() -> Baixo: voltar para navegacao global
fase.apply_selected() -> Confirmar: executa acao; retorna "win"|"lose"|None
fase.hint() -> string de desafio/instrucao
fase.state_text() -> string (pode ter \n) com estado atual
fase.selected_action() -> string da acao/selecao atualmente destacada
fase.reset() -> reinicia a fase

Nas fases em que Cima/Baixo nao fazem sentido, entrar() e sair() sao no-ops.
"""

import heapq
import random


# ═══════════════════════════════════════════════════════════════════════════
# CLASSE BASE
# ═══════════════════════════════════════════════════════════════════════════

class FaseBase:
    """Esqueleto comum. Fases sobrescrevem o que precisam."""

    def __init__(self):
        self.acoes = []
        self.idx_acao = 0
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
        self.max_movimentos = 25

        self.idx_acao = self.COL_INICIAL
        self.origem = None

        self.acoes = list(self.NOMES_COL)

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

        if self.movimentos >= self.max_movimentos:
            return "lose"

        return None

    def _pilha_de(self, idx):
        return [self.inicial, self.auxiliar, self.final][idx]

    def hint(self):
        status = f"Movs: {self.movimentos}/{self.max_movimentos}"

        if self.origem is not None:
            status += f" - ORIGEM: {self.NOMES_COL[self.origem]}"
        else:
            status += " - Use CIMA p/ marcar origem"

        return status

    def state_text(self):
        return "Use as colunas para organizar a pilha"

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

    def apply_selected(self):
        if not self.esteira:
            return "lose"

        acao = self.selected_action()
        letra = self.esteira.pop(0)

        if acao == "ENVIAR AO PLACAR":
            idx = len(self.placar)

            if idx < len(self.gabarito) and letra == self.gabarito[idx]:
                self.placar.append(letra)

                if self.placar == self.gabarito:
                    return "win"

                return None

            return "lose"

        self.esteira.append(letra)
        return None

    def hint(self):
        return f"Forme a sequencia: {' '.join(self.gabarito)}"

    def state_text(self):
        return f"ESTEIRA: {self.esteira}\nPLACAR: {self.placar}"


# ═══════════════════════════════════════════════════════════════════════════
# FASE 3 — ARRAY
# ═══════════════════════════════════════════════════════════════════════════

class FaseArray(FaseBase):
    def reset(self):
        self.sequencia = [random.randint(1, 9) for _ in range(5)]
        self.usuario = []

        self.tempo_memorizar = 90

        self.acoes = [str(i) for i in range(1, 10)]
        self.idx_acao = 0

    def apply_selected(self):
        if self.tempo_memorizar > 0:
            return None

        valor = int(self.selected_action())
        self.usuario.append(valor)

        pos = len(self.usuario) - 1

        if self.usuario[pos] != self.sequencia[pos]:
            return "lose"

        if len(self.usuario) == len(self.sequencia):
            return "win"

        return None

    def hint(self):
        if self.tempo_memorizar > 0:
            self.tempo_memorizar -= 1
            return "MEMORIZE!"
        return "Digite a sequência"

    def state_text(self):
        if self.tempo_memorizar > 0:
            return str(self.sequencia)
        return str(self.usuario)


# ═══════════════════════════════════════════════════════════════════════════
# FASE 4 — GRAFOS
# ═══════════════════════════════════════════════════════════════════════════

class FaseGrafos(FaseBase):
    GRAFOS = [
        ("A", "D", {
            "A": [("B", 2), ("C", 5)],
            "B": [("A", 2), ("D", 4)],
            "C": [("A", 5), ("D", 1)],
            "D": [("B", 4), ("C", 1)],
        }),
    ]

    def reset(self):
        self.inicio, self.alvo, self.grafo = random.choice(self.GRAFOS)

        self.no_atual = self.inicio
        self.caminho = [self.inicio]
        self.custo = 0

        self._atualizar_acoes()

    def _atualizar_acoes(self):
        vizinhos = self.grafo[self.no_atual]
        self.acoes = [f"{v} (+{w})" for v, w in vizinhos]
        self._vizinhos = vizinhos

    def apply_selected(self):
        prox, peso = self._vizinhos[self.idx_acao]

        self.no_atual = prox
        self.custo += peso
        self.caminho.append(prox)

        if self.no_atual == self.alvo:
            return "win"

        self._atualizar_acoes()
        return None

    def hint(self):
        return f"Vá de {self.inicio} até {self.alvo}"

    def state_text(self):
        return f"Caminho: {' -> '.join(self.caminho)} | Custo: {self.custo}"


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