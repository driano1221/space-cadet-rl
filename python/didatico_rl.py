"""Mostra a matematica do PPO acontecendo, passo a passo, com numeros reais
do agente treinado. Nada aqui e' inventado: tudo sai da rede e do jogo.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, torch
from spacecadet_gym import SpaceCadetEnv
from stable_baselines3 import PPO

GAMMA, LAM, N = 0.995, 0.95, 26
NOMES = ["nada", "esq", "dir", "ambos"]

env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=12000)
m = PPO.load("ppo_visao_v1", device="cpu")
pol = m.policy; pol.set_training_mode(False)

obs, _ = env.reset()
for _ in range(240):                       # aquece ate' a bola entrar em jogo
    obs, _, t1, t2, _ = env.step(int(m.predict(obs, deterministic=True)[0]))
    if t1 or t2: obs, _ = env.reset()

# roda bem mais passos e depois escolhe a janela mais informativa: a maioria
# dos passos vale zero, entao mostrar os primeiros so' exibiria esparsidade
reg = []
for i in range(400):
    lote = {k: torch.as_tensor(v[None]).float() for k, v in obs.items()}
    with torch.no_grad():
        dist = pol.get_distribution(lote)
        probs = dist.distribution.probs[0].numpy()
        valor = float(pol.predict_values(lote)[0, 0])
    a = int(np.argmax(probs))
    logp = float(np.log(probs[a] + 1e-9))
    obs, r, term, trunc, info = env.step(a)
    reg.append(dict(i=i, V=valor, a=a, p=probs.copy(), r=float(r),
                    logp=logp, score=info["score"]))
    if term or trunc: break

# escolhe a janela de N passos com maior recompensa acumulada
melhor, ini = -1, 0
for k in range(0, max(1, len(reg) - N)):
    soma = sum(e["r"] for e in reg[k:k + N])
    if soma > melhor:
        melhor, ini = soma, k
zeros = 100 * sum(1 for e in reg if e["r"] == 0) / len(reg)
print(f"[contexto] {len(reg)} passos observados; {zeros:.0f}% deles valeram ZERO.")
print(f"[contexto] janela a partir do passo {ini}, a mais movimentada.")
reg = reg[ini:ini + N]

# --- retorno descontado real (olhando para frente) -----------------------
for k, e in enumerate(reg):
    G, desc = 0.0, 1.0
    for j in range(k, len(reg)):
        G += desc * reg[j]["r"]; desc *= GAMMA
    e["G"] = G
    e["A"] = G - e["V"]

print("=" * 78)
print("O QUE A REDE VE E DECIDE, PASSO A PASSO (25 ms cada)")
print("=" * 78)
print(f"{'t':>2} {'V(s) espera':>11} {'escolhe':>8} {'confianca':>10} {'r recebe':>9} {'score':>10}")
for e in reg[:12]:
    print(f"{e['i']:>2} {e['V']:>11.2f} {NOMES[e['a']]:>8} {e['p'][e['a']]*100:>9.0f}% "
          f"{e['r']:>9.2f} {e['score']:>10,}")

print()
print("=" * 78)
print("A CONTA DA VANTAGEM:  A = G - V")
print("=" * 78)
print(f"{'t':>2} {'V (esperava)':>13} {'G (aconteceu)':>14} {'A = G-V':>10}  leitura")
for e in reg[:12]:
    leitura = "melhor que o esperado" if e["A"] > 0.5 else \
              ("pior que o esperado" if e["A"] < -0.5 else "como esperado")
    print(f"{e['i']:>2} {e['V']:>13.2f} {e['G']:>14.2f} {e['A']:>+10.2f}  {leitura}")

# --- o passo do PPO -------------------------------------------------------
print()
print("=" * 78)
print("O PASSO DO PPO: quanto a probabilidade pode mudar")
print("=" * 78)
alvo = max(reg[:12], key=lambda e: abs(e["A"]))
print(f"passo t={alvo['i']}: acao '{NOMES[alvo['a']]}' com probabilidade "
      f"{alvo['p'][alvo['a']]*100:.1f}%, vantagem A={alvo['A']:+.2f}")
print()
for novo in (0.6, 0.8, 1.0, 1.2, 1.4, 2.0):
    obj_sem = novo * alvo["A"]
    obj_com = min(novo * alvo["A"], np.clip(novo, 0.8, 1.2) * alvo["A"])
    trava = "" if abs(obj_sem - obj_com) < 1e-9 else "  <- travado pelo clip"
    print(f"  se a probabilidade mudar {novo:4.1f}x  ->  ganho {obj_com:+7.2f}{trava}")
print()
print("  E' isso que impede o salto: por mais tentador que seja, o PPO nao")
print("  aceita mudar a politica mais de 20% de uma vez.")
