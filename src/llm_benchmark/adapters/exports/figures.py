"""Génération de figures comparatives pour les résultats de benchmark.

Module headless (sans Marimo) utilisant matplotlib en backend Agg.
Produit des PNG directement à partir des RunResult du domaine.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

from llm_benchmark.domain.entities import RunResult

matplotlib.use("Agg")

# Style matplotlib cohérent
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 12,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})

_COLORS = ["#2563eb", "#16a34a", "#dc2626", "#f59e0b", "#8b5cf6"]


def _short_name(model_id: str) -> str:
    """Nom court pour l'affichage des graphiques."""
    m = model_id.lower()
    if "mistral" in m and "small" in m:
        return "Mistral Small"
    if "mistral" in m:
        return "Mistral Large"
    if "claude" in m and "sonnet" in m:
        return "Claude Sonnet"
    if "claude" in m:
        return "Claude"
    if "gpt-4o-mini" in m:
        return "GPT-4o mini"
    if "gpt-4o" in m:
        return "GPT-4o"
    if "deepseek" in m:
        return "DeepSeek"
    if "gemini" in m:
        return "Gemini"
    return model_id


def generate_figures(
    run_results: list[RunResult],
    output_dir: Path,
) -> list[Path]:
    """Générer toutes les figures comparatives.

    Parameters
    ----------
    run_results : list[RunResult]
        Résultats du benchmark (un par modèle).
    output_dir : Path
        Répertoire de sortie pour les PNG.

    Returns
    -------
    list[Path]
        Chemins vers les fichiers PNG générés.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []

    paths.append(_fig_accuracy(run_results, output_dir))
    paths.append(_fig_cost_latency(run_results, output_dir))
    paths.append(_fig_heatmap(run_results, output_dir))

    print(f"  Figures  : {output_dir}/ ({len(paths)} fichiers)")
    return paths


def _fig_accuracy(results: list[RunResult], output_dir: Path) -> Path:
    """Figure 1 : précision globale et par type de question."""
    names = [_short_name(r.model_id.value) for r in results]
    display_names = [n.replace(" ", "\n") for n in names]

    global_acc = [r.summary.accuracy.value * 100 for r in results]
    open_acc = [
        r.summary.by_type.get("open", {}).get("accuracy", 0) * 100
        for r in results
    ]
    mcq_acc = [
        r.summary.by_type.get("mcq", {}).get("accuracy", 0) * 100
        for r in results
    ]

    x = np.arange(len(results))
    width = 0.25

    fig, ax = plt.subplots(figsize=(max(8, len(results) * 3), 5))
    bars_groups = [
        ax.bar(x - width, global_acc, width, label="Global", color="#2563eb"),
        ax.bar(x, open_acc, width, label="Questions ouvertes", color="#16a34a"),
        ax.bar(x + width, mcq_acc, width, label="QCM", color="#dc2626"),
    ]

    ax.set_ylabel("Taux de réponses correctes (%)")
    ax.set_title("Précision par modèle et type de question")
    ax.set_xticks(x)
    ax.set_xticklabels(display_names)
    ax.set_ylim(0, 105)
    ax.legend(loc="upper right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    for bars in bars_groups:
        for bar in bars:
            h = bar.get_height()
            ax.annotate(
                f"{h:.0f}%",
                xy=(bar.get_x() + bar.get_width() / 2, h),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center", va="bottom", fontsize=9,
            )

    fig.tight_layout()
    path = output_dir / "accuracy_comparison.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def _fig_cost_latency(results: list[RunResult], output_dir: Path) -> Path:
    """Figure 2 : coût vs latence (taille bulle = précision)."""
    fig, ax = plt.subplots(figsize=(8, 5))

    for i, r in enumerate(results):
        s = r.summary
        name = _short_name(r.model_id.value)
        cost = ((s.total_cost.amount if s.total_cost else 0) / max(s.total, 1)) * 1000
        lat = s.avg_latency.seconds if s.avg_latency else 0
        acc = s.accuracy.value * 100

        ax.scatter(
            lat, cost,
            s=acc * 5, c=_COLORS[i % len(_COLORS)],
            alpha=0.7, edgecolors="black", linewidth=0.5, zorder=3,
        )
        ax.annotate(
            f"{name}\n({acc:.0f}%)",
            (lat, cost),
            textcoords="offset points", xytext=(10, 5), fontsize=9,
        )

    ax.set_xlabel("Latence moyenne par question (s)")
    ax.set_ylabel("Coût par question (millièmes de $)")
    ax.set_title("Compromis coût / latence / précision")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    path = output_dir / "cost_latency_bubble.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def _fig_heatmap(results: list[RunResult], output_dir: Path) -> Path:
    """Figure 3 : heatmap correct/incorrect par question et modèle."""
    names = [_short_name(r.model_id.value) for r in results]
    question_ids = [qr.question_id.value for qr in results[0].results]

    matrix = np.zeros((len(results), len(question_ids)))
    for i, r in enumerate(results):
        result_map = {qr.question_id.value: qr for qr in r.results}
        for j, qid in enumerate(question_ids):
            qr = result_map.get(qid)
            if qr is None or qr.error:
                matrix[i, j] = -0.5
            elif qr.score and qr.score.is_correct:
                matrix[i, j] = 1
            else:
                matrix[i, j] = 0

    cmap = ListedColormap(["#fee2e2", "#fef9c3", "#dcfce7"])

    fig, ax = plt.subplots(
        figsize=(max(12, len(question_ids) * 0.6), max(3, len(results) * 1.2))
    )
    ax.imshow(matrix, cmap=cmap, aspect="auto", vmin=-0.5, vmax=1)

    ax.set_xticks(range(len(question_ids)))
    ax.set_xticklabels(question_ids, rotation=45, ha="right", fontsize=9)
    ax.set_yticks(range(len(results)))
    ax.set_yticklabels(names)
    ax.set_title("Réponses correctes par question et modèle")

    for i in range(len(results)):
        for j in range(len(question_ids)):
            val = matrix[i, j]
            symbol = "?" if val == -0.5 else ("V" if val == 1 else "X")
            color = "#6b7280" if val == -0.5 else ("#166534" if val == 1 else "#991b1b")
            ax.text(
                j, i, symbol,
                ha="center", va="center", fontsize=8, color=color, fontweight="bold",
            )

    fig.tight_layout()
    path = output_dir / "question_heatmap.png"
    fig.savefig(path)
    plt.close(fig)
    return path
