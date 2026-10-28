"""
Random-effects meta-analysis from scratch (DerSimonian-Laird).
Reads studies_tdcs_madrs.csv, pools the mean differences, and checks the
result against the published paper (Moshfeghinia 2025, Sci Rep, Fig 3).
"""
import csv
import math

PAPER = {"pooled": -2.74, "low": -4.19, "high": -1.29}   # what the paper reports


def read_studies(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def study_effect(row):
    """Mean difference (active minus sham) and its standard error."""
    n1, m1, s1 = int(row["n_active"]), float(row["mean_active"]), float(row["sd_active"])
    n2, m2, s2 = int(row["n_sham"]), float(row["mean_sham"]), float(row["sd_sham"])
    diff = m1 - m2
    pooled_sd = math.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2))
    se = pooled_sd * math.sqrt(1 / n1 + 1 / n2)
    return diff, se


def random_effects(effects, ses):
    k = len(effects)
    w = [1 / se**2 for se in ses]                       # fixed-effect weights
    fixed = sum(wi * e for wi, e in zip(w, effects)) / sum(w)
    q = sum(wi * (e - fixed) ** 2 for wi, e in zip(w, effects))
    c = sum(w) - sum(wi**2 for wi in w) / sum(w)
    tau2 = max(0.0, (q - (k - 1)) / c)                  # between-study variance
    w_re = [1 / (se**2 + tau2) for se in ses]
    pooled = sum(wi * e for wi, e in zip(w_re, effects)) / sum(w_re)
    se_pooled = math.sqrt(1 / sum(w_re))
    i2 = max(0.0, (q - (k - 1)) / q) * 100 if q > 0 else 0.0
    return pooled, se_pooled, tau2, q, i2, [wi / sum(w_re) * 100 for wi in w_re]


if __name__ == "__main__":
    rows = read_studies("studies_tdcs_madrs.csv")
    effects, ses = zip(*(study_effect(r) for r in rows))
    pooled, se, tau2, q, i2, weights = random_effects(effects, ses)
    low, high = pooled - 1.96 * se, pooled + 1.96 * se

    for r, e, s, w in zip(rows, effects, ses, weights):
        print(f"{r['study']:<14} diff {e:6.2f}  95% CI [{e - 1.96*s:6.2f}, {e + 1.96*s:6.2f}]  weight {w:5.2f}%")
    print(f"\nPooled: {pooled:.2f}  95% CI [{low:.2f}, {high:.2f}]")
    print(f"tau2 = {tau2:.2f}   Q = {q:.2f}   I2 = {i2:.1f}%   z = {pooled / se:.2f}")

    ok = all(abs(a - b) < 0.015 for a, b in
             [(pooled, PAPER["pooled"]), (low, PAPER["low"]), (high, PAPER["high"])])
    print(f"\nPaper reports {PAPER['pooled']} [{PAPER['low']}, {PAPER['high']}]  ->  "
          f"{'MATCH' if ok else 'DIFFERENT'}")