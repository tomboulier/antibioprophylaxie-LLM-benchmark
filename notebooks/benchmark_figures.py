"""Marimo notebook — Figures comparatives pour l'abstract SFAR 2026.

Charge les résultats JSON du benchmark et génère des graphiques
exportables en PNG pour l'abstract et le poster.

Run with: marimo run notebooks/benchmark_figures.py
Edit with: marimo edit notebooks/benchmark_figures.py
"""

import marimo

__generated_with = "0.9.0"
app = marimo.App(width="wide")


@app.cell
def _imports():
    import json
    from pathlib import Path

    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.size": 12,
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
    })

    RESULTS_DIR = Path("research/results")
    FIGURES_DIR = Path("research/figures")
    FIGURES_DIR.mkdir(exist_ok=True)

    return FIGURES_DIR, RESULTS_DIR, json, mo, np, plt


@app.cell
def _load_all_results(RESULTS_DIR, json, mo):
    """Charge tous les fichiers de résultats JSON."""
    _result_files = sorted(RESULTS_DIR.glob("*.json"))

    all_runs = []
    for _path in _result_files:
        _data = json.loads(_path.read_text(encoding="utf-8"))
        _summary = _data.get("summary", {})
        if _summary.get("accuracy") is not None and _summary.get("correct", 0) > 0:
            all_runs.append({"path": _path, "data": _data})

    mo.md(f"**{len(all_runs)} runs valides chargés** sur {len(_result_files)} fichiers")
    return (all_runs,)


@app.cell
def _select_runs(all_runs, mo):
    """Sélectionner les runs à comparer (le plus récent par modèle par défaut)."""
    _latest_by_model = {}
    for _run in all_runs:
        _model_id = _run["data"].get("model_id", "unknown")
        _ts = _run["data"].get("timestamp", "")
        if _model_id not in _latest_by_model or _ts > _latest_by_model[_model_id]["data"]["timestamp"]:
            _latest_by_model[_model_id] = _run

    selected_runs = list(_latest_by_model.values())
    selected_runs.sort(key=lambda r: r["data"].get("model_id", ""))

    _info = "\n".join(
        f"- **{_r['data']['model_id']}** : {_r['data']['summary']['accuracy']:.0%} "
        f"({_r['data']['summary']['correct']}/{_r['data']['summary']['total']})"
        for _r in selected_runs
    )
    mo.md(f"## Runs sélectionnés (plus récent par modèle)\n\n{_info}")
    return (selected_runs,)


@app.cell
def _define_short_name():
    def short_name(model_id: str) -> str:
        """Nom court pour l'affichage des graphiques."""
        _m = model_id.lower()
        if "mistral" in _m and "small" in _m:
            return "Mistral Small"
        if "mistral" in _m:
            return "Mistral Large"
        if "claude" in _m:
            return "Claude Sonnet 4.5"
        if "gpt-4o-mini" in _m:
            return "GPT-4o mini"
        if "gpt-4o" in _m:
            return "GPT-4o"
        return model_id

    return (short_name,)


