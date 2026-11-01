"""
Interactive dashboard: how fragile is the evidence for TMS and tDCS in depression?
Tick trials on and off in the sidebar and watch the pooled result, the confidence
interval and the prediction interval change.

Run with:  streamlit run 10_dashboard.py
"""
import importlib
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import streamlit as st
from scipy import stats

meta = importlib.import_module("05_meta_analysis")
tms = importlib.import_module("06_tms_check")
forest = importlib.import_module("09_forest_plot")

# label -> (csv file, sign: -1 if a lower score means improvement, plot title)
TREATMENTS = {
    "tDCS (home-based, MADRS)": ("studies_tdcs_madrs.csv", -1, "tDCS for depression (MADRS)"),
    "rTMS (treatment-resistant, HAMD)": ("studies_tms_hamd.csv", +1, "rTMS for treatment-resistant depression (HAMD)"),
}

st.set_page_config(page_title="TMS vs tDCS evidence", layout="wide")
st.title("How fragile is the evidence for brain stimulation in depression?")
st.caption("Random-effects meta-analysis written from scratch. Effect size g: positive means "
           "stimulation did better than sham. Data are copied from two published meta-analyses.")

choice = st.sidebar.radio("Treatment", list(TREATMENTS))
csv_file, sign, title = TREATMENTS[choice]
all_rows = meta.read_studies(csv_file)

st.sidebar.markdown("**Include these trials**")
rows = [r for r in all_rows if st.sidebar.checkbox(r["study"], value=True, key=f"{choice}-{r['study']}")]

if len(rows) < 3:
    st.warning("Select at least 3 trials. A prediction interval needs 3 or more.")
    st.stop()

effects, ses = zip(*(tms.study_smd(r) for r in rows))
effects = [sign * e for e in effects]
pooled, se, tau2, q, i2, weights = meta.random_effects(effects, ses)
ci = (pooled - 1.96 * se, pooled + 1.96 * se)
half = stats.t.ppf(0.975, len(rows) - 2) * math.sqrt(tau2 + se**2)
pi = (pooled - half, pooled + half)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Average effect (g)", f"{pooled:.2f}")
c2.metric("95% confidence interval", f"{ci[0]:.2f} to {ci[1]:.2f}")
c3.metric("95% prediction interval", f"{pi[0]:.2f} to {pi[1]:.2f}")
c4.metric("Inconsistency (I\u00b2)", f"{i2:.0f}%")

if pi[0] < 0 < pi[1]:
    st.warning("The prediction interval crosses zero: a new trial could show no benefit, or even harm.")
else:
    st.info("The prediction interval stays above zero. With so few trials this is a minimum "
            "amount of uncertainty, not a guarantee.")

d = dict(names=[r["study"] for r in rows], effects=effects, ses=ses, weights=weights,
         pooled=pooled, se=se, pi=pi)
fig, ax = plt.subplots(figsize=(9, 0.55 * len(rows) + 2.2))
forest.draw(ax, title, d)
lo_x = min(min(e - 1.96 * s for e, s in zip(effects, ses)), pi[0]) - 0.2
hi_x = max(max(e + 1.96 * s for e, s in zip(effects, ses)), pi[1]) + 0.2
ax.set_xlim(lo_x, hi_x)
ax.set_xlabel("Effect size g   (positive = stimulation did better than sham)")
fig.subplots_adjust(left=0.25, right=0.78, bottom=0.15)
st.pyplot(fig)
plt.close(fig)

st.dataframe([{"Trial": r["study"], "Active (N)": int(r["n_active"]), "Sham (N)": int(r["n_sham"]),
               "g": round(e, 2), "95% CI": f"{e - 1.96*s:.2f} to {e + 1.96*s:.2f}",
               "Weight (%)": round(w, 1)}
              for r, e, s, w in zip(rows, effects, ses, weights)], hide_index=True)

st.caption("Caution: very few trials, different scales and populations, and only the variation "
           "between included trials is captured. Not a head-to-head comparison. Not medical advice.")