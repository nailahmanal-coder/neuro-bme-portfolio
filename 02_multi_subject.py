import numpy as np
import mne
from mne.datasets import eegbci
from mne.decoding import CSP
from mne.io import concatenate_raws, read_raw_edf
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import ShuffleSplit, cross_val_score
from sklearn.pipeline import Pipeline

mne.set_log_level("WARNING")

RUNS = [4, 8, 12]


def run_subject(subject):
    """Run the full pipeline for one person. Returns mean and spread of accuracy."""
    paths = eegbci.load_data(subject, RUNS)
    raw = concatenate_raws([read_raw_edf(p, preload=True) for p in paths])
    eegbci.standardize(raw)
    raw.set_montage(mne.channels.make_standard_montage("colin27_1005"))
    raw.filter(7.0, 30.0, fir_design="firwin", skip_by_annotation="edge")

    events, event_id = mne.events_from_annotations(raw, event_id=dict(T1=2, T2=3))
    picks = mne.pick_types(raw.info, eeg=True, exclude="bads")
    epochs = mne.Epochs(
        raw, events, event_id, tmin=-1.0, tmax=4.0,
        proj=True, picks=picks, baseline=None, preload=True,
    )
    X = epochs.copy().crop(tmin=1.0, tmax=2.0).get_data()
    labels = epochs.events[:, -1] - 2

    clf = Pipeline([
        ("CSP", CSP(n_components=4, reg=None, log=True, norm_trace=False)),
        ("LDA", LinearDiscriminantAnalysis()),
    ])
    cv = ShuffleSplit(10, test_size=0.2, random_state=42)
    scores = cross_val_score(clf, X, labels, cv=cv)
    return scores.mean(), scores.std()


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    subjects = list(range(1, 11))
    means = []
    for s in subjects:
        mean, std = run_subject(s)
        means.append(mean)
        print(f"Subject {s}: {mean:.3f} +/- {std:.3f}")

    print(f"\nAverage across subjects: {np.mean(means):.3f}")

    plt.figure(figsize=(7, 4))
    plt.bar(subjects, means)
    plt.axhline(0.5, color="red", linestyle="--", label="chance")
    plt.xlabel("Subject")
    plt.ylabel("Mean accuracy")
    plt.xticks(subjects)
    plt.legend(loc="lower right")
    plt.savefig("subjects.png", dpi=150, bbox_inches="tight")