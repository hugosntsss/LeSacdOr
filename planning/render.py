# -*- coding: utf-8 -*-
# Gantt (PDF + PNG) : date a gauche de la barre, nom de la tache a droite, liaisons visibles, couleurs par lot
import sys, os, io, runpy, datetime as dt, contextlib
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle, Polygon

here = os.path.dirname(os.path.abspath(__file__))
sys.argv = ["gen.py", "/tmp/_g.xml"]
with contextlib.redirect_stdout(io.StringIO()):
    ns = runpy.run_path(os.path.join(here, "gen.py"))
order, CAL, START, byk, END, HOL, tasks = ns["order"], ns["CAL"], ns["START"], ns["byk"], ns["END"], ns["HOL"], ns["tasks"]
LOTCOL = ns["LOTCOL"]

COL = {"SPK": "#6FA8E8", "GO": "#E8832A", "VRD": "#E8832A", "MOA": "#8A8F98", "GO/SPK": "#8E5CB5", "SPK/MOA": "#25A3A0"}
NAVY = "#1B1B1B"
off = lambda i: (CAL[i] - START).days
FIN_EIF = byk["m_fin"].fd
span_days = max((CAL[END] - START).days, (CAL[FIN_EIF] - START).days) + 3
XMAX = span_days + 62
ROWS = 34
title = "DECATHLON CAMPUS - Phase 1 - Planning des travaux EIFFAGE (15 semaines) et interfaces SPK - départ %s - fin EIFFAGE %s" % (
    START.strftime("%d/%m/%Y"), CAL[FIN_EIF].strftime("%d/%m/%Y"))
pages = [order[i:i + ROWS] for i in range(0, len(order), ROWS)]

def draw(ax, page):
    n = len(page); ax.set_xlim(-6, XMAX); ax.set_ylim(n + 0.2, -2.0)
    row = {id(o): r for r, o in enumerate(page)}
    # bandes week-end / feries
    d = START - dt.timedelta(START.weekday()); wk = 0
    while (d - START).days <= span_days + 6:
        x = (d - START).days
        ax.add_patch(Rectangle((x + 5, -0.5), 2, n + 0.7, color="#E9EBF0", lw=0, zorder=0))
        ax.axvline(x, color="#B8BEC9", lw=0.7, zorder=0)
        ax.text(x + 3.5, -1.3, "S%d" % (wk + 1), ha="center", va="center", fontsize=7.6, fontweight="bold")
        ax.text(x + 3.5, -0.7, d.strftime("%d/%m"), ha="center", va="center", fontsize=6.4, color="#56607A")
        d += dt.timedelta(7); wk += 1
    for h in HOL:
        x = (h - START).days
        if 0 <= x <= span_days and h.weekday() < 5:
            ax.add_patch(Rectangle((x, -0.5), 1, n + 0.7, color="#F6D5D2", lw=0, zorder=0))
    # ligne des 15 semaines
    x15 = 15 * 7
    ax.axvline(x15, color="#C0392B", lw=1.4, ls="--", zorder=1)
    ax.text(x15 + 0.8, -1.95, "15 semaines", color="#C0392B", fontsize=7.4, fontweight="bold", va="center")
    # liaisons FS
    for t in tasks:
        if t.span or id(t) not in row: continue
        for k, ty, lag in t.links:
            p = byk[k]
            if ty != "FS" or id(p) not in row or p.key == "m_start": continue
            xe = off(p.fd) + (0.9 if p.dur == 0 else 1.0)
            xs = off(t.sd) - (0.9 if t.dur == 0 else 0.0)
            yp, ys = row[id(p)], row[id(t)]
            if xs >= xe + 0.9: pts = [(xe, yp), (xe + 0.5, yp), (xe + 0.5, ys), (xs, ys)]
            else: pts = [(xe, yp), (xe + 0.5, yp), (xe + 0.5, ys - 0.5), (xs - 0.6, ys - 0.5), (xs - 0.6, ys), (xs, ys)]
            ax.plot([a for a, b in pts], [b for a, b in pts], color="#2D5FA8", lw=0.6, zorder=3, alpha=0.6)
            ax.plot([pts[-1][0]], [pts[-1][1]], marker=">", ms=2.6, color="#2D5FA8", zorder=3)
    for r, o in enumerate(page):
        if r % 2 == 0: ax.add_patch(Rectangle((-6, r - 0.5), XMAX + 6, 1, color="#F7F8FA", lw=0, zorder=0.1))
        a, b = off(o.sd), off(o.fd) + 1
        ds = CAL[o.sd].strftime("%d/%m")
        if o.kind == "S":
            ax.add_patch(Rectangle((a, r - 0.14), b - a, 0.28, color="#3A3A3A", zorder=4))
            ax.add_patch(Polygon([(a, r + 0.14), (a + 2.0, r + 0.14), (a, r + 0.5)], color="#3A3A3A", zorder=4))
            ax.add_patch(Polygon([(b, r + 0.14), (b - 2.0, r + 0.14), (b, r + 0.5)], color="#3A3A3A", zorder=4))
            ax.text(a - 0.8, r, ds, ha="right", va="center", fontsize=7, zorder=5)
            ax.text(b + 1.2, r, o.name, ha="left", va="center", fontsize=8.6, fontweight="bold", zorder=5)
            continue
        c = COL.get(o.lot, "#999")
        name = o.name if len(o.name) <= 120 else o.name[:118] + "…"
        if o.dur == 0:
            x = a if o.key == "m_start" else b
            ax.add_patch(Polygon([(x, r - 0.4), (x + 0.9, r), (x, r + 0.4), (x - 0.9, r)], color="#C0392B" if o.key == "m_fin" else "black", zorder=5))
            ax.text(x - 1.4, r, ds, ha="right", va="center", fontsize=7, zorder=5)
            ax.text(x + 1.6, r, name, ha="left", va="center", fontsize=7.6, fontweight="bold", zorder=5)
            continue
        sp = o.span is not None
        ax.add_patch(Rectangle((a, r - (0.14 if sp else 0.3)), b - a, 0.28 if sp else 0.6, facecolor=c, hatch="////" if sp else None, alpha=0.6 if sp else 1,
                               edgecolor="#C0392B" if o.crit else "none", lw=1.2 if o.crit else 0, zorder=4))
        ax.text(a - 0.8, r, ds, ha="right", va="center", fontsize=7, zorder=5)
        ax.text(b + 1.0, r, name, ha="left", va="center", fontsize=7.6, zorder=5)
    ax.axis("off")

