# -*- coding: utf-8 -*-
# Planning EXE 15 semaines : derive de data.py (sans etudes/appro, durees et enchainements recales)
import re
import data

RECALE = " | Durée recalée EXE (15 semaines) : renfort d'équipes / travail en parallèle."

# 1) suppression du chapitre 2 (preparation, etudes, validations, approvisionnements)
items, skip, removed = [], False, set()
for it in data.ITEMS:
    if it[0] == "S" and it[1] == 1:
        skip = it[2].startswith("2. PREPARATION")
    if skip:
        if it[0] in ("T", "P"): removed.add(it[1])
        continue
    items.append(it)
removed.discard("m_start")

OV = {  # cle: (duree, predecesseurs ou None si inchange)
 "ic_clot": (2, "m_start"), "ic_bv": (2, "ic_clot"), "ic_fluides": (2, "ic_bv"), "ic_armoire": (1, None), "ic_prot": (1, "ic_clot"),
 "ic_piste": (3, "ic_clot"), "ic_bord": (1, "ic_clot"),
 "dv_rec": (1, "ic_clot"), "dv_inc": (6, "dv_rec"), "dv_aut": (2, "dv_rec"), "spk_racprov": (3, "ic_clot"),
 "spk_vidange": (2, "spk_racprov,sa_ms"),
 "dm_brise": (3, "ic_clot,ic_piste"), "dm_cuve": (4, None), "dm_res": (3, None), "dm_radier": (3, "dm_cuve,dv_inc"),
 "dm_etet": (2, "dm_radier:SS+1"), "dm_recol": (1, None), "dm_purge": (2, None),
 "spk_depgmpd": (2, None), "spk_depge": (1, None), "go_pdb2_dep": (2, None), "go_dalle_ge": (2, None), "go_pdge_dep": (1, None),
 "fd_plate": (2, None), "fd_pieux": (4, "fd_plate"), "fd_boues": (3, None), "fd_recep": (1, None), "fd_terr": (2, None), "fd_puis": (2, None),
 "fd_terre": (1, None), "fd_plat": (1, None), "fd_forme": (1, None), "fd_aspir": (1, "fd_forme"), "fd_drain": (1, None), "fd_fer": (4, None),
 "fd_cure": (7, None),
 "rs_livr": (2, "fd_bet"), "rs_mont": (6, None), "rs_poche": (2, None), "rs_toit": (3, None), "rs_equip": (3, None), "rs_eu": (1, None),
 "b2_ea": (1, "rs_poche"), "rs_remp": (2, None),
 "t1_ouv": (2, None), "t1_fourr": (1, None), "t1_spk": (3, "t1_ouv,fd_aspir,go_pdb2_pose"), "t1_remb": (2, None),
 "t2_ouv": (3, "dm_res,dv_inc"), "t2_fourr": (1, None), "t2_spk": (4, "t2_ouv,go_pdb2_pose,go_pdge_pose"),
 "eu_tr": (3, None), "eu_rac": (1, None), "el_cable": (3, "t1_fourr,t2_fourr"),
 "go_pdb2_pose": (2, None), "go_pdge_pose": (1, None), "b2_gmpd": (5, "go_pdb2_pose,spk_depgmpd"), "b2_tuy": (4, "b2_gmpd,go_pdb2_pose"),
 "b2_nour": (1, None), "b2_vent": (2, None), "b2_det": (2, None), "go_dalle_rest": (3, None),
 "la_perc": (2, "ic_clot"), "la_grille": (1, "la_perc"), "la_floc": (2, "ic_clot"), "la_prot": (4, "ic_prot"), "la_det": (2, None),
 "la_arm": (2, "ic_clot"), "la_aff": (2, None),
 "sb1_dep": (2, "ic_prot"), "sa_comp": (1, "ic_prot"), "sa_pompe": (3, None), "sa_tuy": (2, None), "sa_arm": (3, None), "sa_res": (1, None),
 "sa_nour": (1, None), "sa_canne": (1, None), "sa_seuil": (1, "sa_pompe"),
 "pc1": (1, "sa_ms"), "pc2": (1, None), "pc3": (1, None), "pc4": (1, None), "pc5": (1, None), "pc6": (1, None), "pc7": (1, None),
 "pc_vis": (2, None), "pc_byp": (4, None), "pc_num": (1, None),
 "el_arm": (3, "la_arm"), "el_cab": (3, None), "el_tab": (1, None), "el_terre": (1, None), "al_rep": (2, None), "al_ver": (1, None), "pt_peint": (2, None),
 "es_epr": (2, None), "es_b2": (2, None), "es_ident": (2, None), "es_pc": (2, None), "es_q1": (2, None),
 "es_form": (1, "es_pc,es_src,es_ident,es_rech,spk_msb2"), "es_doe": (3, None),
 "bv_charp": (4, "rs_toit,rs_equip"), "bv_ossat": (3, "bv_charp:SS+2"), "bv_lames": (6, "bv_ossat:SS+2"),
 "vr_enr": (3, None), "vr_pist": (1, "bv_charp,eu_remb,go_dalle_rest,t1_remb"), "vr_terre": (2, None), "vr_prep": (1, None), "vr_semis": (1, None),
 "vr_chem": (1, None), "vr_cur": (1, "eu_remb,vr_pist"),
 "fin_hui": (1, "vr_semis,vr_chem,vr_enr,vr_cur,bv_lames"), "go_doe": (3, None), "fin_repli": (2, None), "fin_opr": (1, None),
}
SECT = {"11. SOURCES A / B1 / JOCKEY (apres remise en service de la source B2)": "SOURCES A / B1 / JOCKEY (AVANT vidange B2 - la B2 reste en service pendant ces travaux)",
        "12. POSTES DE CONTROLE (apres retour des sources)": "POSTES DE CONTROLE (après retour de la source A, B2 vidangée : mesures compensatoires)"}

def clean_preds(p):
    return ",".join(x for x in p.split(",") if x and re.match(r"\w+", x).group(0) not in removed)

out = []
for it in items:
    if it[0] == "S":
        name = SECT.get(it[2], it[2]); out.append(("S", it[1], name)); continue
    if it[0] == "T":
        _, key, name, dur, lot, preds, src = it
        if key in OV:
            d, p = OV[key]
            if d != dur: src = src + RECALE
            dur = d
            if p is not None: preds = p
        preds = clean_preds(preds)
        out.append(("T", key, name, dur, lot, preds, src))
    else:
        _, key, name, lot, a, b, src = it
        if key == "hm_homme_spk": a, b = "rs_livr", "rs_remp"
        out.append(("P", key, name, lot, a, b, src))

# 2) renumerotation des chapitres
n1 = n2 = 0
for i, it in enumerate(out):
    if it[0] == "S":
        base = re.sub(r"^\d+(\.\d+)?\.?\s*", "", it[2])
        if it[1] == 1: n1 += 1; n2 = 0; out[i] = ("S", 1, "%d. %s" % (n1, base))
        else: n2 += 1; out[i] = ("S", it[1], "%d.%d %s" % (n1, n2, base))
ITEMS = out
