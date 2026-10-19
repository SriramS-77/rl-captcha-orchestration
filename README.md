# Adaptive CAPTCHA Orchestration via Reinforcement Learning

Code, data and results for the paper

> **Balancing Security and Usability: Adaptive CAPTCHA Orchestration via RL**
> Manuscript: *[link to be added]*

A behavioural **Humanity Scorer** turns 10 s chunks of a user's mouse movement into
P(bot). A reinforcement-learning controller reads that score and the session history, and picks
one of 11 intervention levels for every active user. The levels range from no challenge, through
invisible checks and visible CAPTCHAs, to an audio fallback.

Policies are trained and evaluated in a simulator grounded in published CAPTCHA user studies,
with a leakage-controlled data protocol:
- **Learners.** DQN, PPO, Neural-LinUCB and Neural Thompson Sampling, compared with static score
  thresholds.
- **Drift study.** It tests what happens when unseen covert bots break the scorer's calibration,
  and compares offline training, online training with label-free and audit-based rewards, and
  online training gated by a CUSUM drift detector.

## Repository layout

```text
rlcaptcha/          core package: session chunking, metrics, rewards, policies, simulation loop
experiments/        everything behind the paper's numbers (see experiments/README.md)
  expkit/             experiment library: split, scorer, cross-fitting, simulator, learners, rewards
  paper/              one script per table / figure / result of the paper
  models/             the Humanity Scorer used throughout and the selected policy architectures
  results/            the outputs behind every number in the paper, incl. trained Table 4 agents
data/
  recordings/         our 156 mouse recordings (44 human, 112 bot), cursor trajectories only
  external/           instructions for the two third-party datasets (not redistributed)
```

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt                        # Python 3.12

cd experiments
python paper/make_tables.py           # Tables 3-6, rebuilt from the shipped results
python paper/make_drift_figure.py     # Fig. 4 -> results/figures/drift.pdf
python paper/make_pareto_figure.py    # Fig. 5 -> results/figures/pareto.pdf
```

To rerun the experiments themselves (the scorer evaluation, Table 4's training and evaluation,
the sensitivity checks, and the drift, audit and gated studies), follow
[`experiments/README.md`](experiments/README.md). It maps each item of the paper to its command,
its output file and its approximate compute cost. The drift-related experiments also need the
two public datasets described in [`data/external/README.md`](data/external/README.md).

## Results at a glance

On the held-out evaluation block (fixed traffic: 100 humans, 20–1000 bots; DI = % humans kept −
% bots let through):

| Policy | DI | Humans kept | Friction (s per human) |
|---|---|---|---|
| PPO | 99.8 ± 0.6 | 99.8 % | 0.1 |
| DQN | 97.8 ± 1.2 | 97.8 % | 1.3 |
| Best static policy (Neyman–Pearson threshold) | 95.5 | 95.5 % | 3.0 |
| DQN without the Humanity Score | 16.8 ± 7.5 | 61.4 % | 20.0 |

Under covert bots that shift the scorer's calibration (ρ = 1), frozen PPO falls to DI 3.8. PPO
trained online with the label-free score-only reward keeps DI 82.7, against 39.5 for the best
static policy. Training online only after a CUSUM detector raises an alarm keeps the frozen
policy's 99.8 when nothing changes.

## Citation

*To be added.*

## License

*To be added.*