@app.cell
def _fig_accuracy_comparison(selected_runs, short_name, plt, np, FIGURES_DIR, mo):
    """Figure 1 : Comparaison de la précision globale et par type."""
    _models = [r["data"]["model_id"] for r in selected_runs]
    _names = [short_name(m).replace(" ", "\n") for m in _models]

    _global_acc = [r["data"]["summary"]["accuracy"] * 100 for r in selected_runs]
    _open_acc = [
        r["data"]["summary"]["by_type"].get("open", {}).get("accuracy", 0) * 100
        for r in selected_runs
    ]
    _mcq_acc = [
        r["data"]["summary"]["by_type"].get("mcq", {}).get("accuracy", 0) * 100
        for r in selected_runs
    ]

    _x = np.arange(len(_models))
    _width = 0.25

    fig1, _ax = plt.subplots(figsize=(max(8, len(_models) * 3), 5))
    _bars1 = _ax.bar(_x - _width, _global_acc, _width, label="Global", color="#2563eb")
    _bars2 = _ax.bar(_x, _open_acc, _width, label="Questions ouvertes", color="#16a34a")
    _bars3 = _ax.bar(_x + _width, _mcq_acc, _width, label="QCM", color="#dc2626")

    _ax.set_ylabel("Taux de réponses correctes (%)")
    _ax.set_title("Précision par modèle et type de question")
    _ax.set_xticks(_x)
    _ax.set_xticklabels(_names)
    _ax.set_ylim(0, 105)
    _ax.legend(loc="upper right")
    _ax.spines["top"].set_visible(False)
    _ax.spines["right"].set_visible(False)

    for _bars in [_bars1, _bars2, _bars3]:
        for _bar in _bars:
            _h = _bar.get_height()
            _ax.annotate(
                f"{_h:.0f}%",
                xy=(_bar.get_x() + _bar.get_width() / 2, _h),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    fig1.tight_layout()
    fig1.savefig(FIGURES_DIR / "accuracy_comparison.png")
    mo.md("### Figure 1 : Précision par modèle")
    return (fig1,)


@app.cell
def _show_fig1(fig1, mo):
    mo.as_html(fig1)
    return


@app.cell
def _fig_cost_latency(selected_runs, short_name, plt, FIGURES_DIR, mo):
    """Figure 2 : Coût vs latence (bubble = précision)."""
    _colors = ["#2563eb", "#16a34a", "#dc2626", "#f59e0b", "#8b5cf6"]

    fig2, _ax = plt.subplots(figsize=(8, 5))

    for _i, _run in enumerate(selected_runs):
        _s = _run["data"]["summary"]
        _name = short_name(_run["data"]["model_id"])
        _cost = ((_s.get("total_cost") or 0) / max(_s.get("total", 1), 1)) * 1000
        _lat = _s.get("avg_latency_s") or 0
        _acc = _s.get("accuracy", 0) * 100

        _ax.scatter(
            _lat, _cost,
            s=_acc * 5,
            c=_colors[_i % len(_colors)],
            alpha=0.7,
            edgecolors="black",
            linewidth=0.5,
            zorder=3,
        )
        _ax.annotate(
            f"{_name}\n({_acc:.0f}%)",
            (_lat, _cost),
            textcoords="offset points",
            xytext=(10, 5),
            fontsize=9,
        )

    _ax.set_xlabel("Latence moyenne par question (s)")
    _ax.set_ylabel("Coût par question (millièmes de $)")
    _ax.set_title("Compromis coût / latence / précision")
    _ax.spines["top"].set_visible(False)
    _ax.spines["right"].set_visible(False)
    _ax.grid(True, alpha=0.3)

    fig2.tight_layout()
    fig2.savefig(FIGURES_DIR / "cost_latency_bubble.png")
    mo.md("### Figure 2 : Coût vs latence")
    return (fig2,)


@app.cell
def _show_fig2(fig2, mo):
    mo.as_html(fig2)
    return


@app.cell
def _fig_question_heatmap(selected_runs, short_name, plt, np, FIGURES_DIR, mo):
    """Figure 3 : Heatmap correct/incorrect par question et modèle."""
    _models = [r["data"]["model_id"] for r in selected_runs]
    _names = [short_name(m) for m in _models]

    _question_ids = [r["question_id"] for r in selected_runs[0]["data"]["results"]]

    _matrix = np.zeros((len(_models), len(_question_ids)))
    for _i, _run in enumerate(selected_runs):
        _result_map = {r["question_id"]: r for r in _run["data"]["results"]}
        for _j, _qid in enumerate(_question_ids):
            _r = _result_map.get(_qid, {})
            if _r.get("error"):
                _matrix[_i, _j] = -0.5
            elif _r.get("is_correct"):
                _matrix[_i, _j] = 1
            else:
                _matrix[_i, _j] = 0

    from matplotlib.colors import ListedColormap

    _cmap = ListedColormap(["#fee2e2", "#fef9c3", "#dcfce7"])

    fig3, _ax = plt.subplots(
        figsize=(max(12, len(_question_ids) * 0.6), max(3, len(_models) * 1.2))
    )
    _ax.imshow(_matrix, cmap=_cmap, aspect="auto", vmin=-0.5, vmax=1)

    _ax.set_xticks(range(len(_question_ids)))
    _ax.set_xticklabels(_question_ids, rotation=45, ha="right", fontsize=9)
    _ax.set_yticks(range(len(_models)))
    _ax.set_yticklabels(_names)
    _ax.set_title("Réponses correctes par question et modèle")

    for _i in range(len(_models)):
        for _j in range(len(_question_ids)):
            _val = _matrix[_i, _j]
            _symbol = "?" if _val == -0.5 else ("V" if _val == 1 else "X")
            _color = "#6b7280" if _val == -0.5 else ("#166534" if _val == 1 else "#991b1b")
            _ax.text(
                _j, _i, _symbol,
                ha="center", va="center", fontsize=8, color=_color, fontweight="bold",
            )

    fig3.tight_layout()
    fig3.savefig(FIGURES_DIR / "question_heatmap.png")
    mo.md("### Figure 3 : Heatmap par question")
    return (fig3,)


@app.cell
def _show_fig3(fig3, mo):
    mo.as_html(fig3)
    return


@app.cell
def _export_summary(selected_runs, FIGURES_DIR, mo):
    """Résumé texte pour copier-coller dans l'abstract."""
    _lines = ["## Résumé pour l'abstract\n"]
    _lines.append("| Modèle | Précision globale | Open | QCM | Latence moy. (s) | Coût/question ($) |")
    _lines.append("|--------|:-:|:-:|:-:|:-:|:-:|")

    for _r in selected_runs:
        _s = _r["data"]["summary"]
        _name = _r["data"]["model_id"]
        _total = _s.get("total", 1)
        _cost_per_q = (_s.get("total_cost") or 0) / max(_total, 1)
        _open_acc = _s.get("by_type", {}).get("open", {}).get("accuracy", 0)
        _mcq_acc = _s.get("by_type", {}).get("mcq", {}).get("accuracy", 0)

        _lines.append(
            f"| {_name} | {_s['accuracy']:.0%} | {_open_acc:.0%} | {_mcq_acc:.0%} "
            f"| {_s.get('avg_latency_s', 0):.2f} | {_cost_per_q:.5f} |"
        )

    _lines.append(f"\nFigures exportées dans `{FIGURES_DIR}/`")
    mo.md("\n".join(_lines))
    return
