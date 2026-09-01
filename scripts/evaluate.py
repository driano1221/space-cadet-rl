"""Evaluate a trained agent over complete episodes.

    python scripts/evaluate.py --model ppo_c9_prever --episodes 10

Episodes run back to back in the same process: variance between separate runs
reaches 40%, so agents must be compared side by side, never across runs.
"""
import argparse
import os
import statistics
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "python"))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", required=True,
                    help="model name without .zip, e.g. ppo_c9_prever")
    ap.add_argument("--episodes", type=int, default=10)
    ap.add_argument("--csv", help="optional path to write per-episode rows")
    args = ap.parse_args()

    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    from stable_baselines3 import PPO
    from spacecadet_gym import SpaceCadetEnv

    caminho = args.model if os.path.exists(args.model + ".zip") else \
        os.path.join(AQUI, "..", "python", args.model)
    m = PPO.load(caminho, device="cpu")
    # the env must match the observation width the model was trained with:
    # 18 fields with trajectory prediction, 15 without
    dim = m.observation_space["vetor"].shape[0]
    env = SpaceCadetEnv(quadros_por_passo=3, visao=True, max_passos=288_000,
                        prever=(dim == 18))
    print(f"{args.model}: {dim}-field observation, prediction={dim == 18}")

    linhas = []
    for ep in range(args.episodes):
        obs, info = env.reset()
        a0, passos = info["ev_flip_acerto"], 0
        term = trunc = False
        while not (term or trunc):
            obs, _, term, trunc, info = env.step(
                int(m.predict(obs, deterministic=True)[0]))
            passos += 1
        linhas.append(dict(episode=ep, score=info["score"],
                           duration_s=round(info["tempo_s"], 1),
                           strikes=info["ev_flip_acerto"] - a0, steps=passos))
        print(f"  episode {ep}: {info['score']:>10,}  {info['tempo_s']:>6.0f}s")
    env.close()

    sc = [l["score"] for l in linhas]
    du = [l["duration_s"] for l in linhas]
    print(f"\nn = {len(sc)}")
    print(f"  score     median {statistics.median(sc):>12,.0f}"
          f"  min {min(sc):>10,}  max {max(sc):>10,}")
    print(f"  duration  median {statistics.median(du):>12,.0f}s")

    if args.csv:
        import csv
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(linhas[0]))
            w.writeheader(); w.writerows(linhas)
        print(f"  wrote {args.csv}")


if __name__ == "__main__":
    main()
