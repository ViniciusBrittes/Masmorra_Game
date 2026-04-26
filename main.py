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
LARGURA = 960
ALTURA  = 640
FPS     = 30

COR_BG        = (8,  10,  14)
COR_BG_GRID   = (18, 22,  30)
COR_AMBAR     = (255, 176,  58)
COR_AMBAR_DIM = (140,  90,  20)
COR_CIANO     = (88,  220, 230)
COR_CIANO_DIM = (30,   90, 100)
COR_VERDE     = (120, 255, 140)
COR_ROXO      = (180, 120, 255)
COR_VERMELHO  = (255,  95,  85)
COR_TEXTO     = (230, 220, 200)
COR_TEXTO_DIM = (110, 100,  85)
COR_MOLDURA   = (200, 140,  40)


# ═══════════════════════════════════════════════════════════════════════════
# ENGINE VISUAL
# ═══════════════════════════════════════════════════════════════════════════
class EngineVisual:
    def __init__(self):
        pygame.init()
        self.tela  = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("MASMORRA DAS ESTRUTURAS DE DADOS")
        self.clock = pygame.time.Clock()

        self.fonte_titulo  = pygame.font.SysFont("couriernew,consolas,monospace", 42, bold=True)
        self.fonte_sub     = pygame.font.SysFont("couriernew,consolas,monospace", 22, bold=True)
        self.fonte_texto   = pygame.font.SysFont("couriernew,consolas,monospace", 20)
        self.fonte_mono_g  = pygame.font.SysFont("couriernew,consolas,monospace", 28, bold=True)
        self.fonte_pequena = pygame.font.SysFont("couriernew,consolas,monospace", 16)

        self.fases          = criar_fases()
        self.fase_atual_num = 1
        self.estado         = "MENU"
        self.menu_idx       = 0
        self.menu_itens     = ["INICIAR EXPEDICAO", "SAIR DA MASMORRA"]

        self.flash_timer = 0
        self.flash_cor   = None
        self.shake_timer = 0

        self.tick       = 0
        self.particulas = []
        self._gerar_particulas_bg()
