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
 ("1 · INSTALLATION DE CHANTIER", "S1 · 02/11 → 04/11", NAVY, [
   (SPK, "Clôture, base vie (25 pers.), armoire de chantier, bâchage"),
   (EIF, "Pistes d'accès engins, dépose et stockage des bordures")]),
 ("2 · SOURCE A + LOCAL SPRINKLEUR", "S1 → S3 · la B2 reste en service", NAVY, [
   (SPK, "Pompe source A, jockey, armoire, tuyauteries, canne d'essai"),
   (SPK, "Protection et alarmes du local A, dépose pompe B1"),
   (SPK, "Source A remise en service le 17/11, AVANT la vidange de la B2"),
   (EIF, "Percement des voiles façade Nord (ventilation) - S1")]),
 ("3 · DÉVOIEMENTS ET COUPURE DE LA B2", "S1 → S3 · vidange le 18/11", NAVY, [
   (EIF, "Dévoiement incendie DN150 + AEP DN100 (S1-S2)"),
   (SPK, "Raccordements provisoires, mesures compensatoires"),
   (SPK, "Consignation + VIDANGE de la cuve B2 (18/11)")]),
 ("4 · DÉPOSES ET DÉMOLITIONS", "S2 → S5", NAVY, [
   (EIF, "Dépose brise-vue + grille (S2)"),
   (SPK, "Dépose de la cuve B2 (S3-S4) et du GMPD (S4)"),
   (EIF, "Démolition radier, étêtage -1 m, récolement (S4-S5)"),
   (EIF, "Dépose pièces de scellement, dalle local GE")]),
 ("5 · FONDATIONS ET RADIER", "S5 → S10", NAVY, [
   (EIF, "Plateforme, pieux (S6), recépage, terrassement, béton de propreté"),
   (BOTH, "Aspiration DN300 sous radier : SPK fournit, EIFFAGE pose"),
   (EIF, "Ferraillage, COULAGE du radier 29/12, durcissement 7 j")]),
 ("6 · LOCAL B2 ET LOCAL GE", "S4 → S7", NAVY, [
   (EIF, "Pose des pièces de scellement (S4), reprise dalle local GE (S6-S7)"),
   (SPK, "Nouveau GMPD (S5), tuyauteries, ventilation, détection")]),
]
LEFT = [
 ("7 · TRANCHÉES ET RÉSEAUX ENTERRÉS", "S5 → S12", NAVY, [
   (EIF, "Ouverture des tranchées, fourreaux, puisard et réseau EU"),
   (SPK, "Pose fonte DN300 / DN200 / DN150 + épreuves hydrauliques"),
   (EIF, "Remblaiement APRÈS les épreuves SPK, voirie, espaces verts")]),
 ("8 · CUVE 620 m³ (SPK)", "S11 → S14", NAVY, [
   (SPK, "Montage cuve boulonnée (S11-S12), poche PVC, toit, équipements"),
   (EIF, "Joint ciment périphérique de la cornière"),
   (SPK, "Remplissage ≤ 36 h et test d'étanchéité (S13-S14)")]),
 ("9 · POSTES DE CONTRÔLE (SPK)", "S3 → S5", NAVY, [
   (SPK, "Entretien triennal des 7 postes (un à la fois)"),
   (SPK, "Bypass, numérotation des vannes, schémas")]),
 ("10 · ESSAIS ET REMISE EN SERVICE B2", "S14 → S15 · 08/02", NAVY, [
   (SPK, "Épreuves, essais du GMPD, alarmes, REMISE EN SERVICE B2"),
   (SPK, "Vérification des postes de contrôle et des alarmes")]),
 ("11 · BRISE-VUE, FINITIONS, RÉCEPTION", "S13 → S16 · OPR 16/02", NAVY, [
   (EIF, "Charpente (S13), bardage bois (S14-S15), porte d'accès"),
   (EIF, "Enrobés, terre végétale, gazon, constat d'huissier, DOE"),
   (SPK, "Formation, DOE, repli base vie, OPR commune")]),
]

fig = plt.figure(figsize=(24, 15)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(-12, 12); ax.set_ylim(-7.9, 8.1); ax.axis("off")
ax.text(0, 7.75, "PHASAGE EXE PHASE 1 · EIFFAGE (gros œuvre / VRD) / SPK (sprinklage)", ha="center", fontsize=19, fontweight="bold", color=NAVY)

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

ys_r = [6.6, 4.3, 1.5, -1.4, -3.9, -6.2]
ys_l = [6.3, 3.7, 0.9, -1.8, -5.0]
for y, br in zip(ys_r, RIGHT): branch(5.0, y, +1, br)
for y, br in zip(ys_l, LEFT): branch(-5.0, y, -1, br)

# centre
ax.add_patch(Ellipse((0, 0), 4.8, 2.5, fc=NAVY, ec="white", lw=3, zorder=5))
ax.text(0, 0.42, "PHASE 1 · 15 SEMAINES", color="white", ha="center", fontsize=14, fontweight="bold", zorder=6)
ax.text(0, 0.0, "02/11/2026 → 16/02/2027", color="white", ha="center", fontsize=11.5, zorder=6)
ax.text(0, -0.4, "Source B2 hors service :", color="#FFD9A8", ha="center", fontsize=10.5, zorder=6)
ax.text(0, -0.68, "18/11 → 08/02 (57 j ouvrés)", color="#FFD9A8", ha="center", fontsize=10.5, fontweight="bold", zorder=6)

# légende
lx = -6.0
for c, t in [(SPK, "SPK (sprinklage)"), (EIF, "EIFFAGE (gros œuvre, VRD, CM, bardage)"), (BOTH, "Interface EIFFAGE + SPK")]:
    ax.add_patch(Circle((lx, -7.55), 0.12, color=c)); ax.text(lx + 0.25, -7.55, t, fontsize=11, va="center"); lx += 2.6 + 0.07 * len(t)
ax.text(-11.8, -7.85, "Source : tableau de limites de prestations, CCTP et DPGF des deux lots ; durées = estimations du planning EXE.", fontsize=8.5, color="#56607A")
fig.savefig(os.path.join(here, "Carte_mentale_phasage_EIFFAGE_SPK.png"), dpi=100)
fig.savefig(os.path.join(here, "Carte_mentale_phasage_EIFFAGE_SPK.pdf"))
