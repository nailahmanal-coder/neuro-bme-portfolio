"""
How fragile is the evidence?  Confidence interval vs prediction interval.

Confidence interval: where the AVERAGE effect across these trials probably is.
Prediction interval: where the effect of a NEW trial might land
(Higgins et al. 2009: pooled +/- t * sqrt(tau2 + se^2), with k-2 degrees of freedom).
Positive effect = stimulation did better than sham.
"""
import importlib
import math

from scipy import stats

meta = importlib.import_module("05_meta_analysis")
tms = importlib.import_module("06_tms_check")

DATASETS = [
    ("tDCS (MADRS, home-based)", "studies_tdcs_madrs.csv", -1),
    ("rTMS (HAMD, treatment-resistant)", "studies_tms_hamd.csv", +1),
]


def analyse(csv_file, sign):
    rows = meta.read_studies(csv_file)
    effects, ses = zip(*(tms.study_smd(r) for r in rows))
    effects = [sign * e for e in effects]
    pooled, se, tau2, q, i2, _ = meta.random_effects(effects, ses)
    k = len(rows)
    ci = (pooled - 1.96 * se, pooled + 1.96 * se)
    t_crit = stats.t.ppf(0.975, k - 2)
    half = t_crit * math.sqrt(tau2 + se**2)
    return k, pooled, ci, (pooled - half, pooled + half), tau2


if __name__ == "__main__":
    for label, path, sign in DATASETS:
        k, pooled, ci, pi, tau2 = analyse(path, sign)
        print(label)
        print(f"  {k} trials, average effect g = {pooled:.2f}")
        print(f"  95% confidence interval: [{ci[0]:5.2f}, {ci[1]:5.2f}]   width {ci[1]-ci[0]:.2f}")
        print(f"  95% prediction interval: [{pi[0]:5.2f}, {pi[1]:5.2f}]   width {pi[1]-pi[0]:.2f}")
        crosses = pi[0] < 0 < pi[1]
        print(f"  A new trial could show no benefit or harm: {'YES' if crosses else 'no'}\n")

    print("Caution: with only 4-6 trials, tau2 (the variation between trials) is very "
          "uncertain, so the prediction interval itself is uncertain too.")