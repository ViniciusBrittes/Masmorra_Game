"""
main.py — Jogo Educativo: Estruturas de Dados
Engine visual com tema "Masmorra / Terminal CRT".

Teclas:
  A / ←   : Mover seleção para esquerda
  D / →   : Mover seleção para direita
  W / ↑   : Entrar / marcar origem
  S / ↓   : Sair / cancelar seleção
  F / SPC : Confirmar ação
"""

import pygame
import sys
import math
import random
from estruturas import criar_fases

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO
# ═══════════════════════════════════════════════════════════════════════════
LARGURA = 480
ALTURA = 320
FPS = 30

COR_BG = (8, 10, 14)
COR_BG_GRID = (18, 22, 30)
COR_AMBAR = (255, 176, 58)
COR_AMBAR_DIM = (140, 90, 20)
COR_CIANO = (88, 220, 230)
COR_CIANO_DIM = (30, 90, 100)
COR_VERDE = (120, 255, 140)
COR_ROXO = (180, 120, 255)
COR_VERMELHO = (255, 95, 85)
COR_TEXTO = (230, 220, 200)
COR_TEXTO_DIM = (110, 100, 85)
COR_MOLDURA = (200, 140, 40)


# ═══════════════════════════════════════════════════════════════════════════
# ENGINE VISUAL
# ═══════════════════════════════════════════════════════════════════════════
class EngineVisual:
    def __init__(self):
        pygame.init()
        pygame.font.init()  # garantia explícita — alguns sistemas precisam disso
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("MASMORRA DAS ESTRUTURAS DE DADOS")
        self.clock = pygame.time.Clock()

        # Carrega fontes com fallback. SysFont pode falhar silenciosamente em
        # alguns Linux/Mac retornando fonte vazia (causa "tela preta"). Por
        # isso tentamos a fonte do sistema; se falhar, caímos na default.
        self.fonte_titulo = self._carregar_fonte(24, bold=True)
        self.fonte_sub = self._carregar_fonte(15, bold=True)
        self.fonte_texto = self._carregar_fonte(13)
        self.fonte_mono_g = self._carregar_fonte(16, bold=True)
        self.fonte_pequena = self._carregar_fonte(10)

        self.fases = criar_fases()
        self.fase_atual_num = 1
        self.estado = "MENU"
        self.menu_idx = 0
        self.menu_itens = ["INICIAR EXPEDICAO", "MODO DEV", "SAIR DA MASMORRA"]

        self.flash_timer = 0
        self.flash_cor = None
        self.shake_timer = 0

        self.tick = 0
        self.particulas = []
        self._gerar_particulas_bg()

        self.tempo_total_frames = 120 * FPS

    @staticmethod
    def _carregar_fonte(tamanho, bold=False):
        """Carrega fonte com cascata de fallbacks p/ máxima compatibilidade."""
        candidatos = ["couriernew", "consolas", "monospace", "dejavusansmono"]
        for nome in candidatos:
            try:
                f = pygame.font.SysFont(nome, tamanho, bold=bold)
                # Testa se a fonte realmente renderiza algo (size > 0)
                if f and f.size("A")[0] > 0:
                    return f
            except Exception:
                continue
        # Último recurso: fonte default do pygame (sempre funciona)
        return pygame.font.Font(None, tamanho)

    def _desenhar_menu_dev(self):
        ox, oy = self._offset_shake()
        self._desenhar_texto(
            "[ MODO DO DESENVOLVEDOR ]",
            self.fonte_titulo,
            COR_ROXO,
            LARGURA // 2 + ox,
            45 + oy,
            centro=True,
        )
        self._desenhar_texto(
            "Pressione 1: Fase de Pilha",
            self.fonte_sub,
            COR_TEXTO_DIM,
            LARGURA // 2 + ox,
            100 + oy,
            centro=True,
        )
        self._desenhar_texto(
            "Pressione 2: Fase de Fila",
            self.fonte_sub,
            COR_TEXTO_DIM,
            LARGURA // 2 + ox,
            130 + oy,
            centro=True,
        )
        self._desenhar_texto(
            "Pressione 3: Fase de Array",
            self.fonte_sub,
            COR_TEXTO_DIM,
            LARGURA // 2 + ox,
            160 + oy,
            centro=True,
        )
        self._desenhar_texto(
            "Pressione 4: Fase de Grafos",
            self.fonte_sub,
            COR_TEXTO_DIM,
            LARGURA // 2 + ox,
            190 + oy,
            centro=True,
        )
        self._desenhar_texto(
            "[ESC] Voltar",
            self.fonte_pequena,
            COR_AMBAR,
            LARGURA // 2 + ox,
            ALTURA - 25 + oy,
            centro=True,
        )

    def rodar(self):
        while True:
            try:
                self.tick += 1
                for evento in pygame.event.get():
                    if evento.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if evento.type == pygame.KEYDOWN:
                        self._processar_teclado(evento.key)

                self._desenhar_fundo()

                if self.estado == "MENU":
                    self._desenhar_menu()
                elif self.estado == "MENU_DEV":
                    self._desenhar_menu_dev()
                elif self.estado == "JOGANDO":
                    self._desenhar_fase()
                elif self.estado == "VITORIA":
                    self._desenhar_tela_final(
                        "VITORIA", COR_VERDE, "A MASMORRA FOI CONQUISTADA"
                    )
                elif self.estado == "DERROTA":
                    self._desenhar_tela_final(
                        "GAME OVER",
                        COR_VERMELHO,
                        "AS SOMBRAS DA MASMORRA TE CONSUMIRAM",
                    )

                if self.flash_timer > 0:
                    self._aplicar_flash()

                if self.estado == "JOGANDO":
                    self.tempo_total_frames -= 1
                    if self.tempo_total_frames <= 0:
                        self._disparar_shake(20)
                        self._disparar_flash(COR_VERMELHO, 15)
                        self.estado = "DERROTA"

                self._aplicar_scanlines()
                pygame.display.flip()
                self.clock.tick(FPS)
            except SystemExit:
                raise
            except Exception as e:
                # Captura QUALQUER erro de renderização e imprime no terminal
                # em vez de deixar a janela em "tela preta" silenciosa.
                import traceback

                print(f"\n{'='*60}")
                print(f"ERRO no estado '{self.estado}' (fase {self.fase_atual_num}):")
                print(f"  {type(e).__name__}: {e}")
                print(traceback.format_exc())
                print(f"{'='*60}\n")
                # Continua o loop para que dê tempo de ver o erro
                pygame.display.flip()
                self.clock.tick(FPS)

    def _desenhar_menu(self):
        ox, oy = self._offset_shake()

        self._desenhar_texto(
            "MASMORRA DAS",
            self.fonte_sub,
            COR_TEXTO_DIM,
            LARGURA // 2 + ox,
            60 + oy,
            centro=True,
        )
        self._desenhar_texto(
            "ESTRUTURAS DE DADOS",
            self.fonte_titulo,
            COR_AMBAR,
            LARGURA // 2 + ox,
            95 + oy,
            centro=True,
        )

        for i, item in enumerate(self.menu_itens):
            is_sel = i == self.menu_idx
            cor = COR_VERDE if is_sel else COR_TEXTO_DIM
            texto = f"> {item} <" if is_sel else item

            if is_sel:
                p = self._glow()
                cor = tuple(int(c * (0.7 + 0.3 * p)) for c in COR_VERDE)

            self._desenhar_texto(
                texto,
                self.fonte_sub,
                cor,
                LARGURA // 2 + ox,
                160 + i * 30 + oy,
                centro=True,
            )

        self._desenhar_texto(
            "W/S para navegar • SPACE/F para entrar",
            self.fonte_pequena,
            COR_TEXTO_DIM,
            LARGURA // 2 + ox,
            ALTURA - 25 + oy,
            centro=True,
        )

    def _processar_teclado(self, tecla):
        if self.estado == "MENU":
            if tecla in (pygame.K_w, pygame.K_UP):
                self.menu_idx = (self.menu_idx - 1) % len(self.menu_itens)
            elif tecla in (pygame.K_s, pygame.K_DOWN):
                self.menu_idx = (self.menu_idx + 1) % len(self.menu_itens)
            elif tecla in (pygame.K_f, pygame.K_SPACE, pygame.K_RETURN):
                if self.menu_idx == 0:
                    self.estado = "JOGANDO"
                    self.fases = criar_fases()
                    self.fase_atual_num = 1
                    self.tempo_total_frames = 120 * FPS
                elif self.menu_idx == 1:
                    self.estado = "MENU_DEV"
                else:
                    pygame.quit()
                    sys.exit()

        elif self.estado == "MENU_DEV":
            if tecla in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                self.estado = "JOGANDO"
                self.fases = criar_fases()
                self.fase_atual_num = int(pygame.key.name(tecla))
                self.tempo_total_frames = 120 * FPS
            elif tecla == pygame.K_ESCAPE:
                self.estado = "MENU"

        elif self.estado == "JOGANDO":
            if tecla == pygame.K_ESCAPE:
                self.estado = "MENU"
                self.fase_atual_num = 1
                self.fases = criar_fases()
                return

            fase = self.fases[self.fase_atual_num]

            if self.fase_atual_num == 3:
                if tecla in (pygame.K_a, pygame.K_LEFT):
                    fase.move_2d(-1, 0)
                elif tecla in (pygame.K_d, pygame.K_RIGHT):
                    fase.move_2d(1, 0)
                elif tecla in (pygame.K_w, pygame.K_UP):
                    fase.move_2d(0, -1)
                elif tecla in (pygame.K_s, pygame.K_DOWN):
                    fase.move_2d(0, 1)
            else:
                if tecla in (pygame.K_a, pygame.K_LEFT):
                    fase.move(-1)
                elif tecla in (pygame.K_d, pygame.K_RIGHT):
                    fase.move(1)
                elif tecla in (pygame.K_w, pygame.K_UP):
                    fase.entrar()
                elif tecla in (pygame.K_s, pygame.K_DOWN):
                    fase.sair()

            if tecla in (pygame.K_f, pygame.K_SPACE, pygame.K_RETURN):
                resultado = fase.apply_selected()
                if resultado == "win":
                    self._disparar_flash(COR_VERDE, 12)
                    self.fase_atual_num += 1
                    if self.fase_atual_num > 4:
                        self.estado = "VITORIA"
                    else:
                        self.fases[self.fase_atual_num].reset()
                elif isinstance(resultado, (int, float)):
                    frames_penalidade = int(resultado * FPS)
                    self.tempo_total_frames -= frames_penalidade
                    self._disparar_flash(COR_VERMELHO, 8)
                    self._disparar_shake(8)
                elif resultado == "lose":
                    self._disparar_shake(15)
                    self._disparar_flash(COR_VERMELHO, 12)
                    self.estado = "DERROTA"

        elif self.estado in ("VITORIA", "DERROTA"):
            if tecla in (pygame.K_f, pygame.K_SPACE, pygame.K_RETURN):
                self.estado = "MENU"
                self.fase_atual_num = 1
                self.fases = criar_fases()

    def _gerar_particulas_bg(self):
        self.particulas = [
            {
                "x": random.randint(0, LARGURA),
                "y": random.randint(0, ALTURA),
                "vy": random.uniform(0.2, 0.5),
                "size": random.choice([1, 1, 2]),
                "brilho": random.randint(60, 130),
            }
            for _ in range(25)
        ]

    def _desenhar_fundo(self):
        self.tela.fill(COR_BG)
        for x in range(0, LARGURA, 30):
            pygame.draw.line(self.tela, COR_BG_GRID, (x, 0), (x, ALTURA), 1)
        for y in range(0, ALTURA, 30):
            pygame.draw.line(self.tela, COR_BG_GRID, (0, y), (LARGURA, y), 1)
        for p in self.particulas:
            p["y"] -= p["vy"]
            if p["y"] < 0:
                p["y"] = ALTURA
                p["x"] = random.randint(0, LARGURA)
            c = (p["brilho"], p["brilho"] * 2 // 3, p["brilho"] // 3)
            pygame.draw.circle(self.tela, c, (int(p["x"]), int(p["y"])), p["size"])
        self._vinheta()

    def _vinheta(self):
        ov = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        for i in range(30):
            a = int(60 * (i / 30) ** 2)
            pygame.draw.rect(
                ov, (0, 0, 0, a), (i, i, LARGURA - 2 * i, ALTURA - 2 * i), 1
            )
        self.tela.blit(ov, (0, 0))

    def _aplicar_scanlines(self):
        ov = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        for y in range(0, ALTURA, 2):
            pygame.draw.line(ov, (0, 0, 0, 25), (0, y), (LARGURA, y), 1)
        self.tela.blit(ov, (0, 0))

    def _aplicar_flash(self):
        ov = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        a = int(140 * (self.flash_timer / 12))
        ov.fill((*self.flash_cor, a))
        self.tela.blit(ov, (0, 0))
        self.flash_timer -= 1

    def _disparar_flash(self, cor, frames):
        self.flash_cor = cor
        self.flash_timer = frames

    def _disparar_shake(self, frames):
        self.shake_timer = frames

    def _offset_shake(self):
        if self.shake_timer > 0:
            self.shake_timer -= 1
            return random.randint(-3, 3), random.randint(-3, 3)
        return 0, 0

    def _desenhar_moldura(self, rect, cor=COR_MOLDURA, titulo=None):
        x, y, w, h = rect
        pygame.draw.rect(self.tela, cor, rect, 1)
        pygame.draw.rect(self.tela, cor, (x + 2, y + 2, w - 4, h - 4), 1)
        if titulo:
            t = self.fonte_pequena.render(f" {titulo} ", True, COR_BG, cor)
            self.tela.blit(t, (x + 12, y - 6))

    def _desenhar_texto(self, texto, fonte, cor, x, y, centro=False, sombra=True):
        if sombra:
            s = fonte.render(texto, True, (0, 0, 0))
            r = s.get_rect()
            if centro:
                r.center = (x + 1, y + 1)
            else:
                r.topleft = (x + 1, y + 1)
            self.tela.blit(s, r)
        sup = fonte.render(texto, True, cor)
        r = sup.get_rect()
        if centro:
            r.center = (x, y)
        else:
            r.topleft = (x, y)
        self.tela.blit(sup, r)

    def _glow(self):
        return (math.sin(self.tick * 0.15) + 1) / 2

    def _desenhar_frame_fase(self, ox, oy):
        fase = self.fases[self.fase_atual_num]
        nomes = {
            1: "PILHA (LIFO)",
            2: "FILA (FIFO)",
            3: "ARRAY (INDICES)",
            4: "GRAFOS (MAPA TESOURO)",
        }

        # Cabeçalho compacto
        self._desenhar_moldura(
            (15 + ox, 10 + oy, LARGURA - 30, 42),
            COR_CIANO_DIM,
            titulo=f"FASE {self.fase_atual_num}/4",
        )
        self._desenhar_texto(
            nomes.get(self.fase_atual_num, "???"),
            self.fonte_sub,
            COR_CIANO,
            LARGURA // 2 + ox,
            31 + oy,
            centro=True,
        )
        for i in range(4):
            cx = 40 + i * 18 + ox
            cy = 31 + oy
            idx = i + 1
            cor = (
                COR_VERDE
                if idx < self.fase_atual_num
                else COR_AMBAR if idx == self.fase_atual_num else COR_TEXTO_DIM
            )
            pts = [(cx, cy - 4), (cx + 4, cy), (cx, cy + 4), (cx - 4, cy)]
            pygame.draw.polygon(
                self.tela, cor, pts, 0 if idx <= self.fase_atual_num else 1
            )

        # Desafio/Dica compacto
        self._desenhar_moldura(
            (15 + ox, 58 + oy, LARGURA - 30, 34), COR_AMBAR_DIM, titulo="DESAFIO"
        )
        self._desenhar_texto(
            f"> {fase.hint()}", self.fonte_texto, COR_AMBAR, 28 + ox, 74 + oy
        )

        # Rodapé de instruções
        if self.fase_atual_num == 1:
            teclas = "[A/D] COLUNA    [W] ORIGEM    [S] CANCELAR    [F] MOVER"
        elif self.fase_atual_num == 3:
            teclas = "[W/A/S/D] NAVEGAR NO GRID    [F] CONFIRMAR DIGITO"
        elif self.fase_atual_num == 4:
            teclas = "[A/D] SELECIONAR CAMINHO      [F] VIAJAR"
        else:
            teclas = "[A/D] NAVEGAR ACOES    [F] EXECUTAR"
        self._desenhar_texto(
            teclas,
            self.fonte_pequena,
            COR_TEXTO_DIM,
            LARGURA // 2 + ox,
            ALTURA - 15 + oy,
            centro=True,
        )

        segundos_restantes = max(0, self.tempo_total_frames // FPS)
        mins = segundos_restantes // 60
        segs = segundos_restantes % 60
        cor_timer = COR_VERDE if segundos_restantes > 40 else COR_VERMELHO

        self._desenhar_texto(
            f"TEMPO: {mins:02d}:{segs:02d}",
            self.fonte_sub,
            cor_timer,
            LARGURA - 85 + ox,
            31 + oy,
            centro=True,
        )

    def _desenhar_fase(self):
        ox, oy = self._offset_shake()
        self._desenhar_frame_fase(ox, oy)
        if self.fase_atual_num == 1:
            self._desenhar_pilha_visual(ox, oy)
        elif self.fase_atual_num == 2:
            self._desenhar_fila_visual(ox, oy)
        elif self.fase_atual_num == 3:
            self._desenhar_array_visual(ox, oy)
        elif self.fase_atual_num == 4:
            self._desenhar_grafo_visual(ox, oy)

    # ─────────────────────────────────────────────────────────────────────
    # FASE 1 — PILHA (Redimensionada)
    # ─────────────────────────────────────────────────────────────────────
    def _desenhar_pilha_visual(self, ox, oy):
        fase = self.fases[1]
        AY = 96 + oy
        AH = 198
        self._desenhar_moldura(
            (15 + ox, AY, LARGURA - 30, AH), COR_MOLDURA, titulo="ESTADO DA PILHA"
        )

        BW, BH, GAP = 44, 18, 3
        BASE_Y = AY + AH - 16
        MAX = 4

        # Meta
        meta_cx = 45 + ox
        self._desenhar_texto(
            "META",
            self.fonte_pequena,
            COR_ROXO,
            meta_cx,
            AY + 14,
            centro=True,
            sombra=False,
        )
        for i, val in enumerate(fase.meta):
            bx = meta_cx - 18
            by = BASE_Y - BH - i * (BH + GAP) - 2
            pygame.draw.rect(self.tela, (35, 25, 55), (bx, by, 36, BH))
            pygame.draw.rect(self.tela, COR_ROXO, (bx, by, 36, BH), 1)
            self._desenhar_texto(
                str(val),
                self.fonte_mono_g,
                COR_ROXO,
                meta_cx,
                by + BH // 2,
                centro=True,
                sombra=False,
            )
        pygame.draw.line(
            self.tela, COR_ROXO, (meta_cx - 22, BASE_Y), (meta_cx + 22, BASE_Y), 2
        )

        pygame.draw.line(
            self.tela,
            COR_TEXTO_DIM,
            (meta_cx + 28, AY + 10),
            (meta_cx + 28, BASE_Y + 8),
            1,
        )

        # Colunas
        COLUNAS = [
            (fase.inicial, "INICIAL", COR_AMBAR, 0),
            (fase.auxiliar, "AUXILIAR", COR_CIANO, 1),
            (fase.final, "FINAL", COR_VERDE, 2),
        ]
        col_xs = [140 + ox, 250 + ox, 360 + ox]

        for dados, rotulo, cor, col_idx in COLUNAS:
            cx = col_xs[col_idx]
            is_sel = fase.idx_acao == col_idx
            is_origem = fase.origem is not None and fase.origem == col_idx

            if is_origem:
                dest_cor = COR_VERDE
            elif is_sel:
                dest_cor = cor
            else:
                dest_cor = tuple(c // 4 for c in cor)

            lbl = f"[{rotulo}]" if is_sel else f" {rotulo} "
            self._desenhar_texto(
                lbl,
                self.fonte_pequena,
                dest_cor,
                cx,
                AY + 14,
                centro=True,
                sombra=False,
            )

            if is_origem:
                self._desenhar_texto(
                    "<ORIGEM>",
                    self.fonte_pequena,
                    COR_VERDE,
                    cx,
                    AY + 26,
                    centro=True,
                    sombra=False,
                )

            for slot in range(len(dados), MAX):
                bx = cx - BW // 2
                by = BASE_Y - BH - slot * (BH + GAP) - 2
                dim = tuple(max(c // 6, 10) for c in cor)
                pygame.draw.rect(self.tela, dim, (bx, by, BW, BH), 1)

            for i, val in enumerate(dados):
                is_topo = i == len(dados) - 1
                bx = cx - BW // 2
                by = BASE_Y - BH - i * (BH + GAP) - 2

                bg = tuple(max(int(c * 0.13), 8) for c in cor)
                pygame.draw.rect(self.tela, bg, (bx, by, BW, BH))

                b_cor = (
                    dest_cor if is_topo else tuple(max(int(c * 0.45), 10) for c in cor)
                )
                b_thick = 2 if is_topo else 1
                pygame.draw.rect(self.tela, b_cor, (bx, by, BW, BH), b_thick)

                if is_topo and is_sel:
                    for ex, ey in [
                        (bx, by),
                        (bx + BW, by),
                        (bx, by + BH),
                        (bx + BW, by + BH),
                    ]:
                        pygame.draw.circle(self.tela, b_cor, (ex, ey), 2)

                n_cor = (
                    dest_cor if is_topo else tuple(max(int(c * 0.5), 10) for c in cor)
                )
                self._desenhar_texto(
                    str(val),
                    self.fonte_mono_g,
                    n_cor,
                    cx,
                    by + BH // 2,
                    centro=True,
                    sombra=False,
                )

            if dados:
                ti = len(dados) - 1
                tb = BASE_Y - BH - ti * (BH + GAP) - 2
                self._desenhar_texto(
                    "topo v",
                    self.fonte_pequena,
                    dest_cor,
                    cx,
                    tb - 10,
                    centro=True,
                    sombra=False,
                )
            else:
                self._desenhar_texto(
                    "VAZIA",
                    self.fonte_pequena,
                    tuple(c // 5 for c in cor),
                    cx,
                    BASE_Y - 45,
                    centro=True,
                    sombra=False,
                )

            pygame.draw.line(
                self.tela,
                dest_cor,
                (cx - BW // 2 - 4, BASE_Y),
                (cx + BW // 2 + 4, BASE_Y),
                2,
            )

        if fase.origem is not None and fase.origem != fase.idx_acao:
            p = self._glow()
            ac = tuple(int(c * (0.55 + 0.45 * p)) for c in COR_TEXTO)
            ax1 = col_xs[fase.origem]
            ax2 = col_xs[fase.idx_acao]
            ay = BASE_Y - BH * 2 - 12
            pygame.draw.line(self.tela, ac, (ax1, ay), (ax2, ay), 1)
            dx = 1 if ax2 > ax1 else -1
            pygame.draw.polygon(
                self.tela, ac, [(ax2, ay - 4), (ax2 + dx * 8, ay), (ax2, ay + 4)]
            )

    # ─────────────────────────────────────────────────────────────────────
    # FASE 2 — FILA (Redimensionada)
    # ─────────────────────────────────────────────────────────────────────
    def _desenhar_fila_visual(self, ox, oy):
        fase = self.fases[2]
        AY = 96 + oy
        AH = 198
        self._desenhar_moldura(
            (15 + ox, AY, LARGURA - 30, AH), COR_MOLDURA, titulo="ESTADO DA FILA"
        )

        BW, BH = 26, 22

        # Esteira
        self._desenhar_texto(
            "ESTEIRA (frente -> fim):",
            self.fonte_pequena,
            COR_TEXTO_DIM,
            30 + ox,
            AY + 14,
        )
        for i, letra in enumerate(fase.esteira):
            bx = 30 + ox + i * (BW + 4)
            by = AY + 26
            is_f = i == 0
            cor = COR_AMBAR if is_f else COR_TEXTO_DIM
            t = 2 if is_f else 1
            pygame.draw.rect(self.tela, (22, 16, 6), (bx, by, BW, BH))
            pygame.draw.rect(self.tela, cor, (bx, by, BW, BH), t)
            self._desenhar_texto(
                letra,
                self.fonte_mono_g,
                cor,
                bx + BW // 2,
                by + BH // 2,
                centro=True,
                sombra=False,
            )
            if is_f:
                self._desenhar_texto(
                    "SAIDA",
                    self.fonte_pequena,
                    cor,
                    bx + BW // 2,
                    by - 10,
                    centro=True,
                    sombra=False,
                )

        # Placar
        self._desenhar_texto(
            "PLACAR:", self.fonte_pequena, COR_TEXTO_DIM, 30 + ox, AY + 64
        )
        for i in range(len(fase.gabarito)):
            bx = 30 + ox + i * (BW + 4)
            by = AY + 76
            ok = i < len(fase.placar)
            cor = COR_VERDE if ok else tuple(c // 5 for c in COR_VERDE)
            pygame.draw.rect(self.tela, (8, 20, 10) if ok else COR_BG, (bx, by, BW, BH))
            pygame.draw.rect(self.tela, cor, (bx, by, BW, BH), 2 if ok else 1)
            txt = fase.placar[i] if ok else "?"
            self._desenhar_texto(
                txt,
                self.fonte_mono_g,
                cor,
                bx + BW // 2,
                by + BH // 2,
                centro=True,
                sombra=False,
            )

        # Ação Selecionada compactada dentro da moldura principal
        ay2 = AY + 120
        self._desenhar_moldura(
            (30 + ox, ay2, LARGURA - 60, 56), COR_CIANO_DIM, titulo="ACAO SELECIONADA"
        )
        self._desenhar_texto(
            f"<< {fase.selected_action()} >>",
            self.fonte_sub,
            COR_AMBAR,
            LARGURA // 2 + ox,
            ay2 + 28,
            centro=True,
        )

    # ─────────────────────────────────────────────────────────────────────
    # FASE 3 — ARRAY (Redimensionada)
    # ─────────────────────────────────────────────────────────────────────
    def _desenhar_array_visual(self, ox, oy):
        fase = self.fases[3]
        AY = 96 + oy
        AH = 198
        self._desenhar_moldura(
            (15 + ox, AY, LARGURA - 30, AH), COR_MOLDURA, titulo="ESTADO DO ARRAY"
        )

        BW = 50
        BH = 26
        by = AY + 24
        n = len(fase.sequencia)
        sx = (LARGURA - n * BW - (n - 1) * 6) // 2 + ox

        for i in range(n):
            bx = sx + i * (BW + 6)
            show = fase.tempo_memorizar > 0 or i < len(fase.usuario)
            is_cur = fase.tempo_memorizar <= 0 and i == len(fase.usuario)
            preench = i < len(fase.usuario)

            if fase.tempo_memorizar > 0:
                val = fase.sequencia[i]
                cor = COR_AMBAR
            elif preench:
                val = fase.usuario[i]
                cor = COR_VERDE
            elif is_cur:
                val = "?"
                cor = COR_CIANO
            else:
                val = "?"
                cor = COR_TEXTO_DIM

            thick = 2 if is_cur else 1
            pygame.draw.rect(
                self.tela, tuple(max(int(c * 0.10), 8) for c in cor), (bx, by, BW, BH)
            )
            pygame.draw.rect(self.tela, cor, (bx, by, BW, BH), thick)
            self._desenhar_texto(
                str(val),
                self.fonte_mono_g,
                cor,
                bx + BW // 2,
                by + BH // 2,
                centro=True,
                sombra=False,
            )
            self._desenhar_texto(
                f"[{i}]",
                self.fonte_pequena,
                tuple(c // 2 for c in cor),
                bx + BW // 2,
                by + BH + 6,
                centro=True,
                sombra=False,
            )

        # Teclado Virtual Numérico 2D Compacto
        ay2 = AY + 70
        self._desenhar_moldura(
            (30 + ox, ay2, LARGURA - 60, 114), COR_CIANO_DIM, titulo="ENTRADA"
        )

        grid = [
            ["7", "8", "9"],
            ["4", "5", "6"],
            ["1", "2", "3"],
        ]

        spacing_x = 60
        spacing_y = 22
        start_x = LARGURA // 2 - spacing_x + ox
        start_y = ay2 + 20

        for row_idx, row in enumerate(grid):
            for col_idx, acao in enumerate(row):
                x = start_x + col_idx * spacing_x
                y = start_y + row_idx * spacing_y

                is_sel = fase.row == row_idx and fase.col == col_idx
                cor = COR_AMBAR if is_sel else COR_TEXTO_DIM
                esp = 2 if is_sel else 1

                pygame.draw.rect(self.tela, (20, 20, 20), (x - 20, y - 9, 40, 18))
                pygame.draw.rect(self.tela, cor, (x - 20, y - 9, 40, 18), esp)
                self._desenhar_texto(acao, self.fonte_texto, cor, x, y, centro=True)

        # Botão Reset Integrado na Linha 3
        reset_x = start_x
        reset_y = start_y + 3 * spacing_y
        is_sel_reset = fase.row == 3

        cor_reset = COR_ROXO if is_sel_reset else COR_TEXTO_DIM
        esp_reset = 2 if is_sel_reset else 1

        pygame.draw.rect(self.tela, (20, 20, 20), (reset_x - 30, reset_y - 9, 60, 18))
        pygame.draw.rect(
            self.tela, cor_reset, (reset_x - 30, reset_y - 9, 60, 18), esp_reset
        )
        self._desenhar_texto(
            "NOVA SEQ", self.fonte_pequena, cor_reset, reset_x, reset_y, centro=True
        )

    # ─────────────────────────────────────────────────────────────────────
    # FASE 4 — MAPA DO TESOURO (Redimensionada)
    # ─────────────────────────────────────────────────────────────────────
    def _desenhar_linha_pontilhada(
        self, x1, y1, x2, y2, cor, espessura=1, dash_length=4
    ):
        dx = x2 - x1
        dy = y2 - y1
        dist = math.sqrt(dx**2 + dy**2)
        if dist == 0:
            return

        dashes = int(dist / dash_length)
        for i in range(dashes):
            if i % 2 == 0:
                start = i / dashes
                end = min((i + 1) / dashes, 1)
                pygame.draw.line(
                    self.tela,
                    cor,
                    (int(x1 + dx * start), int(y1 + dy * start)),
                    (int(x1 + dx * end), int(y1 + dy * end)),
                    espessura,
                )

    # Limites da área do mapa do grafo, em pixels (margem interna p/ os nós).
    GRAFO_MAP_X = 40
    GRAFO_MAP_Y = 130
    GRAFO_MAP_W = LARGURA - 80
    GRAFO_MAP_H = 130

    def _calcular_posicoes_grafo(self, fase):
        """
        Mapeia coordenadas normalizadas (0..1) que vêm de fase.posicoes
        para pixels dentro da área do mapa. Se a fase NÃO tiver .posicoes
        (estruturas.py antigo), cai num layout circular/grid genérico como
        fallback — assim o jogo nunca quebra.
        """
        # ── FALLBACK: estruturas.py antigo sem o atributo .posicoes ──
        if not hasattr(fase, "posicoes") or not fase.posicoes:
            nos = list(fase.grafo.keys())
            num_nos = len(nos)
            posicoes = {}
            cx = self.GRAFO_MAP_X + self.GRAFO_MAP_W // 2
            cy = self.GRAFO_MAP_Y + self.GRAFO_MAP_H // 2
            raio = min(self.GRAFO_MAP_W, self.GRAFO_MAP_H) // 2.4
            for i, no in enumerate(nos):
                ang = (2 * math.pi * i / max(num_nos, 1)) - math.pi / 2
                posicoes[no] = (
                    int(cx + raio * math.cos(ang)),
                    int(cy + raio * math.sin(ang)),
                )
            return posicoes

        # ── CAMINHO NORMAL: lê posições planares de estruturas.py ──
        posicoes = {}
        for nome, (nx, ny) in fase.posicoes.items():
            px = self.GRAFO_MAP_X + int(nx * self.GRAFO_MAP_W)
            py = self.GRAFO_MAP_Y + int(ny * self.GRAFO_MAP_H)
            posicoes[nome] = (px, py)
        return posicoes

    def _cor_por_peso(self, peso):
        """
        Color-coding das arestas/plaquinhas conforme o custo em dias:
          1-3  -> CIANO (rota rapida)
          4-5  -> AMBAR (rota media)
          6+   -> VERMELHO (rota lenta)
        """
        if peso <= 3:
            return COR_CIANO
        elif peso <= 5:
            return COR_AMBAR
        else:
            return COR_VERMELHO

    def _desenhar_plaquinha_peso(self, mx, my, peso, cor, destaque=False):
        """
        Desenha um retângulo opaco (cor de fundo) com o número do peso
        centralizado por cima. A plaqueta "corta" visualmente a aresta,
        garantindo contraste 100%. Borda colorida casa com a cor da aresta.
        """
        txt = f"{peso}"
        sup = self.fonte_pequena.render(txt, True, cor)
        w, h = sup.get_size()
        pad_x, pad_y = 4, 1
        rx = mx - w // 2 - pad_x
        ry = my - h // 2 - pad_y
        rw = w + pad_x * 2
        rh = h + pad_y * 2

        # Fundo opaco — recorta a linha da aresta atrás da plaqueta
        pygame.draw.rect(self.tela, COR_BG, (rx, ry, rw, rh))
        # Borda colorida (mais espessa quando selecionada)
        esp = 2 if destaque else 1
        pygame.draw.rect(self.tela, cor, (rx, ry, rw, rh), esp)
        # Número centralizado
        self.tela.blit(sup, (mx - w // 2, my - h // 2))

    def _desenhar_grafo_visual(self, ox, oy):
        fase = self.fases[4]
        AY = 96 + oy
        AH = 198

        self._desenhar_moldura(
            (15 + ox, AY, LARGURA - 30, AH), COR_MOLDURA, titulo="MAPA DO TESOURO"
        )

        # Posições planares vindas de fase.posicoes
        nos_pos = self._calcular_posicoes_grafo(fase)

        # Identifica aresta atualmente selecionada (no_atual -> vizinho focado)
        aresta_selecionada = None
        prox_no_selecionado = None
        if fase._vizinhos and fase.idx_acao < len(fase._vizinhos):
            prox_no_selecionado, _ = fase._vizinhos[fase.idx_acao]
            aresta_selecionada = (fase.no_atual, prox_no_selecionado)

        pulso = self._glow()

        # ─── PASSE 1: ARESTAS (linhas) ────────────────────────────────────
        # Desenha cada aresta UMA VEZ usando ordem alfabética para evitar
        # duplicata (grafo é não-direcionado).
        arestas_desenhadas = []  # guarda (mx, my, peso, cor, destaque) p/ passe 2
        for no, vizinhos in fase.grafo.items():
            if no not in nos_pos:
                continue
            x1, y1 = nos_pos[no]
            for v, peso in vizinhos:
                if v not in nos_pos or no >= v:
                    continue
                x2, y2 = nos_pos[v]

                # Esta aresta faz parte do caminho percorrido?
                em_caminho = False
                for i in range(len(fase.caminho) - 1):
                    if (fase.caminho[i] == no and fase.caminho[i + 1] == v) or (
                        fase.caminho[i] == v and fase.caminho[i + 1] == no
                    ):
                        em_caminho = True
                        break

                is_selecionada = aresta_selecionada == (
                    no,
                    v,
                ) or aresta_selecionada == (v, no)

                # Cor base pelo peso (color-coding)
                cor_peso = self._cor_por_peso(peso)

                # Cor final da linha + espessura
                if em_caminho:
                    cor_linha = COR_VERDE
                    espessura = 3
                elif is_selecionada:
                    # Pulso intenso na cor do peso
                    cor_linha = tuple(int(c * (0.6 + 0.4 * pulso)) for c in cor_peso)
                    espessura = 3
                else:
                    # Tom esmaecido da cor do peso (60% do brilho)
                    cor_linha = tuple(int(c * 0.45) for c in cor_peso)
                    espessura = 1

                if em_caminho or is_selecionada:
                    pygame.draw.line(
                        self.tela, cor_linha, (x1 + ox, y1), (x2 + ox, y2), espessura
                    )
                else:
                    self._desenhar_linha_pontilhada(
                        x1 + ox, y1, x2 + ox, y2, cor_linha, espessura
                    )

                mx = (x1 + x2) // 2 + ox
                my = (y1 + y2) // 2
                arestas_desenhadas.append((mx, my, peso, cor_peso, is_selecionada))

        # ─── PASSE 2: PLAQUINHAS DE PESO (opacas, por cima das linhas) ────
        for mx, my, peso, cor, destaque in arestas_desenhadas:
            self._desenhar_plaquinha_peso(mx, my, peso, cor, destaque)

        # ─── PASSE 3: NÓS ─────────────────────────────────────────────────
        for nome, (nx, ny) in nos_pos.items():
            is_cur = nome == fase.no_atual
            is_tesouro = nome == "Tesouro"
            is_inicio = nome == "Inicio"
            is_destino = nome == prox_no_selecionado

            if is_cur:
                cor = COR_VERDE
                r = 14
            elif is_tesouro:
                cor = COR_AMBAR
                r = 14
            elif is_inicio:
                cor = COR_CIANO
                r = 12
            elif is_destino:
                # Nó-destino selecionado pulsa para indicar pra onde o jogador vai
                base = COR_AMBAR
                cor = tuple(int(c * (0.55 + 0.45 * pulso)) for c in base)
                r = 13
            else:
                cor = COR_TEXTO if nome in fase.caminho else COR_TEXTO_DIM
                r = 10

            # Disco de fundo escuro p/ texto não brigar com a linha
            pygame.draw.circle(self.tela, COR_BG, (nx + ox, ny), r)
            esp = 3 if (is_cur or is_tesouro or is_destino) else 1
            pygame.draw.circle(self.tela, cor, (nx + ox, ny), r, esp)

            # Marca X do tesouro
            if is_tesouro:
                x_size = 5
                pygame.draw.line(
                    self.tela,
                    COR_VERMELHO,
                    (nx + ox - x_size, ny - x_size),
                    (nx + ox + x_size, ny + x_size),
                    2,
                )
                pygame.draw.line(
                    self.tela,
                    COR_VERMELHO,
                    (nx + ox + x_size, ny - x_size),
                    (nx + ox - x_size, ny + x_size),
                    2,
                )
            else:
                # Nome curto sob/sobre o nó — usar apenas 1ª letra dentro do
                # círculo evita colisão com plaquinhas adjacentes.
                self._desenhar_texto(
                    nome[0],
                    self.fonte_pequena,
                    cor,
                    nx + ox,
                    ny,
                    centro=True,
                    sombra=True,
                )

            # Label legível abaixo/acima do círculo
            label_y = ny + r + 7
            if is_inicio:
                label_y = ny - r - 7
            self._desenhar_texto(
                nome,
                self.fonte_pequena,
                cor if (is_cur or is_destino) else COR_TEXTO_DIM,
                nx + ox,
                label_y,
                centro=True,
                sombra=True,
            )

        # ─── RODAPÉ DE INFORMAÇÃO ─────────────────────────────────────────
        info_y = AY + AH - 14
        jornada_texto = " > ".join(
            fase.caminho[-3:] if len(fase.caminho) > 3 else fase.caminho
        )
        if len(fase.caminho) > 3:
            jornada_texto = "...>" + jornada_texto

        self._desenhar_texto(
            f"Mapa: {jornada_texto}", self.fonte_pequena, COR_TEXTO, 25 + ox, info_y
        )

        cor_dias = COR_VERDE if fase.custo <= fase._custo_minimo else COR_VERMELHO
        self._desenhar_texto(
            f"Dias: {fase.custo}/{fase._custo_minimo}",
            self.fonte_texto,
            cor_dias,
            LARGURA - 75 + ox,
            info_y,
            centro=True,
        )

        if fase._vizinhos and fase.idx_acao < len(fase._vizinhos):
            prox_no, dias = fase._vizinhos[fase.idx_acao]
            cor_instrucao = tuple(int(c * (0.7 + 0.3 * pulso)) for c in COR_AMBAR)
            self._desenhar_texto(
                f"Destino: {prox_no} ({dias}d)",
                self.fonte_sub,
                cor_instrucao,
                LARGURA // 2 + ox,
                AY + 14,
                centro=True,
            )

    # ─────────────────────────────────────────────────────────────────────
    # TELA FINAL (Redimensionada)
    # ─────────────────────────────────────────────────────────────────────
    def _desenhar_tela_final(self, titulo, cor, subtitulo):
        bw, bh = 380, 180
        bx, by = (LARGURA - bw) // 2, (ALTURA - bh) // 2
        self._desenhar_moldura((bx, by, bw, bh), cor)
        self._desenhar_texto(
            titulo, self.fonte_titulo, cor, LARGURA // 2, by + 40, centro=True
        )
        self._desenhar_texto(
            subtitulo, self.fonte_texto, COR_TEXTO, LARGURA // 2, by + 85, centro=True
        )
        self._desenhar_texto(
            "[F] VOLTAR AO MENU",
            self.fonte_sub,
            COR_AMBAR,
            LARGURA // 2,
            by + 135,
            centro=True,
        )


if __name__ == "__main__":
    game = EngineVisual()
    game.rodar()
