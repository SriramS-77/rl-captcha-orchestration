# Reproducing the paper

Every command below is run from this folder (`experiments/`). All results are on **fold 2** of
the recording split (`results/rotation.json`).

The repository ships the outputs behind every number in the paper under `results/`. You can
therefore:

1. **Rebuild the tables and figures from the shipped outputs.** This takes seconds and needs no
   external data:

   ```bash
   python paper/make_tables.py            # Tables 3-6
   python paper/make_drift_figure.py      # Fig. 4 -> results/figures/drift.pdf
   python paper/make_pareto_figure.py     # Fig. 5 -> results/figures/pareto.pdf
   ```
2. **Rerun any experiment** (§2 and §3 below) and compare its new CSVs with the shipped ones.

## 1. Setup

```bash
pip install -r ../requirements.txt                       # Python 3.12 (Linux CPU-only torch:
                                                         #   add --extra-index-url https://download.pytorch.org/whl/cpu)
python -m expkit.external --build --check                # needs the downloads in ../data/external/
python paper/drift_study.py --setup                      # scorer -> results/scorer/, scores the external data
```

- **External data.** The build needs the two third-party datasets downloaded first; see
  [`../data/external/README.md`](../data/external/README.md). Experiments on our recordings
  alone (§IV-A, Table 4, §IV-C) work without them. In that case skip the build: `--setup` then
  prints a note and leaves out the external scoring. Rerun `--setup` after building the cache,
  before any drift experiment (Figs. 4–5, Tables 5–6, §IV-D).
- **What `--setup` does.**
  - Copies the Humanity Scorer from `models/humanity_scorer/` into `results/scorer/`.
  - Loads all six scorers: five cross-fitted ones and the refit used for evaluation. It must
    print `LOADED ... none refitted`. If it tries to fit, the recordings do not match the
    scorer's provenance; stop.
  - Copies `models/arch_choice.json` and scores the external sessions once
    (`results/ext_scores.pkl`).

**Writing to a fresh folder.** Every runner skips a task whose output CSV already exists, and
the shipped CSVs already exist. To recompute rather than skip, write to a fresh folder:

```bash
export RESULTS_OUT=$PWD/results_rerun        # every script in paper/ honours it
python paper/drift_study.py --setup          # once per output folder
```

Without `RESULTS_OUT`, a rerun skips existing tasks and fills in only missing ones under
`results/`.

**Smoke tests.** These use a toy budget and the RL validation block only. The evaluation block
stays closed, and they finish in minutes:

```bash
python paper/grounded_headline.py --smoke
python paper/drift_study.py --smoke
```

## 2. Paper item → command → output

`J` is the number of parallel processes; each task is one single-threaded subprocess.
Approximate CPU time is from our runs on a desktop CPU.

| Paper | Command | Output in `results/` | CPU time |
|---|---|---|---|
| §IV-A scorer on the evaluation block (AUC 0.992, Brier 0.032, ECE 0.053, T = 1.14) | `python paper/scorer_eval.py` | `scorer_eval.json` | 1 min |
| §IV-A reliability / calibrators | `python paper/calib_study.py` | `calib_study.csv`, `calib_chunks.csv` | 1 min |
| **Table 3** web bot benchmark | `python paper/webbot_finetune.py` | `webbot/webbot_summary.csv` | ~1 h |
| **Table 4** RL rows | `python paper/grounded_headline.py --run-all J`, then `--collect` | `headline/*.csv`, `headline/agents/*.pt`, `headline_summary.csv`, `headline_runs.csv` | 30 h |
| Table 4 TS posterior rows | `python paper/ts_variants.py --run-all J`, then `--collect` | `ts_variants/`, `ts_variants_runs.csv` | 13 h |
| Table 4 NP rows | `python paper/np_headline.py`; `python paper/np_multi_t4.py` | `headline/np_threshold_a0.10.csv`, `headline/np_multi_threshold_a0.10.csv` | 5 min |
| §IV-C simulator constants, population input (uses the Table 4 agents) | `python paper/grounded_extras.py --run-all J`, then `--collect` | `extras_alpha.csv`, `extras_tau.csv`, `extras_freeze.csv` | 20 h |
| §IV-C reward constants | `python paper/grounded_reward_sweep.py --run-all J`, then `--collect` | `reward_sweep_summary.csv` | 7 h |
| **Fig. 4**, and Table 5's label-based, score-only and posterior rows | `python paper/drift_study.py --run-all J`, then `--collect` | `drift/drift_curves.csv`, `drift/drift_per_seed.csv`, `drift/drift_metrics.csv` | ~140 h (417 tasks) |
| Fig. 4 NP-threshold curve | `python paper/np_drift_curve.py` | `np_drift_curve.csv` | 10 min |
| Fig. 4 audit markers, Table 5 audit rows | `python paper/np_audit.py --run-all J`, then `AUDIT_LEVELS=0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0 python paper/audit_curve.py J` | `np_audit/` | ~80 h (240 tasks) |
| **Table 5** static rows | `python paper/np_multi_equal.py`; `python paper/multi_table5.py`; `SINGLE=1 python paper/multi_table5.py` | `np_multi_equal.csv`, `multi_table5.csv`, `single_table5.csv` | 15 min |
| **Fig. 5** Pareto | `python paper/pareto.py --run-all J`, then `--collect`; `python paper/np_half.py` | `pareto_points.csv`, `np_alpha_0005.csv` | ~20 h |
| **Table 6** gated online training | `python paper/detector_calib.py` (thresholds), then `python paper/gated.py --run-all J`, then `--collect` | `detector_thresholds.json`, `gated_runs.csv` | ~30 h |
| §IV-D ranking-destroying covert bots | `python paper/auc_drift.py --run-all J` | `auc_drift/` | ~30 h |
| All tables, both figures | `python paper/make_tables.py`; `python paper/make_drift_figure.py`; `python paper/make_pareto_figure.py` | stdout; `figures/` | seconds |

