# -*- coding: utf-8 -*-
# Planning EIFFAGE (15 semaines) : taches EIFFAGE + interventions SPK qui conditionnent EIFFAGE (ou inversement).
import re
import data as base

B = {}
for it in base.ITEMS:
    if it[0] == "T": B[it[1]] = dict(name=it[2], lot=it[4], src=it[6], dur=it[3])
    elif it[0] == "P": B[it[1]] = dict(name=it[2], lot=it[3], src=it[6], span=(it[4], it[5]))

ITEMS = []
def S(level, name): ITEMS.append(("S", level, name))
def T(key, dur, preds, name=None, lot=None, src=None):
    b = B.get(key, {})
    ITEMS.append(("T", key, name or b.get("name", key), dur, lot or b.get("lot", "SPK"), preds, src if src is not None else b.get("src", "")))
def P(key, a, b_, name=None, lot=None, src=None):
    b = B[key]
    ITEMS.append(("P", key, name or b.get("name", key), lot or b.get("lot", "SPK"), a, b_, src if src is not None else b.get("src", "")))

S(1, "1. DEMARRAGE")
ITEMS.append(("T", "m_start", "DEMARRAGE DES TRAVAUX EIFFAGE (OS) - date modifiable via Informations sur le projet", 0, "GO", "", "Modifier la date de début du projet : tout le planning se décale."))

S(1, "2. INSTALLATION DE CHANTIER")
T("go_huissier", 1, "m_start")
T("ic_clot", 2, "m_start", name="[SPK] Clôture de chantier + base vie commune + armoire de chantier (SPK) - préalable aux interventions EIFFAGE",
  src="Limites de prestations 1 : clôture, base vie, armoire = SPK. CCTP EIFFAGE 5.1.3, 5.1.9.")
T("ic_piste", 3, "ic_clot,go_huissier")
T("ic_bord", 1, "ic_clot")

S(1, "3. PHASAGE - DEVOIEMENTS ET MISE HORS SERVICE SOURCE B2")
T("dv_rec", 1, "ic_clot")
T("dv_inc", 6, "dv_rec")
T("dv_aut", 2, "dv_rec")
T("spk_racprov", 3, "ic_clot", name="[SPK] Raccordements provisoires + mesures compensatoires avant coupure de la B2 (gardiennage MOA : préavis 5 semaines)")
T("spk_vidange", 2, "spk_racprov", name="[SPK] Consignation + VIDANGE cuve source B2 (début de l'indisponibilité de la B2)")

S(1, "4. DEPOSES ET DEMOLITIONS - SOURCE B2")
T("dm_brise", 3, "ic_clot,ic_piste,go_huissier")
T("dm_cuve", 4, "spk_vidange,dm_brise", name="[SPK] Dépose et évacuation de la cuve B2 existante (SPK) - EIFFAGE démolit le radier ensuite")
T("spk_depgmpd", 2, "spk_vidange", name="[SPK] Dépose du GMPD B2 + tuyauteries (SPK) - avant dépose des pièces de scellement EIFFAGE")
T("spk_depge", 1, "spk_vidange", name="[SPK] Dépose des réseaux existants local GE (SPK) - avant démolition dalle EIFFAGE")
T("dm_res", 3, "dm_cuve,spk_vidange")
T("dm_radier", 4, "dm_cuve,dv_inc")
T("dm_etet", 2, "dm_radier:SS+1")
T("dm_recol", 1, "dm_etet")
T("dm_purge", 2, "dm_recol")
T("go_pdb2_dep", 2, "spk_depgmpd")
T("go_dalle_ge", 2, "spk_depge")
T("go_pdge_dep", 1, "go_dalle_ge")

S(1, "5. FONDATIONS ET RADIER - CUVE B2")
T("fd_plate", 2, "dm_recol,dm_purge")
P("fd_rabat", "fd_plate", "fd_bet")
T("fd_pieux", 5, "fd_plate")
T("fd_boues", 3, "fd_pieux:SS+1")
T("fd_essais", 2, "fd_pieux")
T("fd_recep", 1, "fd_pieux")
T("fd_terr", 2, "fd_recep")
T("fd_puis", 2, "fd_terr")
T("fd_propre", 1, "fd_terr")
T("fd_terre", 1, "fd_propre")
T("fd_plat", 1, "fd_propre")
T("fd_forme", 1, "fd_propre")
T("spk_pdscell", 1, "spk_depgmpd", name="[SPK] Livraison sur site : pièces de scellement + tuyauterie d'aspiration DN300 (fournitures SPK pour EIFFAGE)")
T("fd_aspir", 1, "fd_forme,spk_pdscell")
T("fd_drain", 1, "fd_forme")
T("fd_fer", 4, "fd_aspir,fd_plat,fd_terre,fd_drain")
T("fd_bet", 1, "fd_fer")
T("fd_cure", 9, "fd_bet", src="Hypothèse 9 jours ouvrés avant chargement de la cuve : à valider BET / bureau de contrôle (28 j si exigé).")

