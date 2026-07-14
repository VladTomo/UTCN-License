import warnings
warnings.filterwarnings('ignore')

import matplotlib
matplotlib.use('Agg')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier

DATASET      = 'diet_recommendations_dataset.csv'
TEST_SIZE    = 0.20
RANDOM_STATE = 42
CV_FOLDS     = 5

FEATURE_NAMES = ['Age', 'Gender', 'Weight (kg)', 'Height (cm)', 'BMI',
                 'Disease Type', 'Severity', 'Activity Level',
                 'Cholesterol', 'Blood Pressure', 'Glucose',
                 'Weekly Exercise Hrs']

MODELS = {
    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
    'Decision Tree':       DecisionTreeClassifier(random_state=RANDOM_STATE),
    'Random Forest':       RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE),
    'K-Nearest Neighbors': KNeighborsClassifier(n_neighbors=7),
    'Gradient Boosting':   GradientBoostingClassifier(n_estimators=100, random_state=RANDOM_STATE),
}

SHORT_NAMES = ['Log. Reg.', 'Dec. Tree', 'Rand. Forest', 'KNN', 'Grad. Boost.']

BG      = '#ffffff'
CARD    = '#ffffff'
TEXT    = '#000000'
DIM     = '#000000'
GRID    = '#000000'
PALETTE = ['#06b6d4', '#38bdf8', '#0ea5e9', '#7dd3fc', '#0284c7']


# ── Data ─────────────────────────────────────────────────────────────────────

def load_and_preprocess(filepath: str):
    df = pd.read_csv(filepath)

    # Disease_Type has 204 NaN rows (healthy patients) — fill before encoding
    df['Disease_Type'] = df['Disease_Type'].fillna('None')

    categorical_cols = ['Gender', 'Disease_Type', 'Severity', 'Physical_Activity_Level']
    encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le

    le_target = LabelEncoder()
    y = le_target.fit_transform(df['Diet_Recommendation'].astype(str))
    encoders['Diet_Recommendation'] = le_target

    feature_cols = ['Age', 'Gender', 'Weight_kg', 'Height_cm', 'BMI',
                    'Disease_Type', 'Severity', 'Physical_Activity_Level',
                    'Cholesterol_mg/dL', 'Blood_Pressure_mmHg',
                    'Glucose_mg/dL', 'Weekly_Exercise_Hours']
    X = df[feature_cols].values
    return X, y, le_target.classes_, encoders


# ── Evaluation ───────────────────────────────────────────────────────────────

def evaluate_models(X_train, X_test, y_train, y_test):
    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    results = {}

    for name, model in MODELS.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='f1_weighted')

        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(X_test)
            avg_conf = float(proba.max(axis=1).mean())
        else:
            avg_conf = None

        results[name] = {
            'model':       model,
            'y_pred':      y_pred,
            'accuracy':    accuracy_score(y_test, y_pred),
            'f1':          f1_score(y_test, y_pred, average='weighted'),
            'precision':   precision_score(y_test, y_pred, average='weighted', zero_division=0),
            'recall':      recall_score(y_test, y_pred, average='weighted', zero_division=0),
            'cv_mean':     cv_scores.mean(),
            'cv_std':      cv_scores.std(),
            'cm':          confusion_matrix(y_test, y_pred),
            'avg_conf':    avg_conf,
        }

    return results


def _get_importances(model):
    """Return normalized feature importances, or None for models that lack them."""
    if hasattr(model, 'feature_importances_'):
        imp = model.feature_importances_
    elif hasattr(model, 'coef_'):
        imp = np.abs(model.coef_).mean(axis=0)
    else:
        return None
    total = imp.sum()
    return imp / total if total > 0 else imp


# ── Plots ─────────────────────────────────────────────────────────────────────

