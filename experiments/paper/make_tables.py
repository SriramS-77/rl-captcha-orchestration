"""Rebuild Tables 3-6 of the paper from the CSVs in results/ (no training, no evaluation).

Each table reads only the files listed in experiments/README.md; rerunning an experiment
overwrites its CSVs, and this script then prints the reproduced table.

    python paper/make_tables.py            # all tables
    python paper/make_tables.py 4 6        # some of them
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

RES = Path(os.environ.get("RESULTS_OUT", Path(__file__).resolve().parent.parent / "results"))
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)


def seed_means(df, cols=("DI", "friction_s")):
    return df.groupby("train_seed")[list(cols)].mean()


def ci95(x):
    """Half-width of the 95 % t-interval over training seeds."""
    x = np.asarray(x, float)
    return stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x)) if len(x) > 1 else np.nan


def mean_sd(df):
    s = seed_means(df)
    sd = f" ± {s.DI.std(ddof=1):.1f}" if len(s) > 1 else ""
    return f"{s.DI.mean():.2f}{sd} ({s.friction_s.mean():.1f})"


# --------------------------------------------------------------------------- #

def table3():
    d = pd.read_csv(RES / "webbot" / "webbot_summary.csv")
    d = d[d.model == "fine-tuned"]
    cols = ["dataset", "level", "accuracy_mean", "bot_precision_mean", "bot_recall_mean", "bot_f1_mean",
            "human_precision_mean", "human_recall_mean", "human_f1_mean", "auc_mean", "accuracy_std"]
    print("TABLE 3  web bot benchmark, fine-tuned scorer (mean over 5 seeds)")
    print(d[cols].round(3).to_string(index=False))


def table4():
    runs = pd.concat([
        pd.read_csv(RES / "headline_runs.csv"),
        pd.read_csv(RES / "ts_variants_runs.csv").query("policy != 'TS mog3'"),   # MoG3 = headline TS
        pd.read_csv(RES / "headline" / "np_threshold_a0.10.csv"),
        pd.read_csv(RES / "headline" / "np_multi_threshold_a0.10.csv"),
    ], ignore_index=True)
    runs = runs[runs.n_bots > 0]
    rows = []
    for pol, r in runs.groupby("policy", sort=False):
        f, v = r[r.grid == "fixed"], r[r.grid == "varying"]
        fs, vs = f.groupby("train_seed").DI.mean(), v.groupby("train_seed").DI.mean()
        row = {"policy": pol}
        row.update({int(k): x for k, x in f.groupby("level").DI.mean().items()})
        row.update({"DI": fs.mean(), "CI95": ci95(fs), "worst seed": fs.min() if len(fs) > 1 else np.nan,
                    "BOS": f.BOS.mean(), "SP-F1": f.SP_F1.mean(), "SI-F1": f.SI_F1.mean(),
                    "humans kept": f.human_survival.mean(), "friction s": f.friction_s.mean(),
                    "varying DI": vs.mean(), "varying CI95": ci95(vs)})
        rows.append(row)
    t = pd.DataFrame(rows).set_index("policy").sort_values("DI", ascending=False)
    print("TABLE 4  held-out evaluation (fixed: 100 humans x 20-1000 bots; varying: 50-250 humans, "
          "5-75 % bots); 50 eval seeds; CI95 over 5 training seeds")
    print(t.round(3).to_string())


def table5():
    ps = pd.read_csv(RES / "drift" / "drift_per_seed.csv")
    au = pd.concat([pd.read_csv(f) for f in sorted((RES / "np_audit").glob("*__ppo__*.csv"))],
                   ignore_index=True)
    au = au[au.bots > 0]
    cells = [("bots", 0.5), ("bots", 1.0), ("humans", 0.5), ("humans", 1.0)]
    rows = {}
    for label, pol in (("Label-based (all)", "PPO oracle"), ("Score-only", "PPO score-only"),
                       ("Posterior (EM share)", "PPO posterior")):
        # drift_per_seed.csv already holds per-seed means; the no-shift cell is the control at rho 0
        p = ps
        rows[label] = [mean_sd(p[(p.panel == "control") & (p.policy == pol) & (p.eval_rho == 0)
                                 & (p.eval_direction == "bots")])] + \
                      [mean_sd(p[(p.panel == "online") & (p.policy == pol) & (p.eval_direction == d)
                                 & (p.eval_rho == r)]) for d, r in cells]
    for label, arm in (("Audit recal., 2% labels", "audit_recal"),
                       ("Audit recal., level-9 challenge", "audit_ch")):
        a = au[au.arm == arm]
        rows[label] = [mean_sd(a[(a.panel == "control") & (a.eval_direction == "none")])] + \
                      [mean_sd(a[(a.panel == "online") & (a.eval_direction == d) & (a.eval_rho == r)])
                       for d, r in cells]
    statics = pd.concat([pd.read_csv(RES / "single_table5.csv"), pd.read_csv(RES / "multi_table5.csv")])
    statics = statics[statics.bots > 0]
    for pol, s in statics.groupby("policy"):
        rows[pol] = [f"{s[(s.eval_direction == d) & (s.eval_rho == r)].DI.mean():.2f} "
                     f"({s[(s.eval_direction == d) & (s.eval_rho == r)].friction_s.mean():.1f})"
                     for d, r in [("none", 0.0)] + cells]
    npm = pd.read_csv(RES / "np_multi_equal.csv")
    for pol in ("NP threshold", "NP multi-threshold"):
        s = npm[npm.policy == pol]
        rows[f"Static {pol}"] = [f"{s[(s.eval_direction == d) & (s.eval_rho == r)].DI.iloc[0]:.2f} "
                                 f"({s[(s.eval_direction == d) & (s.eval_rho == r)].fr.iloc[0]:.1f})"
                                 for d, r in [("none", 0.0)] + cells]
    t = pd.DataFrame(rows, index=["no shift", "covert bots 0.5", "covert bots 1",
                                  "bot-like humans 0.5", "bot-like humans 1"]).T
    print("TABLE 5  PPO trained online through the shift; DI mean ± SD over 5 seeds (friction s)")
    print(t.to_string())


def table6():
    g = pd.read_csv(RES / "gated_runs.csv")
    g = g[g.bots > 0]
    rows = {}
    for label, arm in (("Always frozen", "frozen"), ("Always online (score-only)", "online"),
                       ("Gated, mid-band CUSUM", "gated_mid"), ("Gated, KS CUSUM", "gated_ks"),
                       ("Ungated audit baseline", "online_audit")):
        a = g[g.arm == arm]
        row = [mean_sd(a[(a.train_rho == 0) & (a.eval_direction == "none")])]
        row += [mean_sd(a[(a.train_rho == r) & (a.eval_direction == "bots") & (a.eval_rho == r)])
                for r in (0.5, 1.0)]
        delays = []
        for r in (0.5, 1.0):
            al = a[a.train_rho == r].groupby("train_seed").alarm_ep.first() - 250   # attack at ep 250
            delays.append("---" if al.isna().all() else
                          f"{al.fillna(al.max()).median():.0f} (missed {int(al.isna().sum())})")
        rows[label] = row + [" / ".join(delays)]
    t = pd.DataFrame(rows, index=["no drift", "covert bots 0.5", "covert bots 1",
                                  "detection delay 0.5 / 1"]).T
    print("TABLE 6  gated online training; DI mean ± SD over 5 seeds (friction s)")
    print(t.to_string())


if __name__ == "__main__":
    want = sys.argv[1:] or ["3", "4", "5", "6"]
    for k in want:
        globals()[f"table{k}"]()
        print()
