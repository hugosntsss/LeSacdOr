# -*- coding: utf-8 -*-
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Ellipse, Circle
from matplotlib.path import Path
from matplotlib.patches import PathPatch
import os
here = os.path.dirname(os.path.abspath(__file__))
SPK, EIF, BOTH, MOA = "#2F6DB5", "#E8832A", "#8E5CB5", "#8A8F98"
NAVY = "#1F2A44"
# (titre, semaines, couleur_titre, [(lot, texte), ...])
RIGHT = [
 ("1 · INSTALLATION DE CHANTIER", "S1 · 02/11 → 06/11", NAVY, [
   (SPK, "Clôture, base vie commune, armoire de chantier (préalable à EIFFAGE)"),
   (EIF, "Constat d'huissier, pistes d'accès, dépose des bordures"),
   (EIF, "Percement des voiles façade Nord, puis SPK pose les grilles")]),
 ("2 · DÉVOIEMENTS ET COUPURE DE LA B2", "S1 → S2 · vidange le 09/11", NAVY, [
   (EIF, "Dévoiement incendie DN150 + AEP DN100 (S1-S2)"),
   (SPK, "Raccordements provisoires + mesures compensatoires (S1)"),
   (SPK, "Consignation + VIDANGE de la cuve B2 (09/11)")]),
 ("3 · DÉPOSES ET DÉMOLITIONS", "S2 → S4", NAVY, [
   (EIF, "Dépose brise-vue + grille (S2)"),
   (SPK, "Dépose cuve B2 (S2-S3), GMPD et réseaux local GE (S2)"),
   (EIF, "Démolition radier, étêtage, récolement (S3-S4)"),
   (EIF, "Dépose pièces de scellement locaux B2 et GE (S2-S3)")]),
 ("4 · FONDATIONS ET RADIER", "S4 → S10", NAVY, [
   (EIF, "Plateforme, pieux (S5-S6), recépage, terrassement, propreté"),
   (BOTH, "Aspiration DN300 sous radier : SPK fournit, EIFFAGE pose"),
   (EIF, "Ferraillage, COULAGE du radier 22/12, durcissement 9 j")]),
 ("5 · LOCAUX B2 ET GE", "S3 → S6", NAVY, [
   (EIF, "Pose des pièces de scellement (S3), restauration dalle GE (S5-S6)"),
   (SPK, "Pose du nouveau GMPD dans le local B2 après les scellements (S3-S4)")]),
]
LEFT = [
 ("6 · TRANCHÉES ET RÉSEAUX ENTERRÉS", "S4 → S10", NAVY, [
   (EIF, "Ouverture, fourreaux, puisard + réseau EU, grillage avertisseur"),
   (SPK, "Pose fonte DN300 / DN150 / DN200 + épreuves, tirage des câbles"),
   (EIF, "Remblaiement APRÈS les épreuves SPK (S5-S6 et S10)")]),
 ("7 · CUVE 620 m³ (SPK sur radier EIFFAGE)", "S10 → S13", NAVY, [
   (SPK, "Livraison (S8), montage (S10-S12), poche, toit, équipements"),
   (EIF, "Joint ciment périphérique de la cornière"),
   (SPK, "Remplissage ≤ 36 h + essais, remise en service B2 (S13-S14)")]),
 ("8 · BRISE-VUE (après cuve et réseaux)", "S13 → S15", NAVY, [
   (EIF, "Charpente métallique (S13)"),
   (EIF, "Sous-construction et bardage bois (S13-S15), porte d'accès")]),
 ("9 · VOIRIES ET ESPACES VERTS", "S10 → S14", NAVY, [
   (EIF, "Bordures, enrobés au droit des réseaux"),
   (EIF, "Dépose pistes, terre végétale, gazon (S14), cheminements")]),
 ("10 · FIN DE CHANTIER EIFFAGE", "S15 · 09/02 → 12/02", NAVY, [
   (EIF, "Constat d'huissier de fin de travaux"),
   (EIF, "DOE EIFFAGE, fin des travaux le 12/02/2027")]),
]

