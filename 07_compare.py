"""
Put tDCS and rTMS on the same scale and compare them.

Both are turned into a standardized effect (Hedges g) where a POSITIVE number
means active stimulation did better than sham. The tDCS file stores score
changes as negative numbers when patients improved, so its sign is flipped.
"""
import importlib
import math

meta = importlib.import_module("05_meta_analysis")
tms = importlib.import_module("06_tms_check")

DATASETS = [
    # (label, csv file, sign: -1 if a lower score means improvement)
    ("tDCS (MADRS, home-based)", "studies_tdcs_madrs.csv", -1),
    ("rTMS (HAMD, treatment-resistant)", "studies_tms_hamd.csv", +1),
]


def pool(csv_file, sign):
    rows = meta.read_studies(csv_file)
    effects, ses = zip(*(tms.study_smd(r) for r in rows))
    effects = [sign * e for e in effects]
    pooled, se, tau2, q, i2, _ = meta.random_effects(effects, ses)
    return len(rows), pooled, se, tau2, i2


if __name__ == "__main__":
    results = {}
    for label, path, sign in DATASETS:
        k, pooled, se, tau2, i2 = pool(path, sign)
        results[label] = (pooled, se)
        print(f"{label:<34} {k} trials  g = {pooled:5.2f}  "
              f"95% CI [{pooled - 1.96*se:5.2f}, {pooled + 1.96*se:5.2f}]  I2 = {i2:.0f}%")

    (g_tdcs, se_tdcs), (g_tms, se_tms) = results.values()
    diff = g_tms - g_tdcs
    se_diff = math.sqrt(se_tdcs**2 + se_tms**2)
    print(f"\nDifference (rTMS minus tDCS): {diff:.2f}  "
          f"95% CI [{diff - 1.96*se_diff:.2f}, {diff + 1.96*se_diff:.2f}]")
    print("\nCaution: different trials, patients and depression scales, and only "
          "a handful of studies each. This is a rough side-by-side, not a head-to-head trial.")