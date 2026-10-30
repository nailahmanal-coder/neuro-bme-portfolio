"""
Forest plot from our own meta-analysis code: one row per trial, the pooled
result as a diamond, and the 95% prediction interval as a thick bar.
Positive effect = stimulation did better than sham. Saves forest_plot.png.
"""
import importlib
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

meta = importlib.import_module("05_meta_analysis")
tms = importlib.import_module("06_tms_check")

DATASETS = [
    ("tDCS for depression (MADRS, home-based)", "studies_tdcs_madrs.csv", -1),
    ("rTMS for treatment-resistant depression (HAMD)", "studies_tms_hamd.csv", +1),
]


def prepare(csv_file, sign):
    rows = meta.read_studies(csv_file)
    names = [r["study"] for r in rows]
    effects, ses = zip(*(tms.study_smd(r) for r in rows))
    effects = [sign * e for e in effects]
    pooled, se, tau2, q, i2, weights = meta.random_effects(effects, ses)
    half = stats.t.ppf(0.975, len(rows) - 2) * math.sqrt(tau2 + se**2)
    return dict(names=names, effects=effects, ses=ses, weights=weights,
                pooled=pooled, se=se, pi=(pooled - half, pooled + half))


def draw(ax, title, d):
    n = len(d["names"])
    for i, (e, s, w) in enumerate(zip(d["effects"], d["ses"], d["weights"])):
        y = n + 2 - i
        ax.plot([e - 1.96 * s, e + 1.96 * s], [y, y], color="#1f4e79", lw=1.5)
        ax.scatter(e, y, s=w * 9, marker="s", color="#1f4e79", zorder=3)
        ax.annotate(f"{e:.2f} [{e - 1.96*s:.2f}, {e + 1.96*s:.2f}]", xy=(1.02, y),
                    xycoords=("axes fraction", "data"), va="center", fontsize=9)
    lo, hi = d["pooled"] - 1.96 * d["se"], d["pooled"] + 1.96 * d["se"]
    ax.fill([lo, d["pooled"], hi, d["pooled"]], [2, 2.3, 2, 1.7], color="#2e7d32")
    ax.annotate(f"{d['pooled']:.2f} [{lo:.2f}, {hi:.2f}]", xy=(1.02, 2),
                xycoords=("axes fraction", "data"), va="center", fontsize=9, weight="bold")
    ax.plot(d["pi"], [1, 1], color="#c62828", lw=6, alpha=0.55, solid_capstyle="butt")
    ax.annotate(f"{d['pi'][0]:.2f} to {d['pi'][1]:.2f}", xy=(1.02, 1),
                xycoords=("axes fraction", "data"), va="center", fontsize=9, color="#c62828")
    ax.axvline(0, color="grey", ls="--", lw=1)
    ax.set_yticks(list(range(n + 2, 2, -1)) + [2, 1])
    ax.set_yticklabels(d["names"] + ["Pooled (95% CI)", "95% prediction interval"])
    ax.set_ylim(0.3, n + 2.8)
    ax.set_title(title, loc="left", fontsize=11, weight="bold")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)


if __name__ == "__main__":
    data = [prepare(path, sign) for _, path, sign in DATASETS]
    lows = [min(e - 1.96 * s for e, s in zip(d["effects"], d["ses"])) for d in data]
    lows += [d["pi"][0] for d in data]
    highs = [max(e + 1.96 * s for e, s in zip(d["effects"], d["ses"])) for d in data]
    highs += [d["pi"][1] for d in data]

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True,
                             gridspec_kw={"height_ratios": [len(data[0]["names"]) + 3,
                                                            len(data[1]["names"]) + 3]})
    for ax, (title, _, _), d in zip(axes, DATASETS, data):
        draw(ax, title, d)
    axes[0].set_xlim(min(lows) - 0.2, max(highs) + 0.2)
    axes[1].set_xlabel("Effect size g   (positive = stimulation did better than sham)")
    fig.subplots_adjust(left=0.24, right=0.80, hspace=0.35)
    fig.savefig("forest_plot.png", dpi=150, bbox_inches="tight")
    print("Saved forest_plot.png")