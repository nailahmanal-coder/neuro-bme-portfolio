"""
Same check as 05, for the rTMS data: standardized mean difference (Hedges g),
pooled with the random-effects code from 05_meta_analysis.py, compared with
Liu et al. 2014, BMC Psychiatry, Fig 5 (change in HAMD scores, rTMS vs sham).
"""
import importlib
import math

meta = importlib.import_module("05_meta_analysis")

PAPER = {"pooled": 0.86, "low": 0.57, "high": 1.15}


def study_smd(row):
    """Hedges g (standardized mean difference) and its standard error."""
    n1, m1, s1 = int(row["n_active"]), float(row["mean_active"]), float(row["sd_active"])
    n2, m2, s2 = int(row["n_sham"]), float(row["mean_sham"]), float(row["sd_sham"])
    df = n1 + n2 - 2
    pooled_sd = math.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / df)
    g = (m1 - m2) / pooled_sd * (1 - 3 / (4 * df - 1))
    se = math.sqrt((n1 + n2) / (n1 * n2) + g**2 / (2 * df))
    return g, se


if __name__ == "__main__":
    rows = meta.read_studies("studies_tms_hamd.csv")
    effects, ses = zip(*(study_smd(r) for r in rows))
    pooled, se, tau2, q, i2, weights = meta.random_effects(effects, ses)
    low, high = pooled - 1.96 * se, pooled + 1.96 * se

    for r, e, s, w in zip(rows, effects, ses, weights):
        print(f"{r['study']:<18} g {e:5.2f}  95% CI [{e - 1.96*s:5.2f}, {e + 1.96*s:5.2f}]  weight {w:5.1f}%")
    print(f"\nPooled: {pooled:.2f}  95% CI [{low:.2f}, {high:.2f}]")
    print(f"tau2 = {tau2:.2f}   Q = {q:.2f}   I2 = {i2:.1f}%   z = {pooled / se:.2f}")

    ok = all(abs(a - b) < 0.015 for a, b in
             [(pooled, PAPER["pooled"]), (low, PAPER["low"]), (high, PAPER["high"])])
    print(f"\nPaper reports {PAPER['pooled']} [{PAPER['low']}, {PAPER['high']}]  ->  "
          f"{'MATCH' if ok else 'DIFFERENT'}")