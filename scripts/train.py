"""Interface de treino com nomes em vez de argumentos posicionais.

O treinador original (python/treinar_visao_par.py) recebe 14 argumentos
posicionais, o que e' pratico para varrer experimentos e pessimo para quem chega
agora. Este wrapper aceita flags ou um arquivo de configuracao.

    python scripts/train.py --config configs/trajectory.yaml
    python scripts/train.py --steps 2500000 --tag teste --trajectory-prediction
"""
import argparse
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TREINADOR = os.path.join(RAIZ, "python", "treinar_visao_par.py")

# ordem exata que treinar_visao_par.py espera em sys.argv
POSICIONAIS = ["steps", "tag", "envs", "reward", "progress", "target", "multiplier",
               "medal", "flip_cost", "strike", "prediction", "potential",
               "novelty", "balls"]
PADRAO = {"steps": 2_500_000, "tag": "run", "envs": 6, "reward": "score",
          "progress": 0.0, "target": 0.0, "multiplier": 0.0, "medal": 0.0,
          "flip_cost": 0.0, "strike": 0.0, "prediction": False,
          "potential": 0.0, "novelty": 0.0, "balls": 0}


def carregar(caminho):
    import yaml
    with open(caminho, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", help="arquivo YAML em configs/")
    p.add_argument("--steps", type=int, help="passos de treino")
    p.add_argument("--tag", help="nome do agente")
    p.add_argument("--envs", type=int, help="ambientes paralelos")
    p.add_argument("--trajectory-prediction", action="store_true",
                   help="expoe quando/onde a bola cruza a linha dos flippers")
    p.add_argument("--progress", type=float, help="peso do shaping de progresso")
    p.add_argument("--potential", type=float, help="peso do shaping por potencial")
    p.add_argument("--novelty", type=float, help="peso do bonus de novidade")
    p.add_argument("--balls", type=int, help="bolas por partida (0 = padrao, 3)")
    p.add_argument("--flip-cost", type=float, help="custo por acionamento")
    p.add_argument("--dry-run", action="store_true", help="so' mostra o comando")
    a = p.parse_args()

    cfg = dict(PADRAO)
    if a.config:
        cfg.update(carregar(a.config))
    for chave, valor in [("steps", a.steps), ("tag", a.tag), ("envs", a.envs),
                         ("progress", a.progress), ("potential", a.potential),
                         ("novelty", a.novelty), ("balls", a.balls),
                         ("flip_cost", a.flip_cost)]:
        if valor is not None:
            cfg[chave] = valor
    if a.trajectory_prediction:
        cfg["prediction"] = True

    argv = []
    for nome in POSICIONAIS:
        v = cfg[nome]
        # o treinador testa a string literal "prever" nessa posicao
        argv.append("prever" if nome == "prediction" and v else
                    ("0" if nome == "prediction" else str(v)))

    cmd = [sys.executable, TREINADOR] + argv
    print(" ".join(cmd))
    if not a.dry_run:
        raise SystemExit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