def _style_ax(ax, title):
    ax.set_facecolor(CARD)
    ax.set_title(title, color=TEXT, fontsize=12, fontweight='bold', pad=10)
    ax.spines[:].set_visible(False)
    ax.yaxis.grid(True, color=GRID, alpha=0.6, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.yaxis.set_tick_params(labelcolor=DIM, labelsize=9)
    ax.xaxis.set_tick_params(labelcolor=DIM, labelsize=8)


def plot_comparison(results: dict, class_names, out_file='diet_benchmark.png'):
    model_names = list(results.keys())
    metric_specs = [
        ('Accuracy',           'accuracy'),
        ('Precision',          'precision'),
        ('Recall',             'recall'),
        ('F1 Score',           'f1'),
        (f'{CV_FOLDS}-Fold CV F1', 'cv'),
    ]

    fig = plt.figure(figsize=(24, 14), facecolor=BG)
    gs = GridSpec(2, 5, figure=fig, hspace=0.55, wspace=0.38,
                  top=0.91, bottom=0.06, left=0.04, right=0.98)
    fig.suptitle('Diet Recommendation — Model Comparison', color=TEXT,
                 fontsize=19, fontweight='bold')

    for col, (title, key) in enumerate(metric_specs):
        ax = fig.add_subplot(gs[0, col])
        _style_ax(ax, title)

        if key == 'cv':
            values = [results[m]['cv_mean'] for m in model_names]
            errors = [results[m]['cv_std']  for m in model_names]
            bars = ax.bar(range(len(model_names)), values, color=PALETTE,
                          edgecolor='none', width=0.6, yerr=errors, capsize=5,
                          error_kw={'color': TEXT, 'linewidth': 1.4, 'capthick': 1.4})
        else:
            values = [results[m][key] for m in model_names]
            bars = ax.bar(range(len(model_names)), values, color=PALETTE,
                          edgecolor='none', width=0.6)

        ax.set_xticks(range(len(SHORT_NAMES)))
        ax.set_xticklabels(SHORT_NAMES, rotation=40, ha='right')
        ax.set_ylim(0, 1.15)
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, val + 0.03,
                    f'{val:.3f}', ha='center', va='bottom',
                    color=TEXT, fontsize=8, fontweight='bold')

    for col, (name, res) in enumerate(results.items()):
        ax = fig.add_subplot(gs[1, col])
        ax.set_facecolor(CARD)
        cm      = res['cm']
        cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)
        ax.imshow(cm_norm, cmap='Blues', vmin=0, vmax=1, aspect='auto')
        ax.set_xticks(range(len(class_names)))
        ax.set_yticks(range(len(class_names)))
        ax.set_xticklabels(class_names, rotation=40, ha='right', color=DIM, fontsize=8)
        ax.set_yticklabels(class_names, color=DIM, fontsize=8)
        ax.set_title(SHORT_NAMES[col], color=TEXT, fontsize=11, fontweight='bold', pad=8)
        ax.set_xlabel('Predicted', color=DIM, fontsize=9)
        ax.set_ylabel('Actual',    color=DIM, fontsize=9)
        ax.spines[:].set_color(GRID)
        for r in range(cm.shape[0]):
            for c in range(cm.shape[1]):
                txt_col = BG if cm_norm[r, c] > 0.5 else TEXT
                ax.text(c, r, str(cm[r, c]), ha='center', va='center',
                        color=txt_col, fontsize=11, fontweight='bold')

    plt.savefig(out_file, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close(fig)
    print(f"  Chart saved -> {out_file}")


def plot_feature_importance(results: dict, feature_names, out_file='diet_feature_importance.png'):
    fig, axes = plt.subplots(1, 5, figsize=(24, 7), facecolor=BG)
    fig.suptitle('Diet Recommendation — Feature Importance per Model', color=TEXT,
                 fontsize=18, fontweight='bold')
    fig.subplots_adjust(top=0.88, bottom=0.08, left=0.05, right=0.97, wspace=0.45)

    for ax, (name, res), color, short in zip(axes, results.items(), PALETTE, SHORT_NAMES):
        ax.set_facecolor(CARD)
        ax.set_title(short, color=TEXT, fontsize=12, fontweight='bold', pad=10)
        ax.spines[:].set_visible(False)

        importances = _get_importances(res['model'])

        if importances is None:
            ax.text(0.5, 0.5, 'Not\nApplicable\n(KNN)', ha='center', va='center',
                    color=DIM, fontsize=13, transform=ax.transAxes)
            ax.set_xticks([])
            ax.set_yticks([])
            continue

        idx = np.argsort(importances)
        bars = ax.barh(range(len(feature_names)), importances[idx],
                       color=color, edgecolor='none', height=0.6)
        ax.set_yticks(range(len(feature_names)))
        ax.set_yticklabels([feature_names[i] for i in idx], color=DIM, fontsize=9)
        ax.xaxis.grid(True, color=GRID, alpha=0.6, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.xaxis.set_tick_params(labelcolor=DIM, labelsize=8)

        for bar, val in zip(bars, importances[idx]):
            ax.text(val + 0.005, bar.get_y() + bar.get_height() / 2,
                    f'{val:.3f}', va='center', color=TEXT, fontsize=8)

    plt.savefig(out_file, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close(fig)
    print(f"  Chart saved -> {out_file}")


# ── Console summary ───────────────────────────────────────────────────────────

def print_summary(results: dict):
    best = max(results, key=lambda m: results[m]['f1'])
    header = (f"\n{'Model':<22} {'Accuracy':>9} {'Precision':>10} {'Recall':>8}"
              f" {'F1':>8} {'Avg Conf':>9}  {'CV F1 (mean+/-std)':>20}")
    sep = "=" * len(header)
    print(f"\n{sep}\n{header}\n{sep}")
    for name, res in results.items():
        conf_str = f"{res['avg_conf']:>8.3f}" if res['avg_conf'] is not None else "     N/A"
        marker = "  << best" if name == best else ""
        print(
            f"{name:<22} {res['accuracy']:>9.3f} {res['precision']:>10.3f}"
            f" {res['recall']:>8.3f} {res['f1']:>8.3f} {conf_str}  "
            f"{res['cv_mean']:>6.3f} +/- {res['cv_std']:.3f}{marker}"
        )
    print(sep)
    print(f"\n  Winner: {best}  (weighted F1 = {results[best]['f1']:.3f})\n")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    print(f"Loading '{DATASET}'...")
    X, y, class_names, encoders = load_and_preprocess(DATASET)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    print(f"Samples -- total: {len(X)} | train: {len(X_train)} | test: {len(X_test)}")
    print(f"Classes: {list(class_names)}")
    print(f"\nTraining & evaluating ({CV_FOLDS}-fold CV on training set)...\n")

    results = evaluate_models(X_train, X_test, y_train, y_test)

    print_summary(results)

    print("Generating charts...")
    plot_comparison(results, class_names)
    plot_feature_importance(results, FEATURE_NAMES)
    print("\nDone.")


if __name__ == '__main__':
    main()