# ─────────────────────────────────────────────────────────────────────
    # MENU PRINCIPAL
    # ─────────────────────────────────────────────────────────────────────
    def _desenhar_menu(self):
        # Caixa / Moldura principal do menu
        bw, bh = 700, 400
        bx, by = (LARGURA - bw) // 2, (ALTURA - bh) // 2 - 20
        self._desenhar_moldura((bx, by, bw, bh), COR_MOLDURA)

        # Títulos
        self._desenhar_texto("MASMORRA DAS", self.fonte_titulo, COR_VERDE,
                             LARGURA // 2, by + 60, centro=True)
        self._desenhar_texto("ESTRUTURAS DE DADOS", self.fonte_titulo, COR_VERDE,
                             LARGURA // 2, by + 110, centro=True)

        # Itens do Menu
        for i, item in enumerate(self.menu_itens):
            is_sel = (i == self.menu_idx)
            cor = COR_AMBAR if is_sel else COR_TEXTO_DIM
            txt = f">> {item} <<" if is_sel else f"   {item}   "
            y = by + 220 + (i * 60)
            
            self._desenhar_texto(txt, self.fonte_mono_g, cor,
                                 LARGURA // 2, y, centro=True)

        # Rodapé de controles
        self._desenhar_texto("[W/S] NAVEGAR   [F/ESPAÇO] CONFIRMAR", self.fonte_pequena, COR_TEXTO_DIM,
                             LARGURA // 2, ALTURA - 40, centro=True)
    # ─────────────────────────────────────────────────────────────────────
    # LOOP PRINCIPAL
    # ─────────────────────────────────────────────────────────────────────
    def rodar(self):
        while True:
            self.tick += 1
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if evento.type == pygame.KEYDOWN:
                    self._processar_teclado(evento.key)

            self._desenhar_fundo()

            if self.estado == "MENU":
                self._desenhar_menu()
            elif self.estado == "JOGANDO":
                self._desenhar_fase()
            elif self.estado == "VITORIA":
                self._desenhar_tela_final("VITORIA",   COR_VERDE,
                                          "A MASMORRA FOI CONQUISTADA")
            elif self.estado == "DERROTA":
                self._desenhar_tela_final("GAME OVER", COR_VERMELHO,
                                          "AS SOMBRAS DA MASMORRA TE CONSUMIRAM")

            if self.flash_timer > 0:
                self._aplicar_flash()

            self._aplicar_scanlines()
            pygame.display.flip()
            self.clock.tick(FPS)

    # ─────────────────────────────────────────────────────────────────────
    # INPUT
    # ─────────────────────────────────────────────────────────────────────
    def _processar_teclado(self, tecla):
        if self.estado == "MENU":
            if tecla in (pygame.K_w, pygame.K_UP):
                self.menu_idx = (self.menu_idx - 1) % len(self.menu_itens)
            elif tecla in (pygame.K_s, pygame.K_DOWN):
                self.menu_idx = (self.menu_idx + 1) % len(self.menu_itens)
            elif tecla in (pygame.K_f, pygame.K_SPACE, pygame.K_RETURN):
                if self.menu_idx == 0:
                    self.estado = "JOGANDO"
                    self.fases  = criar_fases()
                    self.fase_atual_num = 1
                else:
                    pygame.quit(); sys.exit()

        elif self.estado == "JOGANDO":
            fase = self.fases[self.fase_atual_num]
            if tecla in (pygame.K_a, pygame.K_LEFT):
                fase.move(-1)
            elif tecla in (pygame.K_d, pygame.K_RIGHT):
                fase.move(1)
            elif tecla in (pygame.K_w, pygame.K_UP):
                fase.entrar()
            elif tecla in (pygame.K_s, pygame.K_DOWN):
                fase.sair()
            elif tecla in (pygame.K_f, pygame.K_SPACE, pygame.K_RETURN):
                resultado = fase.apply_selected()
                if resultado == "win":
                    self._disparar_flash(COR_VERDE, 12)
                    self.fase_atual_num += 1
                    if self.fase_atual_num > 4:
                        self.estado = "VITORIA"
                    else:
                        self.fases[self.fase_atual_num].reset()
                elif resultado == "lose":
                    self._disparar_shake(15)
                    self._disparar_flash(COR_VERMELHO, 12)
                    self.estado = "DERROTA"

        elif self.estado in ("VITORIA", "DERROTA"):
            if tecla in (pygame.K_f, pygame.K_SPACE, pygame.K_RETURN):
                self.estado = "MENU"
                self.fase_atual_num = 1
                self.fases = criar_fases()

    # ─────────────────────────────────────────────────────────────────────
    # FUNDO / EFEITOS
    # ─────────────────────────────────────────────────────────────────────
    def _gerar_particulas_bg(self):
        self.particulas = [
            {"x": random.randint(0, LARGURA), "y": random.randint(0, ALTURA),
             "vy": random.uniform(0.2, 0.8),  "size": random.choice([1, 1, 2]),
             "brilho": random.randint(60, 150)}
            for _ in range(40)
        ]

    def _desenhar_fundo(self):
        self.tela.fill(COR_BG)
        for x in range(0, LARGURA, 40):
            pygame.draw.line(self.tela, COR_BG_GRID, (x, 0), (x, ALTURA), 1)
        for y in range(0, ALTURA, 40):
            pygame.draw.line(self.tela, COR_BG_GRID, (0, y), (LARGURA, y), 1)
        for p in self.particulas:
            p["y"] -= p["vy"]
            if p["y"] < 0:
                p["y"] = ALTURA; p["x"] = random.randint(0, LARGURA)
            c = (p["brilho"], p["brilho"]*2//3, p["brilho"]//3)
            pygame.draw.circle(self.tela, c, (int(p["x"]), int(p["y"])), p["size"])
        self._vinheta()

    def _vinheta(self):
        ov = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        for i in range(60):
            a = int(80 * (i / 60) ** 2)
            pygame.draw.rect(ov, (0, 0, 0, a), (i, i, LARGURA-2*i, ALTURA-2*i), 1)
        self.tela.blit(ov, (0, 0))

    def _aplicar_scanlines(self):
        ov = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        for y in range(0, ALTURA, 3):
            pygame.draw.line(ov, (0, 0, 0, 35), (0, y), (LARGURA, y), 1)
        self.tela.blit(ov, (0, 0))

    def _aplicar_flash(self):
        ov = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        a  = int(160 * (self.flash_timer / 12))
        ov.fill((*self.flash_cor, a))
        self.tela.blit(ov, (0, 0))
        self.flash_timer -= 1

    def _disparar_flash(self, cor, frames):
        self.flash_cor = cor; self.flash_timer = frames

    def _disparar_shake(self, frames):
        self.shake_timer = frames

    def _offset_shake(self):
        if self.shake_timer > 0:
            self.shake_timer -= 1
            return random.randint(-5, 5), random.randint(-5, 5)
        return 0, 0

    # ─────────────────────────────────────────────────────────────────────
    # PRIMITIVAS
    # ─────────────────────────────────────────────────────────────────────
    def _desenhar_moldura(self, rect, cor=COR_MOLDURA, titulo=None):
        x, y, w, h = rect
        pygame.draw.rect(self.tela, cor, rect, 2)
        pygame.draw.rect(self.tela, cor, (x+4, y+4, w-8, h-8), 1)
        for cx, cy in [(x,y),(x+w,y),(x,y+h),(x+w,y+h)]:
            pygame.draw.circle(self.tela, cor, (cx, cy), 3)
        if titulo:
            t = self.fonte_pequena.render(f" {titulo} ", True, COR_BG, cor)
            self.tela.blit(t, (x+20, y-8))

    def _desenhar_texto(self, texto, fonte, cor, x, y, centro=False, sombra=True):
        if sombra:
            s = fonte.render(texto, True, (0, 0, 0))
            r = s.get_rect()
            if centro: r.center  = (x+2, y+2)
            else:      r.topleft = (x+2, y+2)
            self.tela.blit(s, r)
        sup = fonte.render(texto, True, cor)
        r   = sup.get_rect()
        if centro: r.center  = (x, y)
        else:      r.topleft = (x, y)
        self.tela.blit(sup, r)

    def _glow(self):
        return (math.sin(self.tick * 0.12) + 1) / 2

    # ─────────────────────────────────────────────────────────────────────
    # FRAME COMPARTILHADO (cabeçalho + hint + rodapé)
    # ─────────────────────────────────────────────────────────────────────
    def _desenhar_frame_fase(self, ox, oy):
        fase  = self.fases[self.fase_atual_num]
        nomes = {1:"PILHA (LIFO)", 2:"FILA (FIFO)",
                 3:"ARRAY (INDICES)", 4:"GRAFOS (MENOR CAMINHO)"}

        # cabeçalho
        self._desenhar_moldura((20+ox, 15+oy, LARGURA-40, 62),
                               COR_CIANO_DIM, titulo=f"FASE {self.fase_atual_num}/4")
        self._desenhar_texto(nomes.get(self.fase_atual_num,"???"),
                             self.fonte_sub, COR_CIANO,
                             LARGURA//2+ox, 46+oy, centro=True)
        for i in range(4):
            cx = 55+i*28+ox; cy = 46+oy; idx = i+1
            cor = (COR_VERDE   if idx < self.fase_atual_num  else
                   COR_AMBAR   if idx == self.fase_atual_num else
                   COR_TEXTO_DIM)
            pts = [(cx,cy-6),(cx+6,cy),(cx,cy+6),(cx-6,cy)]
            pygame.draw.polygon(self.tela, cor, pts,
                                0 if idx <= self.fase_atual_num else 1)

        # dica / desafio
        self._desenhar_moldura((20+ox, 87+oy, LARGURA-40, 50),
                               COR_AMBAR_DIM, titulo="DESAFIO")
        self._desenhar_texto(f"> {fase.hint()}", self.fonte_texto,
                             COR_AMBAR, 38+ox, 103+oy)

        # rodapé de teclas
        if self.fase_atual_num == 1:
            teclas = "[A/D] ESCOLHER COLUNA    [W] MARCAR ORIGEM    [S] CANCELAR    [F] MOVER"
        else:
            teclas = "[A/D] NAVEGAR ACOES    [F] EXECUTAR"
        self._desenhar_texto(teclas, self.fonte_pequena, COR_TEXTO_DIM,
                             LARGURA//2+ox, ALTURA-30+oy, centro=True)

    # ─────────────────────────────────────────────────────────────────────
    # DISPATCHER
    # ─────────────────────────────────────────────────────────────────────
    def _desenhar_fase(self):
        ox, oy = self._offset_shake()
        self._desenhar_frame_fase(ox, oy)
        if   self.fase_atual_num == 1: self._desenhar_pilha_visual(ox, oy)
        elif self.fase_atual_num == 2: self._desenhar_fila_visual(ox, oy)
        elif self.fase_atual_num == 3: self._desenhar_array_visual(ox, oy)
        elif self.fase_atual_num == 4: self._desenhar_grafo_visual(ox, oy)

    # ─────────────────────────────────────────────────────────────────────
    # ★  FASE 1 — PILHA  (3 colunas + coluna meta)
    # ─────────────────────────────────────────────────────────────────────
    def _desenhar_pilha_visual(self, ox, oy):
        fase = self.fases[1]

        AY = 147 + oy   # início da área de estado
        AH = 388        # altura
        self._desenhar_moldura((20+ox, AY, LARGURA-40, AH),
                               COR_MOLDURA, titulo="ESTADO DA PILHA")

        BW, BH, GAP = 90, 42, 6
        BASE_Y = AY + AH - 28   # linha do chão das colunas
        MAX    = 4               # blocos por coluna

        # ── Coluna META (referência, à esquerda) ──────────────────────────
        meta_cx = 90 + ox
        self._desenhar_texto("META", self.fonte_pequena, COR_ROXO,
                             meta_cx, AY+16, centro=True, sombra=False)
        for i, val in enumerate(fase.meta):
            bx = meta_cx - 38
            by = BASE_Y - BH - i*(BH+GAP) - 4
            pygame.draw.rect(self.tela, (35, 25, 55), (bx, by, 76, BH))
            pygame.draw.rect(self.tela, COR_ROXO,     (bx, by, 76, BH), 1)
            self._desenhar_texto(str(val), self.fonte_mono_g, COR_ROXO,
                                 meta_cx, by+BH//2, centro=True, sombra=False)
        pygame.draw.line(self.tela, COR_ROXO,
                         (meta_cx-44, BASE_Y), (meta_cx+44, BASE_Y), 2)
        # linha divisória vertical
        pygame.draw.line(self.tela, COR_TEXTO_DIM,
                         (meta_cx+54, AY+10), (meta_cx+54, BASE_Y+10), 1)

        # ── 3 colunas de trabalho ─────────────────────────────────────────
        COLUNAS = [
            (fase.inicial,  "INICIAL",  COR_AMBAR, 0),
            (fase.auxiliar, "AUXILIAR", COR_CIANO, 1),
            (fase.final,    "FINAL",    COR_VERDE, 2),
        ]
        col_xs = [310+ox, 520+ox, 730+ox]

        for dados, rotulo, cor, col_idx in COLUNAS:
            cx        = col_xs[col_idx]
            is_sel    = (fase.idx_acao == col_idx)
            is_origem = (fase.origem is not None and fase.origem == col_idx)

            # cor de destaque conforme estado
            if is_origem:
                dest_cor = COR_VERDE        # verde = "esta coluna é a origem"
            elif is_sel:
                dest_cor = cor              # cor normal saturada
            else:
                dest_cor = tuple(c//4 for c in cor)  # escurecido

            # rótulo da coluna
            lbl = f"[ {rotulo} ]" if is_sel else f"  {rotulo}  "
            self._desenhar_texto(lbl, self.fonte_sub, dest_cor,
                                 cx, AY+16, centro=True, sombra=False)

            # badge ORIGEM
            if is_origem:
                self._desenhar_texto("< ORIGEM >", self.fonte_pequena, COR_VERDE,
                                     cx, AY+38, centro=True, sombra=False)

            # slots vazios acima dos itens
            for slot in range(len(dados), MAX):
                bx = cx - BW//2
                by = BASE_Y - BH - slot*(BH+GAP) - 4
                dim = tuple(max(c//6, 10) for c in cor)
                pygame.draw.rect(self.tela, dim, (bx, by, BW, BH), 1)

            # blocos com valores (0 = base, último = topo)
            for i, val in enumerate(dados):
                is_topo = (i == len(dados)-1)
                bx = cx - BW//2
                by = BASE_Y - BH - i*(BH+GAP) - 4

                # fundo do bloco
                bg = tuple(max(int(c*0.13), 8) for c in cor)
                pygame.draw.rect(self.tela, bg, (bx, by, BW, BH))

                # borda: grossa e brilhante no topo
                b_cor   = dest_cor if is_topo else tuple(max(int(c*0.45),10) for c in cor)
                b_thick = 3 if is_topo else 1
                pygame.draw.rect(self.tela, b_cor, (bx, by, BW, BH), b_thick)

                # cantoneiras no topo selecionado
                if is_topo and is_sel:
                    for ex, ey in [(bx,by),(bx+BW,by),(bx,by+BH),(bx+BW,by+BH)]:
                        pygame.draw.circle(self.tela, b_cor, (ex, ey), 3)

                # número
                n_cor = dest_cor if is_topo else tuple(max(int(c*0.5),10) for c in cor)
                self._desenhar_texto(str(val), self.fonte_mono_g, n_cor,
                                     cx, by+BH//2, centro=True, sombra=False)

            # label TOPO acima do bloco mais alto
            if dados:
                ti = len(dados)-1
                tb = BASE_Y - BH - ti*(BH+GAP) - 4
                self._desenhar_texto("TOPO v", self.fonte_pequena, dest_cor,
                                     cx, tb-16, centro=True, sombra=False)
            else:
                self._desenhar_texto("VAZIA", self.fonte_pequena,
                                     tuple(c//5 for c in cor),
                                     cx, BASE_Y-90, centro=True, sombra=False)

            # linha de chão
            pygame.draw.line(self.tela, dest_cor,
                             (cx-BW//2-8, BASE_Y), (cx+BW//2+8, BASE_Y), 2)

        # ── seta animada origem → destino ────────────────────────────────
        if fase.origem is not None and fase.origem != fase.idx_acao:
            p   = self._glow()
            ac  = tuple(int(c*(0.55+0.45*p)) for c in COR_TEXTO)
            ax1 = col_xs[fase.origem]
            ax2 = col_xs[fase.idx_acao]
            ay  = BASE_Y - BH*2 - 24
            pygame.draw.line(self.tela, ac, (ax1, ay), (ax2, ay), 2)
            dx = 1 if ax2 > ax1 else -1
            pygame.draw.polygon(self.tela, ac,
                                [(ax2, ay-7),(ax2+dx*14, ay),(ax2, ay+7)])
            self._desenhar_texto("mover para ca", self.fonte_pequena, ac,
                                 (ax1+ax2)//2, ay-18, centro=True, sombra=False)

        # ── contador de movimentos ───────────────────────────────────────
        restam  = fase.max_movimentos - fase.movimentos
        cor_mov = COR_VERDE if restam > 12 else COR_AMBAR if restam > 5 else COR_VERMELHO
        self._desenhar_texto(
            f"MOVIMENTOS: {fase.movimentos}/{fase.max_movimentos}  ({restam} restantes)",
            self.fonte_pequena, cor_mov,
            LARGURA//2+ox, AY+AH-13, centro=True, sombra=False)

    # ─────────────────────────────────────────────────────────────────────
    # FASE 2 — FILA
    # ─────────────────────────────────────────────────────────────────────
    def _desenhar_fila_visual(self, ox, oy):
        fase = self.fases[2]
        AY = 147+oy; AH = 240
        self._desenhar_moldura((20+ox, AY, LARGURA-40, AH),
                               COR_MOLDURA, titulo="ESTADO DA FILA")

        BW, BH = 52, 46

        # esteira
        self._desenhar_texto("ESTEIRA  (frente -> fim):", self.fonte_pequena,
                             COR_TEXTO_DIM, 38+ox, AY+18)
        for i, letra in enumerate(fase.esteira):
            bx = 38+ox + i*(BW+8); by = AY+38
            is_f = (i == 0)
            cor  = COR_AMBAR if is_f else COR_TEXTO_DIM
            t    = 3 if is_f else 1
            pygame.draw.rect(self.tela, (22,16,6), (bx, by, BW, BH))
            pygame.draw.rect(self.tela, cor,       (bx, by, BW, BH), t)
            self._desenhar_texto(letra, self.fonte_mono_g, cor,
                                 bx+BW//2, by+BH//2, centro=True, sombra=False)
            if is_f:
                self._desenhar_texto("SAIDA", self.fonte_pequena, cor,
                                     bx+BW//2, by-14, centro=True, sombra=False)

        # placar
        self._desenhar_texto("PLACAR:", self.fonte_pequena,
                             COR_TEXTO_DIM, 38+ox, AY+108)
        for i in range(len(fase.gabarito)):
            bx = 38+ox + i*(BW+8); by = AY+128
            ok  = i < len(fase.placar)
            cor = COR_VERDE if ok else tuple(c//5 for c in COR_VERDE)
            pygame.draw.rect(self.tela, (8,20,10) if ok else COR_BG, (bx,by,BW,BH))
            pygame.draw.rect(self.tela, cor, (bx,by,BW,BH), 2 if ok else 1)
            txt = fase.placar[i] if ok else "?"
            self._desenhar_texto(txt, self.fonte_mono_g, cor,
                                 bx+BW//2, by+BH//2, centro=True, sombra=False)

        # ação selecionada
        ay2 = AY+AH+10
        self._desenhar_moldura((20+ox, ay2, LARGURA-40, 90),
                               COR_CIANO_DIM, titulo="ACAO SELECIONADA")
        self._desenhar_texto(f"<< {fase.selected_action()} >>",
                             self.fonte_sub, COR_AMBAR,
                             LARGURA//2+ox, ay2+44, centro=True)

    # ─────────────────────────────────────────────────────────────────────
    # FASE 3 — ARRAY
    # ─────────────────────────────────────────────────────────────────────
    def _desenhar_array_visual(self, ox, oy):
        fase = self.fases[3]
        AY = 147+oy; AH = 168
        self._desenhar_moldura((20+ox, AY, LARGURA-40, AH),
                               COR_MOLDURA, titulo="ESTADO DO ARRAY")

        BW = 104; BH = 56; by = AY+60
        n  = len(fase.sequencia)
        sx = (LARGURA - n*BW - (n-1)*10)//2 + ox

        for i in range(n):
            bx      = sx + i*(BW+10)
            show    = fase.tempo_memorizar > 0 or i < len(fase.usuario)
            is_cur  = fase.tempo_memorizar <= 0 and i == len(fase.usuario)
            preench = i < len(fase.usuario)

            if fase.tempo_memorizar > 0:
                val = fase.sequencia[i]; cor = COR_AMBAR
            elif preench:
                val = fase.usuario[i];   cor = COR_VERDE
            elif is_cur:
                val = "?";               cor = COR_CIANO
            else:
                val = "?";               cor = COR_TEXTO_DIM

            thick = 3 if is_cur else 2 if preench else 1
            pygame.draw.rect(self.tela, tuple(max(int(c*0.10),8) for c in cor),
                             (bx, by, BW, BH))
            pygame.draw.rect(self.tela, cor, (bx, by, BW, BH), thick)
            self._desenhar_texto(str(val), self.fonte_mono_g, cor,
                                 bx+BW//2, by+BH//2, centro=True, sombra=False)
            self._desenhar_texto(f"[{i}]", self.fonte_pequena,
                                 tuple(c//2 for c in cor),
                                 bx+BW//2, by+BH+8, centro=True, sombra=False)

        ay2 = AY+AH+10
        self._desenhar_moldura((20+ox, ay2, LARGURA-40, 90),
                               COR_CIANO_DIM, titulo="ACAO SELECIONADA")
        self._desenhar_texto(f"<< {fase.selected_action()} >>",
                             self.fonte_sub, COR_AMBAR,
                             LARGURA//2+ox, ay2+44, centro=True)

    # ─────────────────────────────────────────────────────────────────────
    # FASE 4 — GRAFOS
    # ─────────────────────────────────────────────────────────────────────
    def _desenhar_grafo_visual(self, ox, oy):
        fase = self.fases[4]
        AY = 147+oy; AH = 248
        self._desenhar_moldura((20+ox, AY, LARGURA-40, AH),
                               COR_MOLDURA, titulo="GRAFO DE NAVEGACAO")

        # posições fixas para o grafo A-B-C-D
        nos_pos = {
            "A": (170, AY+100),
            "B": (400, AY+45),
            "C": (400, AY+165),
            "D": (630, AY+105),
        }

        # arestas
        for no, vizinhos in fase.grafo.items():
            x1, y1 = nos_pos[no]
            for v, peso in vizinhos:
                x2, y2 = nos_pos[v]
                if no < v:
                    pygame.draw.line(self.tela, COR_TEXTO_DIM,
                                     (x1+ox, y1), (x2+ox, y2), 1)
                    mx = (x1+x2)//2+ox; my = (y1+y2)//2
                    self._desenhar_texto(str(peso), self.fonte_pequena,
                                         COR_AMBAR, mx, my,
                                         centro=True, sombra=False)

        # caminho percorrido
        for i in range(len(fase.caminho)-1):
            x1,y1 = nos_pos[fase.caminho[i]]
            x2,y2 = nos_pos[fase.caminho[i+1]]
            pygame.draw.line(self.tela, COR_VERDE,
                             (x1+ox, y1), (x2+ox, y2), 3)

        # nós
        for nome, (nx, ny) in nos_pos.items():
            is_cur  = nome == fase.no_atual
            is_alvo = nome == fase.alvo
            is_ini  = nome == fase.inicio
            cor = (COR_VERDE   if is_cur  else
                   COR_AMBAR   if is_alvo else
                   COR_CIANO   if is_ini  else
                   COR_TEXTO_DIM)
            r = 26 if is_cur else 22
            pygame.draw.circle(self.tela,
                               tuple(max(int(c*0.15),8) for c in cor),
                               (nx+ox, ny), r)
            pygame.draw.circle(self.tela, cor, (nx+ox, ny), r,
                               3 if is_cur else 1)
            self._desenhar_texto(nome, self.fonte_sub, cor,
                                 nx+ox, ny, centro=True, sombra=False)
            lbl = ("AQUI"   if is_cur  else
                   "ALVO"   if is_alvo else
                   "INICIO" if is_ini  else "")
            if lbl:
                self._desenhar_texto(lbl, self.fonte_pequena, cor,
                                     nx+ox, ny+r+12, centro=True, sombra=False)

        # caminho + custo
        self._desenhar_texto(
            f"Caminho: {' -> '.join(fase.caminho)}   |   Custo: {fase.custo}",
            self.fonte_texto, COR_TEXTO, 38+ox, AY+AH-28)

        ay2 = AY+AH+10
        self._desenhar_moldura((20+ox, ay2, LARGURA-40, 90),
                               COR_CIANO_DIM, titulo="ACAO SELECIONADA")
        self._desenhar_texto(f"<< {fase.selected_action()} >>",
                             self.fonte_sub, COR_AMBAR,
                             LARGURA//2+ox, ay2+44, centro=True)

    # ─────────────────────────────────────────────────────────────────────
    # TELA FINAL
    # ─────────────────────────────────────────────────────────────────────
    def _desenhar_tela_final(self, titulo, cor, subtitulo):
        bw, bh = 640, 260
        bx, by = (LARGURA-bw)//2, (ALTURA-bh)//2
        self._desenhar_moldura((bx, by, bw, bh), cor)
        self._desenhar_texto(titulo, self.fonte_titulo, cor,
                             LARGURA//2, by+70, centro=True)
        self._desenhar_texto(subtitulo, self.fonte_texto, COR_TEXTO,
                             LARGURA//2, by+130, centro=True)
        self._desenhar_texto("[F] VOLTAR AO MENU", self.fonte_sub, COR_AMBAR,
                             LARGURA//2, by+210, centro=True)


if __name__ == "__main__":
    game = EngineVisual()
    game.rodar()