S(1, "6. LOCAL B2, LOCAL GE ET LOCAL SPRINKLEUR - SCELLEMENTS")
T("go_pdb2_pose", 2, "go_pdb2_dep,spk_pdscell")
T("go_pdge_pose", 1, "go_pdge_dep,spk_pdscell")
T("b2_gmpd", 6, "go_pdb2_pose,spk_depgmpd", name="[SPK] Pose du nouveau GMPD + tuyauteries DN300/DN200 dans le local B2 (après scellements EIFFAGE)")
T("go_dalle_rest", 3, "go_pdge_pose,t2_spk")
T("la_perc", 2, "ic_clot")
T("la_grille", 1, "la_perc", name="[SPK] Fourniture et pose des grilles de ventilation (après percement EIFFAGE)")

S(1, "7. TRANCHEES COMMUNES ET RESEAUX ENTERRES")
T("t1_ouv", 2, "fd_bet,dm_res,dv_inc")
T("t1_fourr", 1, "t1_ouv")
T("t1_spk", 4, "t1_ouv,fd_aspir,go_pdb2_pose", name="[SPK] Pose aspiration DN300 + remplissage/retour essai DN150 + épreuves (tranchée 1) - avant remblaiement EIFFAGE")
T("t1_remb", 2, "t1_spk,t1_fourr")
T("t2_ouv", 3, "dm_res,dv_inc")
T("t2_fourr", 1, "t2_ouv")
T("t2_spk", 5, "t2_ouv,go_pdb2_pose,go_pdge_pose", name="[SPK] Pose refoulement DN200 jusqu'au local GE + épreuves (tranchée 2) - avant remblaiement EIFFAGE")
T("t2_remb", 2, "t2_spk,t2_fourr")
T("eu_tr", 3, "fd_puis")
T("rs_eu", 2, "rs_mont", name="[SPK] Réseau EU aérien trop-plein/vidange, sortie à 1,00 m du nu cuve (SPK) - raccordé ensuite par EIFFAGE")
T("eu_rac", 1, "eu_tr,rs_eu")
T("eu_remb", 1, "eu_rac")
T("el_cable", 3, "t1_fourr,t2_fourr", name="[SPK] Tirage des câbles TGBT / reports d'alarme dans les fourreaux EIFFAGE")

S(1, "8. CUVE B2 620 m3 (SPK) - INTERFACES")
T("rs_livr", 2, "fd_bet", name="[SPK] Livraison de la cuve sur site")
T("rs_mont", 8, "fd_cure,rs_livr", name="[SPK] Implantation et montage de la cuve boulonnée O 12,48 m x H 5,74 m sur le radier EIFFAGE")
T("rs_fin", 5, "rs_mont", name="[SPK] Poche PVC, toit autoportant, échelle, équipements de la cuve")
T("rs_joint", 1, "rs_mont")
T("rs_remp", 3, "rs_fin,rs_joint,eu_rac", name="[SPK] Remplissage de la cuve (<= 36 h) + test d'étanchéité")
T("spk_msb2", 3, "rs_remp,b2_gmpd,t1_spk,t2_spk", name="[SPK] Essais + REMISE EN SERVICE de la source B2 (fin de l'indisponibilité de la B2)")
P("spk_comp1", "spk_vidange", "spk_msb2", name="[SPK/MOA] Mesures compensatoires + gardiennage pendant l'indisponibilité de la source B2", lot="SPK/MOA")

S(1, "9. BRISE-VUE : CHARPENTE, BARDAGE BOIS, PORTE")
T("bv_charp", 4, "rs_fin,t1_remb")
T("bv_ossat", 3, "bv_charp:SS+2")
T("bv_lames", 6, "bv_ossat:SS+2")
T("bv_porte", 1, "bv_ossat")

S(1, "10. VOIRIES ET ESPACES VERTS - REMISE EN ETAT")
T("vr_bord", 1, "t2_remb,ic_bord")
T("vr_enr", 3, "vr_bord,t1_remb")
T("vr_pist", 1, "bv_charp,eu_remb,go_dalle_rest,t1_remb")
T("vr_terre", 2, "vr_pist")
T("vr_prep", 1, "vr_terre")
T("vr_semis", 1, "vr_prep")
T("vr_chem", 1, "vr_pist")
T("vr_cur", 1, "eu_remb,vr_pist")

S(1, "11. FIN DE CHANTIER EIFFAGE")
T("fin_hui", 1, "vr_semis,vr_chem,vr_enr,vr_cur,bv_lames,bv_porte")
T("go_doe", 3, "fin_hui,fd_essais")
ITEMS.append(("T", "m_fin", "FIN DES TRAVAUX EIFFAGE", 0, "GO", "go_doe", ""))

S(1, "12. PRESTATIONS TRANSVERSES EIFFAGE (hamacs)")
P("hm_port", "ic_clot", "fin_hui")
P("hm_abords", "ic_clot", "fin_hui")
P("hm_homme_go", "dm_brise", "vr_pist")
P("hm_bennes", "dm_brise", "vr_pist")

# numerotation des sous-chapitres : aucune (un seul niveau)