**Order and dependencies.**
- Run `--setup` first.
- `grounded_extras.py` and `auc_drift.py` load the agents saved by `grounded_headline.py`.
- `gated.py` reads `detector_thresholds.json`.
- `make_drift_figure.py` needs the drift, `np_drift_curve` and `np_audit` outputs.

**Running on a cluster.** Every task-based script also takes `--list` and `--task N`, so it can
run as a Slurm array (one task per element), followed by `--collect`. For example:
`python paper/drift_study.py --list --paper` prints the 417 paper task ids.

**Reproducibility checks we ran on this repository** (a clean copy, Windows, CPU):
- Building the external cache from the raw downloads reproduces the pinned SHA-256.
- `drift_study.py --setup` loads the shipped scorers without refitting.
- It rescores the external sessions identically to the original run.
- `scorer_eval.py` and `np_headline.py` reproduce their shipped outputs exactly.
- Re-evaluating a saved Table 4 agent (`grounded_extras.py --task 5`) reproduces its shipped
  CSV exactly.
- Retraining DQN seed 0 (`grounded_headline.py --task 0`) reproduces its shipped CSV exactly.
- Both smoke tests pass, and the two figures are byte-identical to the paper's.

Torch on other platforms or with GPU kernels may differ in the last digits.

**Windows.** Task names are long. Keep the checkout at a short path, or enable long paths;
otherwise writes can fail at the 260-character `MAX_PATH` limit.

## 3. Protocol, in brief

- **Split.** Recordings are split before windowing into a scorer block, an RL block and an
  evaluation block (14 humans, 36 bots). The scorer and RL blocks form one training pool,
  cross-fitted in 5 parts. RL training sessions are scored out of fold; the evaluation block is
  scored by a refit on the whole pool.
- **Evaluation block.** It is opened only by final-evaluation tasks, and each opening is
  appended to `results/eval_access.log`. Smoke runs assert they never open it.
- **Scorer.** Cross-fit seed 1 (`models/humanity_scorer/`). Choosing seed 1 was post hoc, and the
  paper says so.
- **Architectures.** They are fixed by a cross-validated search on the RL block's
  validation rotations: DQN `128-64`, PPO `128-64`, LinUCB `h64_e32`, Thompson Sampling
  `h128_64_e64` with a 3-component mixture (`models/arch_choice.json`). The search ran under
  cross-fit seed 0 of the same scorer design, so the choice does not depend on the drift study.
  The search itself is not part of this repository.
- **World.** The grounded stochastic simulator (`expkit/stochastic.py`, `GROUNDED`):
  - 2PL bot solves with α = 1.5;
  - human pass rates and times from Bursztein et al. (2010) and Searles et al. (2023);
  - leave-after-pass with τ = 45 s.
- **Budget.** 200 training episodes, 5 training seeds, 50 evaluation seeds (Table 4) or 20 (drift
  study). Online training runs 300 episodes with the shift from episode 100.

## 4. Code map

```text
rlcaptcha/            (repo root) core: data chunking, metrics, rewards, DQN/bandit/static policies, simulation loop
experiments/
  expkit/             library used by every experiment
    humanity_scorer.py  LSTM scorer: windows of [dx, dy, dt, v, a] + mask, temperature scaling
    crossfit.py         5-part cross-fitted scorers + the refit; loads them and checks provenance
    calibration.py      ECE, Brier, temperature scaling
    stochastic.py       grounded world: 2PL bot solves, human pass rates / times, abandonment
    simx.py             simulation loop (a verified superset of rlcaptcha.simulate)
    trainer.py, ppo.py, bandits_x.py   DQN, PPO, Neural-LinUCB and Neural Thompson Sampling
    posterior_reward.py, proxy.py      the score-only and posterior online rewards
    external.py         Balabit / web-bot cleaning rules, cache build and checksum
  partition.py        session-level split and rotation (fold 2 = the paper's)
  exp_round3_fold2.py, exp_policy_arch_search.py, preflight.py
                      fold-2 context (scorers, pools, eval-block logging), training entry
                      points and run-time gates
  protocol/common.py  shared training/evaluation plumbing (+ two modules it imports)
  paper/              one script per paper item (table above); drift_study.py is the drift driver
  models/             humanity_scorer/ (6 Keras scorers + provenance), arch_choice.json
  results/            the outputs behind the paper (see table); figures/ holds Figs. 4 and 5
```

Some module and function names keep the names of the internal experiment rounds they came from
(for example `exp_round3_fold2`). Only the code paths listed above are used for the paper.
