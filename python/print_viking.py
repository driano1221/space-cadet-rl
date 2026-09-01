"""Captura o jogo rodando com o DAT original e com o DAT modificado.

Gera o comparativo do painel: piloto original x viking, com a captura do
proprio emulador (render::vscreen). Nao e' montagem.

Cada captura roda em processo separado porque o modulo nativo carrega o DAT uma
vez so' por processo, e usa o SpaceCadetEnv em vez de chamar `core.iniciar`
direto (essa chamada trava sem o preparo que o env faz).
"""
import os
import shutil
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.abspath(os.path.join(AQUI, "..", "SpaceCadetPinball", "bin"))
DAT_BIN = os.path.join(BIN, "PINBALL.DAT")
ORIGINAL = r"C:\Users\drian\Games\pinball_patch\backup\PINBALL.DAT.bak"
MODIFICADO = r"C:\Users\drian\Games\SpaceCadet\Pinball\PINBALL.DAT"
SAIDA = os.path.abspath(os.path.join(AQUI, "..", "artigo", "img"))

CAPTURA = '''
import os, sys
sys.path.insert(0, r"{aqui}")
import numpy as np
from PIL import Image
from spacecadet_gym import SpaceCadetEnv
import spacecadet_env as core

env = SpaceCadetEnv(quadros_por_passo=3, visao=False, max_passos=5000)
env.reset()
for _ in range(30):
    env.step(0)
Image.fromarray(np.array(core.capturar_tela(), dtype=np.uint8)).save(r"{saida}")
print("ok")
os._exit(0)   # a thread nativa nao encerra sozinha
'''


def capturar(dat, destino):
    shutil.copyfile(dat, DAT_BIN)
    codigo = CAPTURA.format(aqui=AQUI, saida=destino)
    r = subprocess.run([sys.executable, "-c", codigo], capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=240)
    assert os.path.exists(destino), f"captura falhou: {r.stderr[-500:]}"
    print(f"  {os.path.basename(destino)}")


def main():
    guarda = DAT_BIN + ".guarda"
    shutil.copyfile(DAT_BIN, guarda)
    try:
        a = os.path.join(SAIDA, "_jogo_original.png")
        b = os.path.join(SAIDA, "_jogo_viking.png")
        capturar(ORIGINAL, a)
        capturar(MODIFICADO, b)

        from PIL import Image, ImageDraw
        im_a, im_b = Image.open(a), Image.open(b)
        print(f"  tela: {im_a.size}")
        # painel do piloto: alto da coluna direita
        cx, cy, cw, ch = 378, 10, 214, 175
        esc = 3
        pa = im_a.crop((cx, cy, cx + cw, cy + ch)).resize((cw * esc, ch * esc), Image.NEAREST)
        pb = im_b.crop((cx, cy, cx + cw, cy + ch)).resize((cw * esc, ch * esc), Image.NEAREST)

        m, rot = 16, 30
        comp = Image.new("RGB", (pa.width * 2 + m * 3, pa.height + rot + m), "white")
        comp.paste(pa, (m, rot))
        comp.paste(pb, (m * 2 + pa.width, rot))
        d = ImageDraw.Draw(comp)
        d.text((m + 2, 9), "original", fill=(26, 26, 26))
        d.text((m * 2 + pa.width + 2, 9), "modificado", fill=(26, 26, 26))
        destino = os.path.join(SAIDA, "viking_no_jogo.png")
        comp.save(destino)
        print(f"comparativo: {os.path.basename(destino)} {comp.size}")
    finally:
        shutil.copyfile(guarda, DAT_BIN)
        os.remove(guarda)
        print("DAT do bin restaurado")


if __name__ == "__main__":
    main()