def figpage(page, pno, tot):
    fig = plt.figure(figsize=(16.5, 11.7))
    fig.text(0.012, 0.978, title, fontsize=10.5, fontweight="bold", va="top")
    fig.text(0.988, 0.978, "Page %d/%d" % (pno, tot), fontsize=8, ha="right", va="top", color="#56607A")
    x = 0.012
    for k, t in [("GO", "EIFFAGE (gros œuvre, VRD, CM, bardage)"), ("SPK", "SPK : intervention liée à EIFFAGE"), ("GO/SPK", "Commun EIFFAGE + SPK"), ("SPK/MOA", "Indisponibilité B2")]:
        fig.patches.append(Rectangle((x, 0.944), 0.011, 0.012, transform=fig.transFigure, color=COL[k]))
        fig.text(x + 0.014, 0.95, t, fontsize=8, va="center"); x += 0.025 + 0.0058 * len(t)
    fig.patches.append(Rectangle((x, 0.944), 0.011, 0.012, transform=fig.transFigure, facecolor="white", edgecolor="#C0392B", lw=1.2))
    fig.text(x + 0.014, 0.95, "Chemin critique (calcul du générateur)", fontsize=8, va="center")
    ax = fig.add_axes([0.01, 0.012, 0.98, 0.915]); draw(ax, page)
    return fig

for f in os.listdir(here):
    if f.startswith("Planning_EXE_15sem_Gantt") or f.startswith("Planning_EIFFAGE_15sem_Gantt"): os.remove(os.path.join(here, f))
with PdfPages(os.path.join(here, "Planning_EIFFAGE_15sem_Gantt.pdf")) as pdf:
    for i, pg in enumerate(pages):
        fig = figpage(pg, i + 1, len(pages)); pdf.savefig(fig)
        fig.savefig(os.path.join(here, "Planning_EIFFAGE_15sem_Gantt_p%d.png" % (i + 1)), dpi=110); plt.close(fig)
print(len(pages), "pages")
