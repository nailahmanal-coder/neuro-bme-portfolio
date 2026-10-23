"""
Baseline motor-imagery pipeline (Project 1: EEG).

PhysioNet EEG Motor Movement/Imagery dataset (via MNE) ->
band-pass filter -> epoch -> CSP features -> LDA classifier -> cross-validated accuracy.

Runs 4, 8, 12 = imagined left-fist vs right-fist movement.
Annotations: T1 = left, T2 = right.

Setup:  pip install mne scikit-learn numpy matplotlib
Run:    python 01_motor_imagery_baseline.py
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import mne
from mne.datasets import eegbci
from mne.decoding import CSP
from mne.io import concatenate_raws, read_raw_edf
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import ShuffleSplit, cross_val_score
from sklearn.pipeline import Pipeline

SUBJECT = 1
RUNS = [4, 8, 12]
FILTER_BAND = (7.0, 30.0)  # mu (8-12 Hz) + beta (13-30 Hz) rhythms
TMIN, TMAX = -1.0, 4.0     # epoch window around cue (s)
CROP = (1.0, 2.0)          # window used for classification (s)

mne.set_log_level("WARNING")

# 1. Load data (downloads on first run)
paths = eegbci.load_data(SUBJECT, RUNS)
raw = concatenate_raws([read_raw_edf(p, preload=True) for p in paths])
eegbci.standardize(raw)
raw.set_montage(mne.channels.make_standard_montage("colin27_1005"))
fig = raw.compute_psd(fmax=60).plot(show=False)
fig.savefig("psd_before_filter.png", dpi=150)
# 2. Filter
raw.filter(*FILTER_BAND, fir_design="firwin", skip_by_annotation="edge")
fig = raw.compute_psd(fmax=60).plot(show=False)
fig.savefig("psd_after_filter.png", dpi=150)
# 3. Epoch
events, event_id = mne.events_from_annotations(raw, event_id=dict(T1=2, T2=3))
picks = mne.pick_types(raw.info, eeg=True, exclude="bads")
epochs = mne.Epochs(
    raw, events, event_id, tmin=TMIN, tmax=TMAX,
    proj=True, picks=picks, baseline=None, preload=True,
)
epochs_train = epochs.copy().crop(tmin=CROP[0], tmax=CROP[1])
labels = epochs.events[:, -1] - 2  # 0 = left, 1 = right
X = epochs_train.get_data()

# 4. CSP + LDA, cross-validated
clf = Pipeline([
    ("CSP", CSP(n_components=4, reg=None, log=True, norm_trace=False)),
    ("LDA", LinearDiscriminantAnalysis()),
])
cv = ShuffleSplit(10, test_size=0.2, random_state=42)
scores = cross_val_score(clf, X, labels, cv=cv)

chance = max(np.mean(labels == 0), np.mean(labels == 1))
print(f"Epochs: {len(labels)}  |  Channels: {X.shape[1]}")
print(f"CSP+LDA accuracy: {scores.mean():.3f} +/- {scores.std():.3f}  (chance = {chance:.2f})")
import matplotlib.pyplot as plt

plt.figure(figsize=(6, 4))
plt.bar(range(1, len(scores) + 1), scores)
plt.axhline(chance, color="red", linestyle="--", label="chance")
plt.xlabel("Train/test split")
plt.ylabel("Accuracy")
plt.legend(loc="lower right")
plt.savefig("cv_scores.png", dpi=150, bbox_inches="tight")