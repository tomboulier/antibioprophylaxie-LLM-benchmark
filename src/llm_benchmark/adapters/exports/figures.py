"""Génération de figures comparatives pour les résultats de benchmark.

Module headless (sans Marimo) utilisant matplotlib en backend Agg.
Produit des PNG directement à partir des RunResult du domaine.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402 (backend avant pyplot)
import numpy as np

from llm_benchmark.domain.entities import RunResult

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

    print(f"  Figures  : {output_dir}/ ({len(paths)} fichier(s))")
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
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3)
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


