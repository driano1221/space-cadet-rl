# Teaching an RL Agent to Play 3D Pinball Space Cadet

*Instrumenting the original C++ game to study what an RL agent actually learns.*

![The trained agent playing](docs/agent.gif)

| | |
|---|---|
| **2.6M** | median score, unlimited-time games |
| **4.3x** | a random policy |
| **0.62x** | that same random policy, once actions carry 250 ms of latency |

That third number is the point of the project. The agent looks strategic until
you delay its actions by a human-scale reaction time, and then it loses to
pressing buttons at random. Its edge is high-frequency reactive control, not
strategy.

## What I built

The Windows XP pinball game has a [C++ decompilation](https://github.com/k4zmu2a/SpaceCadetPinball)
that compiles and runs. Instead of screen-scraping it, I instrumented it:

1. **C++ hooks** into the physics loop expose ball position, velocity, score and
   per-event counters (bumpers, ramps, medal targets, flipper strikes).
2. **pybind11** bindings surface that state to Python as a normal module.
3. A **Gymnasium environment** wraps it, with the table rendered as a 9x36x28
   grid plus a state vector.
4. **PPO** from Stable-Baselines3 trains against it.

The physics runs headless at up to **941x real time**; a full 2.5M-step training
run takes about an hour, roughly **17x real time** end to end.

## Main finding

![Where it presses vs where it connects](docs/where_it_connects.png)

The base agent connects with the ball on only **2.3%** of its flipper presses.
Reward-based attempts to fix that all failed: penalising presses, rewarding
strikes, potential-based shaping, curiosity bonuses, a ball curriculum, 3x
longer training.

Two things did improve aim. **Action masking** raised the hit rate 20-35x, by
forbidding the flipper outside the region where it can actually reach the ball.
**Trajectory prediction** raised it 16.6% (p = 0.0008). Neither improved the
score.

What did move was survival. Across all seven trained agents, **the ranking by
score is identical to the ranking by episode duration**. In this game the table
scores the points; the flippers only keep the ball alive, and a raised flipper
works as a wall that needs no timing at all.

**[Read the full story (PT-BR, 13 pages) →](https://driano1221.github.io/space-cadet-rl/)**

The PDF also lives in this repository, at
[docs/artigo.pdf](docs/artigo.pdf).

## Running it

You need the original `PINBALL.DAT` from a Windows XP install (not
redistributable, not included here).

The instrumented fork lives at
[driano1221/SpaceCadetPinball, branch `rl-instrumentation`](https://github.com/driano1221/SpaceCadetPinball/tree/rl-instrumentation).

```bash
# 1. build the instrumented game (needs CMake and a C++17 compiler)
cd SpaceCadetPinball && cmake -S . -B build && cmake --build build --config Release

# 2. Python side
pip install -r requirements.txt

# 3. evaluate a trained agent
python scripts/evaluate.py --model ppo_c9_prever --episodes 10

# 4. train from scratch (about 1h on a laptop GPU)
python python/treinar_visao_par.py 2500000 my_tag 6 score 0 0 0 0 0 0 prever

# 5. regenerate every figure in the paper
Rscript scripts/reproduce_figures.R
```

## Repository layout

```
python/          environment, trainers, self-checks and measurement scripts
  spacecadet_gym.py    the Gym env (vision, prediction, zone mask, shaping)
  treinar_*.py         trainers
  teste_*.py           assert-based self-checks
analise/         R scripts, figures, raw evaluation data
scripts/         entry points for evaluation and figure reproduction
docs/            the paper and its assets
SpaceCadetPinball/   instrumented fork, see below
```

## Method notes

Each treatment was trained **once**, with a fixed seed, and evaluated on 10
complete episodes. That characterises the trained policy well but does not
substitute for independent training runs; read causal claims as "in this run,
holding everything else fixed". The p-values are exploratory and not corrected
for multiple comparisons.

Evaluations run back to back in the same process, since variance between
separate runs reaches 40%. Comparisons use Mann-Whitney; episodes do not share
seeds, so these are not paired tests.

## Acknowledgements

- [k4zmu2a/SpaceCadetPinball](https://github.com/k4zmu2a/SpaceCadetPinball),
  the decompilation this whole project rests on (MIT)
- [Stable-Baselines3](https://github.com/DLR-RM/stable-baselines3) for the PPO
  implementation
- [ViZDoom](https://arxiv.org/abs/1605.02097), which established instrumenting
  open-source games for RL back in 2016
- *Pinbot: Applying Reinforcement Learning to Pinball Machines* (CMU 16-831,
  2024), which independently hit the same two failure modes

The game's artwork and `PINBALL.DAT` belong to Microsoft and Maxis. Screenshots
here are used to document the experiments; no game asset is redistributed.

## License

MIT for the code in this repository. The instrumented fork keeps the original
MIT license of the decompilation.
