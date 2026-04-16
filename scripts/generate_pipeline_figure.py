"""Génère le schéma simplifié du pipeline de benchmark pour l'abstract."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.patches as mpatches  # noqa: E402

OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "abstract-sfar-2026"


def draw_pipeline(output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.set_xlim(0, 12)
    ax.set_ylim(-2.5, 3.5)
    ax.axis("off")

    # Couleurs
    c_data = "#4A90D9"
    c_llm = "#E67E22"
    c_score = "#27AE60"
    c_result = "#8E44AD"
    c_arrow = "#555555"
    c_example_bg = "#F5F5F5"
    c_example_border = "#CCCCCC"

    # --- Ligne du haut : boîtes compactes ---
    box_h = 1.3
    box_y = 2.0
    boxes = [
        (1.5, box_y, 2.0, box_h, c_data,
         "134 questions\nstandardisées",
         "8 spécialités"),
        (4.7, box_y, 2.0, box_h, c_llm,
         "Grands modèles\nde langage",
         "3 modèles testés"),
        (7.9, box_y, 2.0, box_h, c_score,
         "Correction\nautomatisée",
         ""),
        (10.7, box_y, 1.6, box_h, c_result,
         "Résultats",
         ""),
    ]

    for x, y, w, h, color, title, subtitle in boxes:
        box = mpatches.FancyBboxPatch(
            (x - w / 2, y - h / 2), w, h,
            boxstyle="round,pad=0.12",
            facecolor=color,
            edgecolor="white",
            linewidth=2,
            alpha=0.9,
        )
        ax.add_patch(box)

        if subtitle:
            ax.text(x, y + 0.15, title,
                    ha="center", va="center",
                    fontsize=10.5, fontweight="bold", color="white",
                    linespacing=1.2)
            ax.text(x, y - 0.35, subtitle,
                    ha="center", va="center",
                    fontsize=7.5, color="white", alpha=0.9)
        else:
            ax.text(x, y, title,
                    ha="center", va="center",
                    fontsize=10.5, fontweight="bold", color="white",
                    linespacing=1.2)

    # Flèches entre les boîtes
    arrow_props = dict(
        arrowstyle="->,head_width=0.25,head_length=0.15",
        color=c_arrow, lw=2,
    )
    for x_start, x_end in [(2.55, 3.65), (5.75, 6.85), (8.95, 9.85)]:
        ax.annotate("", xy=(x_end, box_y), xytext=(x_start, box_y),
                     arrowprops=arrow_props)

    # Titre
    ax.text(6, 3.3, "Méthode d'évaluation", ha="center", va="center",
            fontsize=14, fontweight="bold", color="#333333")

    # --- Ligne du bas : exemples de questions ---
    ex_y = -0.6
    ex_h = 2.0
    ex_w = 5.2

    # Exemple question ouverte
    ex1_x = 3.0
    box_ex1 = mpatches.FancyBboxPatch(
        (ex1_x - ex_w / 2, ex_y - ex_h / 2), ex_w, ex_h,
        boxstyle="round,pad=0.15",
        facecolor=c_example_bg,
        edgecolor=c_example_border,
        linewidth=1.5,
    )
    ax.add_patch(box_ex1)

    ax.text(ex1_x, ex_y + 0.7, "Exemple : question ouverte",
            ha="center", va="center",
            fontsize=8.5, fontweight="bold", color="#555555")
    ax.text(ex1_x, ex_y + 0.2,
            "Quelle est la recommandation d'antibioprophylaxie\n"
            "pour une prothèse totale de hanche ?",
            ha="center", va="center",
            fontsize=8, color="#333333", style="italic", linespacing=1.4)
    ax.text(ex1_x, ex_y - 0.5, "Réponse attendue : Céfazoline",
            ha="center", va="center",
            fontsize=8, fontweight="bold", color=c_score)

    # Exemple QCM
    ex2_x = 9.0
    box_ex2 = mpatches.FancyBboxPatch(
        (ex2_x - ex_w / 2, ex_y - ex_h / 2), ex_w, ex_h,
        boxstyle="round,pad=0.15",
        facecolor=c_example_bg,
        edgecolor=c_example_border,
        linewidth=1.5,
    )
    ax.add_patch(box_ex2)

    ax.text(ex2_x, ex_y + 0.7, "Exemple : QCM",
            ha="center", va="center",
            fontsize=8.5, fontweight="bold", color="#555555")
    ax.text(ex2_x, ex_y + 0.2,
            "Quelle molécule en première intention pour\n"
            "l'antibioprophylaxie d'une prothèse totale de genou ?",
            ha="center", va="center",
            fontsize=8, color="#333333", style="italic", linespacing=1.4)
    ax.text(ex2_x, ex_y - 0.35,
            "A) Amoxicilline/Clavulanate    B) Céfazoline\n"
            "C) Clindamycine                     D) Vancomycine",
            ha="center", va="center",
            fontsize=7, color="#666666", family="monospace", linespacing=1.5)
    ax.text(ex2_x, ex_y - 0.75, "Réponse attendue : B",
            ha="center", va="center",
            fontsize=8, fontweight="bold", color=c_score)

    # Flèche de la 1re boîte vers les exemples
    ax.annotate("", xy=(4.5, ex_y + ex_h / 2),
                xytext=(1.5, box_y - box_h / 2),
                arrowprops=dict(
                    arrowstyle="->,head_width=0.2,head_length=0.12",
                    color=c_data, lw=1.5, linestyle="--",
                    connectionstyle="arc3,rad=0.15",
                ))

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=200, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    print(f"Figure générée : {output_path}")


if __name__ == "__main__":
    draw_pipeline(OUTPUT_DIR / "pipeline_benchmark.png")