fig = plt.figure(figsize=(24, 15)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(-12, 12); ax.set_ylim(-7.9, 8.1); ax.axis("off")
ax.text(0, 7.75, "PHASAGE PHASE 1 · TRAVAUX EIFFAGE ET INTERFACES SPK", ha="center", fontsize=19, fontweight="bold", color=NAVY)

def curve(p0, p1, color):
    (x0, y0), (x1, y1) = p0, p1
    c1 = (x0 + (x1 - x0) * 0.55, y0); c2 = (x0 + (x1 - x0) * 0.45, y1)
    ax.add_patch(PathPatch(Path([p0, c1, c2, p1], [1, 4, 4, 4]), fc="none", ec=color, lw=2.6, alpha=0.55, zorder=1))

def branch(x, y, side, br):
    title, wk, col, items = br
    w = 6.6; h = 0.78
    x0 = x if side > 0 else x - w
    ax.add_patch(FancyBboxPatch((x0, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.18", fc=col, ec="none", zorder=3))
    ax.text(x0 + 0.2, y + 0.13, title, color="white", fontsize=12.2, fontweight="bold", va="center", zorder=4)
    ax.text(x0 + 0.2, y - 0.2, wk, color="#D6DAE6", fontsize=9.2, va="center", zorder=4)
    edge = (x0, y) if side > 0 else (x0 + w, y)
    curve((0, 0), edge, "#56607A")
    yy = y - h / 2 - 0.3
    for c, t in items:
        ax.add_patch(Circle((x0 + 0.22, yy), 0.095, color=c, zorder=4))
        ax.text(x0 + 0.42, yy, t, fontsize=10.2, va="center", color="#1B1B1B", zorder=4)
        yy -= 0.4

ys_r = [6.4, 3.6, 0.7, -2.3, -5.3]
ys_l = [6.3, 3.3, 0.2, -2.4, -4.7]
for y, br in zip(ys_r, RIGHT): branch(5.0, y, +1, br)
for y, br in zip(ys_l, LEFT): branch(-5.0, y, -1, br)

# centre
ax.add_patch(Ellipse((0, 0), 4.8, 2.5, fc=NAVY, ec="white", lw=3, zorder=5))
ax.text(0, 0.42, "TRAVAUX EIFFAGE · 15 SEMAINES", color="white", ha="center", fontsize=14, fontweight="bold", zorder=6)
ax.text(0, 0.0, "02/11/2026 → 12/02/2027", color="white", ha="center", fontsize=11.5, zorder=6)
ax.text(0, -0.4, "Source B2 hors service :", color="#FFD9A8", ha="center", fontsize=10.5, zorder=6)
ax.text(0, -0.68, "09/11 → 02/02 (59 j ouvrés)", color="#FFD9A8", ha="center", fontsize=10.5, fontweight="bold", zorder=6)

# légende
lx = -6.0
for c, t in [(SPK, "SPK (interventions liées à EIFFAGE)"), (EIF, "EIFFAGE (gros œuvre, VRD, CM, bardage)"), (BOTH, "Interface EIFFAGE + SPK")]:
    ax.add_patch(Circle((lx, -7.55), 0.12, color=c)); ax.text(lx + 0.25, -7.55, t, fontsize=11, va="center"); lx += 2.6 + 0.07 * len(t)
ax.text(-11.8, -7.85, "Source : tableau de limites de prestations, CCTP et DPGF des deux lots ; durées = estimations du planning EXE.", fontsize=8.5, color="#56607A")
fig.savefig(os.path.join(here, "Carte_mentale_phasage_EIFFAGE_SPK.png"), dpi=100)
fig.savefig(os.path.join(here, "Carte_mentale_phasage_EIFFAGE_SPK.pdf"))
