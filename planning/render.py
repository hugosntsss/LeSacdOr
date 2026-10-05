# -*- coding: utf-8 -*-
# Rendu Gantt lisible (PDF + PNG) du planning EXE : noms a cote des barres, couleurs par lot
import sys, os, io, runpy, datetime as dt, contextlib
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle, Polygon

here = os.path.dirname(os.path.abspath(__file__))
sys.argv = ["gen.py", "/tmp/_g.xml"]
with contextlib.redirect_stdout(io.StringIO()):
    ns = runpy.run_path(os.path.join(here, "gen.py"))
order, CAL, START, byk, END = ns["order"], ns["CAL"], ns["START"], ns["byk"], ns["END"]
HOL = ns["HOL"]

COL = {"SPK": "#2F6DB5", "GO": "#E8832A", "VRD": "#3FA34D", "MOA": "#8A8F98", "GO/SPK": "#8E5CB5", "SPK/MOA": "#25A3A0"}
LAB = {"SPK": "Lot Sprinklage (SPK)", "GO": "Lot Gros œuvre / CM / Bardage (GO)", "VRD": "VRD / Espaces verts", "MOA": "MOA / MOE",
       "GO/SPK": "Commun GO + SPK", "SPK/MOA": "SPK + MOA (mesures compensatoires)"}
SEC = {1: "#1F2A44", 2: "#56607A"}
off = lambda i: (CAL[i] - START).days
ROWS_PER_PAGE = 44
HDR_TXT = "DECATHLON CAMPUS - Révision majeure sprinklage - PLANNING EXE PHASE 1 (15 semaines) - départ %s, fin %s" % (START.strftime("%d/%m/%Y"), CAL[END].strftime("%d/%m/%Y"))
span_days = (CAL[END] - START).days + 2
TXT_SPACE = 62                     # jours-equivalents reserves aux libelles
XMAX = span_days + TXT_SPACE

# lignes a afficher (on garde les chapitres de niveau 1 et 2, et toutes les taches)
rows = [o for o in order]
pages = [rows[i:i + ROWS_PER_PAGE] for i in range(0, len(rows), ROWS_PER_PAGE)]

def draw(ax, page, hdr_top):
    n = len(page)
    ax.set_xlim(-3, XMAX); ax.set_ylim(n + 0.2, -1.9)
    # semaines + jours feries
    d = START
    wk = 0
    while (d - START).days <= span_days + 3:
        x = (d - START).days
        ax.axvline(x, color="#C9CED8", lw=0.5, zorder=0)
        ax.text(x + 3.5, -1.15, "S%d" % (wk + 1), ha="center", va="center", fontsize=7, fontweight="bold", color="#1F2A44")
        ax.text(x + 3.5, -0.55, d.strftime("%d/%m"), ha="center", va="center", fontsize=5.8, color="#56607A")
        d += dt.timedelta(7); wk += 1
    for h in HOL:
        x = (h - START).days
        if 0 <= x <= span_days and h.weekday() < 5:
            ax.add_patch(Rectangle((x, -0.2), 1, n + 0.4, color="#F2D7D5", lw=0, zorder=0, alpha=0.7))
    for r, o in enumerate(page):
        if r % 2 == 0: ax.add_patch(Rectangle((-3, r - 0.5), XMAX + 3, 1, color="#F6F7FA", lw=0, zorder=0))
        if o.kind == "S":
            a, b = off(o.sd), off(o.fd) + 1
            ax.add_patch(Rectangle((a, r - 0.34), b - a, 0.68, color=SEC[min(o.level, 2)], zorder=2))
            ax.add_patch(Polygon([(a, r + 0.34), (a + 1.6, r + 0.34), (a, r + 0.62)], color=SEC[min(o.level, 2)], zorder=2))
            ax.add_patch(Polygon([(b, r + 0.34), (b - 1.6, r + 0.34), (b, r + 0.62)], color=SEC[min(o.level, 2)], zorder=2))
            lab = o.name if o.level == 1 else "   " + o.name
            ax.text(b + 1.8, r, lab, ha="left", va="center", fontsize=7.4, fontweight="bold" if o.level == 1 else "normal", color="#1F2A44", zorder=3)
            continue
        c = COL.get(o.lot, "#999999")
        a, b = off(o.sd), off(o.fd) + 1
        name = o.name if len(o.name) <= 112 else o.name[:110] + "…"
        right = True
        if o.dur == 0:
            x = b if o.key != "m_start" else a
            ax.add_patch(Polygon([(x, r - 0.42), (x + 0.9, r), (x, r + 0.42), (x - 0.9, r)], color="#C0392B" if o.key == "m_fin" else "#1F2A44", zorder=4))
            ax.text(x + 1.6, r, name, ha="left", va="center", fontsize=6.6, fontweight="bold", zorder=5)
            continue
        is_span = o.span is not None
        ax.add_patch(Rectangle((a, r - (0.16 if is_span else 0.32)), b - a, 0.32 if is_span else 0.64, facecolor=c, edgecolor="#C0392B" if o.crit else "none",
                               lw=1.3 if o.crit else 0, hatch="////" if is_span else None, alpha=0.55 if is_span else 1, zorder=3))
        txt = name + ("   (%d j)" % o.dur)
        if right: ax.text(b + 0.9, r, txt, ha="left", va="center", fontsize=6.6, color="#1B1B1B", zorder=5)
        else: ax.text(a - 0.9, r, txt, ha="right", va="center", fontsize=6.6, color="#1B1B1B", zorder=5)
    ax.axis("off")

def figpage(page, pno, total):
    fig = plt.figure(figsize=(16.5, 11.7))
    fig.text(0.015, 0.975, HDR_TXT, fontsize=11.5, fontweight="bold", color="#1F2A44", va="top")
    fig.text(0.985, 0.975, "Page %d/%d" % (pno, total), fontsize=8, ha="right", va="top", color="#56607A")
    # legende
    x = 0.015
    for k in ["SPK", "GO", "VRD", "MOA", "GO/SPK", "SPK/MOA"]:
        fig.patches.append(Rectangle((x, 0.935), 0.011, 0.012, transform=fig.transFigure, color=COL[k]))
        fig.text(x + 0.014, 0.9405, LAB[k], fontsize=7.6, va="center"); x += 0.0155 + 0.0062 * len(LAB[k])
    fig.patches.append(Rectangle((x, 0.935), 0.011, 0.012, transform=fig.transFigure, facecolor="white", edgecolor="#C0392B", lw=1.3))
    fig.text(x + 0.014, 0.9405, "Chemin critique", fontsize=7.6, va="center")
    ax = fig.add_axes([0.012, 0.015, 0.976, 0.905])
    draw(ax, page, 0)
    return fig

with PdfPages(os.path.join(here, "Planning_EXE_15sem_Gantt.pdf")) as pdf:
    for i, pg in enumerate(pages):
        fig = figpage(pg, i + 1, len(pages)); pdf.savefig(fig)
        fig.savefig(os.path.join(here, "Planning_EXE_15sem_Gantt_p%d.png" % (i + 1)), dpi=110)
        plt.close(fig)
print(len(pages), "pages")
