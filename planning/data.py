# -*- coding: utf-8 -*-
# Definition des taches du planning Phase 1 (GO/VRD/CM/Bardage + SPK)
# T(cle, nom, duree_jours_ouvres, lot, predecesseurs, source/hypothese)
# preds : "cle", "cle:SS", "cle:FF", "cle+3" (decalage jours ouvres), "cle:SS+2"
# SPAN(cle, nom, lot, debut_cle, fin_cle, source) : tache "hamac" (SS depuis debut, FF depuis fin)

ITEMS = []
def S(level, name): ITEMS.append(("S", level, name))
def T(key, name, dur, lot, preds, src=""): ITEMS.append(("T", key, name, dur, lot, preds, src))
def SPAN(key, name, lot, a, b, src=""): ITEMS.append(("P", key, name, lot, a, b, src))

CCTP_GO = "CCTP GO/VRD"
CCTP_SPK = "CCTP SPK"
LIM = "Limites de prestations"

# ---------------------------------------------------------------- 1
S(1, "1. JALONS")
T("m_start", "DEMARRAGE PHASE 1 (OS) - date modifiable via Informations sur le projet", 0, "MOA", "",
  "Modifier la date de debut du projet : tout le planning se decale automatiquement.")

# ---------------------------------------------------------------- 2
S(1, "2. PREPARATION - ETUDES, VALIDATIONS, APPROVISIONNEMENTS")
S(2, "2.1 Administratif / MOA")
T("moa_rep", "[MOA] Reperage des reseaux enterres existants (detection non intrusive, releve NCA)", 5, "MOA", "m_start",
  LIM + " 1 ; CCTP SPK 3.5.4 : detection prevue par le MO avant travaux de reseaux enterres. Duree estimee.")
T("moa_tgbt", "[MOA] Fourniture des notes de calcul du TGBT existant", 5, "MOA", "m_start", LIM + " 3. Duree estimee.")
T("moa_gn13", "[MOA] Dossier GN 13 - avant lancement des interventions (SPK/GO/VRD participent)", 10, "MOA", "m_start",
  LIM + " 2 : MOA = X ; SPK/VRD/GO = P. Duree estimee.")
T("spk_apsad", "[SPK] Transmission de la certification APSAD de l'entreprise", 2, "SPK", "m_start", LIM + " 3.")
T("spk_sps", "[SPK] Coordination SPS - etablissement du plan de prevention", 3, "SPK", "m_start", "DPGF SPK - Frais de chantier.")
T("go_huissier", "[GO] Constat d'huissier avant travaux (site, voiries, vegetation)", 2, "GO", "m_start", "DPGF GO 5.1.1 ; CCTP GO 5.1.1 / 3.5.")

S(2, "2.2 Etudes et validations lot SPRINKLAGE")
T("spk_rel", "[SPK] Releve des installations existantes + plans a jour (AutoCAD)", 5, "SPK", "m_start", "CCTP SPK 3.1.3. Duree estimee.")
T("spk_eau", "[SPK] Analyse electrochimique de l'eau", 5, "SPK", "m_start", "DPGF SPK 3.1.3.")
T("spk_etudes", "[SPK] Etudes d'execution, calculs hydrauliques (NPSH, volume utile reserve), reprise des plans", 15, "SPK", "spk_rel",
  "DPGF SPK 3.1.2 ; CCTP SPK 1.17 (programme sous 8 jours). Duree estimee.")
T("spk_calage", "[SPK] Transmission au GO des fiches techniques cuve : charges, radier, joint corniere, pieces de scellement", 3, "SPK", "spk_etudes",
  LIM + " 4 (radier : SPK definit le principe, GO realise) ; CCTP GO 4.7.4, 5.5.5, 5.8.1.")
T("spk_elec", "[SPK] Schemas et notes electriques (armoires, alimentation pompes, GTB/alarmes)", 5, "SPK", "spk_etudes,moa_tgbt", LIM + " 3 ; DPGF SPK 3.17.")
T("spk_vis", "[SPK] Visa Bureau de controle + BET ABSIX des documents d'execution", 10, "SPK", "spk_etudes", "CCTP SPK 1.x (visa 15 j max). Duree estimee.")
T("spk_plangard", "[SPK] Remise au MOA du planning previsionnel de gardiennage (>= 5 semaines avant 1re coupure)", 1, "SPK", "spk_etudes",
  LIM + " 2 : demande minimum 5 semaines avant intervention.")

S(2, "2.3 Etudes et validations lot GROS OEUVRE / VRD")
T("go_pic", "[GO] Plan d'installation de chantier + coordination avec SPK (base vie commune)", 3, "GO", "m_start", "DPGF GO 5.1.2 ; CCTP GO 5.1.2.")
T("go_geom", "[GO] Implantation par geometre : PV d'implantation + niveaux NGF + traits de niveau", 3, "GO", "m_start", "DPGF GO 5.2.2 / 5.2.3.")
T("go_peo", "[GO] Etudes d'execution (PEO) : pieux, radier, charpente brise-vue, reseaux, descentes de charges, notes de calcul", 20, "GO", "spk_calage",
  "DPGF GO 5.2.4 ; CCTP GO 3.2 / 5.2.4. Duree estimee.")
T("go_g3", "[GO] Mission G3 : validation fondations, etude de pompage/rabattement, controles", 10, "GO", "spk_calage", "DPGF GO 5.2.5 ; CCTP GO 5.2.5. Duree estimee.")
T("go_vis", "[GO] Validation des PEO par Bureau de controle et MOE (G4)", 10, "GO", "go_peo,go_g3", "CCTP GO 5.2.4 : travaux conditionnes a la validation des plans.")
T("go_soumis", "[GO] Soumission pour approbation : grilles ventilation, bois bardage, porte (RAL), echantillons bordures", 5, "GO", "go_pic",
  "CCTP GO 5.8.4, 5.9.2, 5.9.3, 5.10.3.")

S(2, "2.4 Approvisionnements / fabrications")
T("spk_cmd", "[SPK] Commande + fabrication reserve aerienne boulonnee 620 m3 (cuve, poche PVC, toit, echelle)", 40, "SPK", "spk_vis",
  "CCTP SPK 3.5.4 b. Delai de fabrication estime a 8 semaines : A CONFIRMER avec le fournisseur (APRO/SFR).")
T("spk_gmpd", "[SPK] Commande + fabrication GMPD source B2 (360 m3/h - 90 mCE)", 50, "SPK", "spk_vis",
  "CCTP SPK 3.5.4 a. Delai estime a 10 semaines : A CONFIRMER fournisseur.")
T("spk_pdscell", "[SPK] Fourniture des pieces de scellement DN300 / DN200 / DN150 + echappement", 15, "SPK", "spk_vis",
  LIM + " 4 (source B2, local GE) : fourniture SPK.")
T("spk_fonte", "[SPK] Approvisionnement canalisations fonte ductile DN300/DN200/DN150, vannes, accessoires, butees", 20, "SPK", "spk_vis", "CCTP SPK 3.5.4 / 3.5.5.")
T("spk_pompeA", "[SPK] Approvisionnement electropompe source A, jockey, armoires, nourrices pressostatiques, clapet EA", 25, "SPK", "spk_vis", "DPGF SPK 3.5.")
T("spk_grilles", "[SPK] Approvisionnement grilles de ventilation haute et basse (local source A)", 10, "SPK", "spk_vis,go_soumis", LIM + " 4 : fourniture et pose SPK.")
T("go_platines", "[GO] Fourniture platines de pre-scellement et boites de reservation (poteaux brise-vue)", 10, "GO", "go_vis", "DPGF GO 5.5.4.")
T("go_charp", "[GO/CM] Fabrication charpente metallique brise-vue (profiles galvanises, contreventement)", 25, "GO", "go_vis", "DPGF GO 5.7.1 (kg). Duree estimee.")
T("go_bois", "[GO/Bardage] Approvisionnement bois douglas (seche 18 %), omega galvanises, quincaillerie inox", 15, "GO", "go_vis,go_soumis", "DPGF GO 5.9.1 / 5.9.2.")
T("go_porte", "[GO] Fabrication porte d'acces cuve B2 (900 x 2100, 1 vantail) - serrure a commander via MOA", 20, "GO", "go_vis,go_soumis", "DPGF GO 5.9.3 ; CCTP GO 5.9.3.")

# ---------------------------------------------------------------- 3
S(1, "3. INSTALLATION DE CHANTIER")
T("ic_clot", "[SPK] Cloture de chantier, panneau de chantier, signalisation", 2, "SPK", "go_pic,moa_gn13,go_huissier,spk_sps,spk_apsad",
  LIM + " 1 ; CCTP GO 5.1.3-5.1.5. Demarrage conditionne au dossier GN13.")
T("ic_bv", "[SPK] Base vie (25 pers., 2 bungalows reunion, ~100 m2 stockage SPK) commune aux lots", 3, "SPK", "ic_clot", LIM + " 1 ; CCTP SPK 1.19.")
T("ic_fluides", "[SPK] Raccordement fluides + evacuation de la base vie (eau, electricite, fosse toutes eaux)", 3, "SPK", "ic_bv", LIM + " 1 ; DPGF GO 5.1.6 (abonnements MOA).")
T("ic_armoire", "[SPK] Armoire electrique de chantier + point d'eau pres de la zone cuve", 2, "SPK", "ic_bv", LIM + " 1.")
T("ic_prot", "[SPK] Protection par bachage des equipements commerciaux et techniques existants", 1, "SPK", "ic_clot", LIM + " 2 ; CCTP SPK 3.1.6.")
T("ic_piste", "[GO] Pistes d'acces engins + plateforme de circulation sur geotextile classe 5", 4, "GO", "ic_clot,go_geom", "DPGF GO 5.3.3 ; " + LIM + " 1 (si necessaire).")
T("ic_bord", "[GO] Depose et stockage des bordures beton (reemploi en fin de chantier)", 1, "GO", "ic_clot,go_geom", "DPGF GO 5.3.4.")

# ---------------------------------------------------------------- 4
S(1, "4. PHASAGE - DEVOIEMENTS ET MISE HORS SERVICE SOURCE B2")
T("dv_rec", "[GO] Piquetage/marquage et reconnaissance des reseaux existants dans l'emprise (DN100 AEP, DN150 incendie, EU/EV/EP/elec/fibre)", 2, "GO", "moa_rep,ic_clot", "CCTP GO 5.6.2 ; " + LIM + " 1.")
T("dv_inc", "[GO] Devoiement reseau incendie DN150 + alimentation AEP/arrosage DN100 hors emprise radier (essais, DOE)", 8, "GO", "dv_rec,go_vis,moa_gn13",
  "DPGF GO 5.6.2 ; " + LIM + " 1. Continuite du reseau incendie a maintenir (coupure ponctuelle validee MOA).")
T("dv_aut", "[VRD] Devoiement EU / EV / EP / electricite / fibre / arrosage si necessaire (releve NCA)", 3, "VRD", "dv_rec", LIM + " 1 (si necessaire).")
T("spk_racprov", "[SPK] Raccordements provisoires pour maintien de la protection sprinkleur de l'etablissement", 4, "SPK", "spk_vis,ic_fluides",
  LIM + " 2 ; DPGF SPK 3.1.4 ; CCTP SPK 3.1.4. Duree estimee.")
T("spk_vidange", "[SPK] Consignation + vidange cuve source B2 et reseaux associes (mesures compensatoires actives)", 2, "SPK",
  "spk_racprov,dv_inc,dv_aut,spk_plangard+25,go_vis", LIM + " 1/2. Decalage 25 jours ouvres = 5 semaines de preavis gardiennage.")
T("spk_comp1", "[SPK/MOA] Mesures compensatoires + gardiennage pendant l'indisponibilite de la source B2", 0, "SPK", "spk_vidange", "")  # remplace par SPAN ci-dessous
ITEMS.pop()  # on remplace par SPAN
SPAN("spk_comp1", "[SPK/MOA] Mesures compensatoires (renfort securite) + gardiennage pendant l'indisponibilite de la source B2", "SPK/MOA",
     "spk_vidange", "spk_msb2", LIM + " 2 ; DPGF SPK 3.1.4 / 3.1.5. Hamac : duree = vidange -> remise en service B2.")

# ---------------------------------------------------------------- 5
S(1, "5. DEPOSES ET DEMOLITIONS - SOURCE B2 / LOCAUX")
S(2, "5.1 Cuve B2 et enclos brise-vue")
T("dm_brise", "[GO] Depose brise-vue bois + charpente metallique support + grille d'acces/porte grillagee (evacuation)", 4, "GO",
  "ic_clot,ic_piste,go_vis,moa_gn13", "DPGF GO 5.4.1 ; " + LIM + " 4 / Travaux reserves d'eau B2. Fait avant la vidange pour reduire l'indisponibilite.")
T("dm_cuve", "[SPK] Depose et evacuation de la reserve source B existante + equipements et reseaux associes", 6, "SPK", "spk_vidange,dm_brise",
  "DPGF SPK 3.5 ; CCTP GO 5.4.2 (par lot SPK). Duree estimee (cuve acier 405 m3).")
T("dm_res", "[VRD] Depose des reseaux existants cuve B2 -> local B2 -> local A/GE (terrassement, evacuation, remblaiement)", 5, "VRD", "dm_cuve,spk_vidange",
  "DPGF GO 5.6.3 ; " + LIM + " 1 (depose reseaux depuis cuve B2 jusqu'au local source A et B2 = VRD).")
T("dm_radier", "[GO] Demolition du radier existant + evacuation des gravats (maitrise poussieres)", 4, "GO", "dm_cuve", "DPGF GO 5.4.3 (ens.). Duree estimee.")
T("dm_etet", "[GO] Etetage des fondations existantes a -1,00 m du niveau plateforme + evacuation", 3, "GO", "dm_radier", LIM + " 4.")
T("dm_recol", "[GO] Releve geometre + plan de recolement des ouvrages enterres, adaptation des fondations", 2, "GO", "dm_etet", LIM + " 4 ; CCTP GO 5.4.4.")
T("dm_purge", "[GO] (OPTION 5.4.4) Purge des fondations profondes existantes (-80 cm sous niveau final) + remblai sablo-graveleux", 3, "GO", "dm_recol",
  "DPGF GO 5.4.4 OPTIONNEL : mode de fondation existant inconnu. Mettre la duree a 0 si l'option n'est pas retenue.")
S(2, "5.2 Local source B2 et local GE")
T("spk_depgmpd", "[SPK] Depose GMPD source B2 + equipements, tuyauteries aspiration/refoulement (demontage et livraison du GMPD demonte)", 3, "SPK", "spk_vidange",
  "DPGF SPK 3.5 (Source B2 - GMPD).")
T("spk_depge", "[SPK] Depose des reseaux existants local GE", 2, "SPK", "spk_vidange", LIM + " Travaux local GE.")
T("go_pdb2_dep", "[GO] Depose des pieces de scellement existantes local B2 + reprise des percements (DN300, DN200, DN150, echappement)", 3, "GO", "spk_depgmpd",
  "DPGF GO 5.8.2 ; " + LIM + " Travaux source B2.")
T("go_dalle_ge", "[GO] Demolition controlee reservation dalle basse et soubassement local GE (sciage, mise a nu des armatures)", 3, "GO", "spk_depge",
  "DPGF GO 5.8.5 ; " + LIM + " Travaux local GE.")
T("go_pdge_dep", "[GO] Depose piece de scellement existante local GE + creation du percement DN200", 2, "GO", "go_dalle_ge", LIM + " Travaux local GE.")

# ---------------------------------------------------------------- 6
S(1, "6. FONDATIONS ET RADIER - CUVE B2")
T("fd_plate", "[GO] Plateforme de travail pour pieux (portance EV2 > 50 MPa, geotextile)", 3, "GO", "dm_recol,dm_purge", LIM + " 4 ; DPGF GO 5.3.3.")
SPAN("fd_rabat", "[GO] Epuisement des eaux / rabattement de nappe (nappe ~ 27,4 NGF) pendant les fondations", "GO", "fd_plate", "fd_bet",
     "DPGF GO 5.3.7 ; CCTP GO 4.7.2 ; " + LIM + " 3. Hamac plateforme -> coulage radier.")
T("fd_pieux", "[GO] Pieux a tariere creuse (amenee/repli du materiel, forage, armatures, beton) - ~20 a 25 u. a confirmer PEO", 5, "GO", "fd_plate,go_vis,dm_recol",
  "DPGF GO 5.5.1 (u) ; CCTP GO 5.5.1 ; G2PRO Fondasol. Hypothese ~5 pieux/jour.")
T("fd_boues", "[GO] Stockage sur polyane et evacuation des terres et boues de forage + nettoyage voies", 4, "GO", "fd_pieux:SS+1", "DPGF GO 5.5.2 / 5.3.8.")
T("fd_essais", "[GO] Essais et controle des pieux (DTU 13.2 / NF P94-262)", 2, "GO", "fd_pieux", "CCTP GO 5.5.1.")
T("fd_recep", "[GO] Recepage des pieux", 2, "GO", "fd_pieux", "CCTP GO 5.5.1.")
T("fd_terr", "[GO] Terrassement fouille radier + substitution remblais de portance + fond de forme (debord 1 m)", 3, "GO", "fd_recep", "DPGF GO 5.3.5 / 5.3.6 (m3).")
T("fd_puis", "[GO] Puisard de trop-plein de la cuve (terrassement, beton de proprete, grille circulable)", 3, "GO", "fd_terr", "DPGF GO 5.6.6 ; CCTP GO 5.6.6.")
T("fd_propre", "[GO] Beton de proprete (e >= 5 cm) sous radier", 1, "GO", "fd_terr", "DPGF GO 5.5.3.")
T("fd_terre", "[GO] Boucle de terre fond de fouille (cable nu 25 mm2, R <= 3 ohms) + attentes de terre cuve", 2, "GO", "fd_propre", "DPGF GO 5.3.9 ; " + LIM + " 3 (boucle de terre du radier = GO).")
T("fd_plat", "[GO] Pose massifs, platines et boites de reservation de pre-scellement (poteaux brise-vue)", 2, "GO", "fd_propre,go_platines", "DPGF GO 5.5.4.")
T("fd_forme", "[GO] Couche de forme + sablon d'egalisation + film polyethylene", 2, "GO", "fd_propre", "CCTP GO 5.5.5.")
T("fd_aspir", "[GO] Pose et incorporation de la tuyauterie d'aspiration DN300 sous radier (fournie SPK) + validation implantation SPK/GO", 2, "GO/SPK",
  "fd_forme,spk_pdscell,spk_fonte", LIM + " 4 : GO realise, SPK accompagne (P) et valide l'implantation avant coulee.")
T("fd_drain", "[GO] Drain peripherique / gestion des eaux autour du radier (si G2PRO l'impose)", 2, "GO", "fd_forme", LIM + " 4 (conditionnel).")
T("fd_fer", "[GO] Ferraillage radier (TS + HA), attentes pieux, reservations, fourreaux, coffrage de rives et beches peripheriques", 5, "GO",
  "fd_aspir,fd_plat,fd_terre,fd_drain", "DPGF GO 5.5.5 (m3). Duree estimee (radier ~ O 14 m).")
T("fd_bet", "[GO] Coulage du radier beton C25/30 XC2 XF1 (parement soigne, circulations brossees antiderapantes)", 1, "GO", "fd_fer", "DPGF GO 5.5.5 ; CCTP GO 4.4.")
T("fd_cure", "[GO] Durcissement du radier avant chargement de la cuve (delai a valider BET / bureau de controle)", 10, "GO", "fd_bet",
  "Hypothese 10 jours ouvres. Passer a 20 jours si resistance a 28 j exigee.")

# ---------------------------------------------------------------- 7
S(1, "7. RESERVE D'EAU AERIENNE B2 (620 m3)")
T("rs_livr", "[SPK] Livraison cuve + equipements sur site, reception, stockage", 2, "SPK", "spk_cmd,ic_bv", "CCTP SPK 3.5.4 b.")
T("rs_impl", "[SPK] Implantation cuve, pose corniere de fixation, controle planeite", 1, "SPK", "fd_cure,rs_livr", "CCTP SPK 3.5.4 b.")
T("rs_mont", "[SPK] Montage cuve boulonnee O 12,48 m x H 5,74 m", 10, "SPK", "rs_impl", "DPGF SPK 3.5 (Reserve d'eau). Duree estimee.")
T("rs_poche", "[SPK] Pose feutre geotextile + poche PVC (garantie decennale)", 3, "SPK", "rs_mont", "CCTP SPK 3.5.4 b.")
T("rs_toit", "[SPK] Toit autoportant galvanise, echelle a crinoline, plateforme, trappe cadenassable", 4, "SPK", "rs_poche", "CCTP SPK 3.5.4 b.")
T("rs_equip", "[SPK] Equipements : trop-plein DN150, vidange DN80, remplissage/retour essai DN150 disconnecte, aspiration DN300 anti-vortex, jauge, epingle chauffante, chambre de disconnexion, alarmes",
  5, "SPK", "rs_poche", "DPGF SPK 3.5 ; " + LIM + " 4 (reserve aerienne y c. equipements).")
T("rs_joint", "[GO] Joint ciment peripherique autour de la corniere de fixation de la cuve", 1, "GO", "rs_poche", "DPGF GO 5.8.1 (ml) ; " + LIM + " 4.")
T("rs_eu", "[SPK] Reseaux EU aeriens : trop-plein et vidange (DN200), sorties a 1,00 m du nu cuve", 2, "SPK", "rs_equip", LIM + " 5 (Vidange - Eaux usees).")
T("b2_ea", "[SPK] Clapet anti-pollution type EA sur arrivee eau de ville DN65 + vers EU + vanne de contre-barrage", 2, "SPK", "rs_poche,spk_pompeA",
  "DPGF SPK 3.5 (Systemes d'essai).")
T("rs_remp", "[SPK] Remplissage de la cuve (<= 36 h) + test d'etancheite", 3, "SPK", "rs_equip,rs_toit,rs_joint,b2_ea,eu_rac",
  "CCTP SPK 3.5.4 b. (remplissage en 36 h maximum). Evacuation EU du trop-plein necessaire.")

# ---------------------------------------------------------------- 8
S(1, "8. RESEAUX ENTERRES / TRANCHEES COMMUNES")
S(2, "8.1 Tranchee 1 - cuve B2 <-> local source B2")
T("t1_ouv", "[VRD] Ouverture tranchee commune (~ 25 ml estimes)", 3, "VRD", "fd_bet,dm_res,dv_inc", "DPGF GO 5.6.1 (ml) ; " + LIM + " 5. Longueur estimee : a relever sur plan.")
T("t1_fourr", "[VRD] Fourreaux electriques 2 x O90 (local B2 / reserve d'eau) + chambre de tirage", 2, "VRD", "t1_ouv", "DPGF GO 5.6.4 / 5.6.5 ; " + LIM + " 5 (Electricite).")
T("t1_spk", "[SPK] Pose aspiration fonte DN300 + remplissage/retour essai DN150 (butees beton, tiges filetees) de la cuve a la piece de scellement", 4, "SPK",
  "t1_ouv,spk_fonte,fd_aspir,go_pdb2_pose", LIM + " 5 : tableau mentionne remplissage DN200 / retour essai DN150 (CCTP : DN150).")
T("t1_epr", "[SPK] Epreuves hydrauliques des reseaux enterres tranchee 1", 1, "SPK", "t1_spk", "DPGF SPK 3.22.")
T("t1_remb", "[VRD] Grillage avertisseur + remblaiement et compactage tranchee 1 (95 % OPM)", 2, "VRD", "t1_epr,t1_fourr", LIM + " 5 : remblaiement VRD apres pose SPK.")
S(2, "8.2 Tranchee 2 - local source B2 <-> local GE / source A")
T("t2_ouv", "[VRD] Ouverture tranchee commune (~ 60 ml estimes, sciage voirie lourde + espace vert)", 4, "VRD", "dm_res,dv_inc", "DPGF GO 5.6.1 / 5.3.2 ; " + LIM + " 5. Longueur estimee.")
T("t2_fourr", "[VRD] Fourreaux electriques 2 x O90 (local GE / local B2) + chambre de tirage", 2, "VRD", "t2_ouv", "DPGF GO 5.6.4 / 5.6.5.")
T("t2_spk", "[SPK] Pose refoulement fonte DN200 de la piece de scellement B2 jusqu'au local GE (butees beton)", 5, "SPK",
  "t2_ouv,spk_fonte,go_pdb2_pose,go_pdge_pose", LIM + " 5 (Liaison local B2 <-> local GE).")
T("t2_epr", "[SPK] Epreuves hydrauliques du refoulement enterre tranchee 2", 1, "SPK", "t2_spk", "DPGF SPK 3.22.")
T("t2_remb", "[VRD] Grillage avertisseur + remblaiement et compactage tranchee 2", 3, "VRD", "t2_epr,t2_fourr", LIM + " 5.")
S(2, "8.3 Tranchee 3 - EU (puisard trop-plein -> regard existant)")
T("eu_tr", "[VRD] Tranchee + reseau de collecte exterieur EU PVC DN200 (puisard/vidange -> regard existant), regard 500x500", 4, "VRD", "fd_puis", "DPGF GO 5.6.7 (ml) ; " + LIM + " 5.")
T("eu_rac", "[VRD] Raccordement sur reseau EU existant (branchement), boite de branchement, reprise des sorties EU a 1,00 m", 2, "VRD", "eu_tr,rs_eu", LIM + " 5.")
T("eu_remb", "[VRD] Remblaiement et compactage tranchee EU", 1, "VRD", "eu_rac", LIM + " 5.")
S(2, "8.4 Electricite - reseaux enterres")
T("el_cable", "[SPK] Reseau aerien + sortie fourreau a 1 m du nu batiment, cable TGBT -> penetration, cables reports d'alarme (tirage)", 4, "SPK",
  "t1_fourr,t2_fourr,spk_elec", LIM + " 5 (Electricite).")

# ---------------------------------------------------------------- 9
S(1, "9. LOCAL SOURCE B2 / LOCAL GE - SCELLEMENTS ET EQUIPEMENTS")
T("go_pdb2_pose", "[GO] Pose nouvelles pieces de scellement local B2 (DN300, DN200, DN150, echappement), reprise mortier, etancheite, calfeutrement", 3, "GO",
  "go_pdb2_dep,spk_pdscell", "DPGF GO 5.8.3 ; " + LIM + " Travaux source B2.")
T("go_pdge_pose", "[GO] Pose nouvelle piece de scellement refoulement DN200 local GE + calfeutrement", 2, "GO", "go_pdge_dep,spk_pdscell", LIM + " Travaux local GE.")
T("b2_gmpd", "[SPK] Fourniture et installation du nouveau GMPD B2 (equipements, echappement/silencieux, reservoir fuel 500 L double peau)", 6, "SPK",
  "spk_gmpd,go_pdb2_pose,spk_depgmpd", "DPGF SPK 3.5 (Source B2). Duree estimee.")
T("b2_tuy", "[SPK] Tuyauteries DN300 aspiration / DN200 refoulement dans le local B2 + canne d'essai DN150", 5, "SPK", "b2_gmpd,go_pdb2_pose,spk_fonte", "DPGF SPK 3.5.")
T("b2_nour", "[SPK] Remplacement nourrice pressostatique source B2 + pressostats", 2, "SPK", "b2_tuy", "DPGF SPK 3.5 (Nourrices).")
T("b2_debit", "[SPK] Etalonnage du debitmetre electromagnetique source B2 (ecart > 5 %)", 1, "SPK", "b2_tuy", "DPGF SPK 3.5 (Systemes d'essai).")
T("b2_elec", "[SPK] Armoire de commande/demarrage GMPD, cablage, raccordement armoire generale", 3, "SPK", "b2_gmpd,spk_elec", "DPGF SPK 3.17 ; CCTP SPK 3.5.4.")
T("b2_vent", "[SPK] Ventilation mecanique avec clapet coupe-feu (sortie existante reutilisee) + calfeutrement coupe-feu des passages", 3, "SPK", "go_pdb2_pose",
  LIM + " Travaux local B2 ; DPGF SPK 3.4.1.")
T("b2_det", "[SPK] Sonde de temperature + thermostat reportes en alarme, BAES, prolongation protection sprinkleur dans l'entree", 3, "SPK", "b2_vent", "DPGF SPK 3.4.1.")
T("b2_aff", "[SPK] Affichages d'exploitation et etiquetage local B2", 1, "SPK", "b2_det", "DPGF SPK 3.4.1.")
T("go_dalle_rest", "[GO] Restauration couche de forme, dalle portee, soubassement et cuvelage local GE + durcisseur de dalle", 4, "GO", "go_pdge_pose,t2_spk",
  "DPGF GO 5.8.5 ; " + LIM + " Travaux local GE.")

# ---------------------------------------------------------------- 10
S(1, "10. LOCAL SPRINKLEUR SOURCE A + POSTES")
T("la_perc", "[GO] Percement des voiles beton facade Nord : ventilation haute et basse + redressement des tableaux", 3, "GO", "ic_clot,go_vis,go_soumis", "DPGF GO 5.8.4 (m2) ; " + LIM + " Travaux local sprinkleur source A.")
T("la_grille", "[SPK] Fourniture et pose des grilles de ventilation haute et basse", 1, "SPK", "la_perc,spk_grilles", LIM + " 4.")
T("la_floc", "[SPK] Flocage de la toiture coupe-feu 1 h (local source A)", 3, "SPK", "ic_clot,spk_vis", LIM + " 4 ; DPGF SPK 3.4.1 (m2). Duree estimee.")
T("la_prot", "[SPK] Remplacement protection sprinkleur local A + postes (PC5 : CPE + vanne d'isolement, indicateur de passage d'eau), extension local eau glacee, gaine technique", 5, "SPK",
  "spk_vis,ic_prot", "DPGF SPK 3.4.1 ; CCTP SPK 3.6.1.")
T("la_det", "[SPK] Sonde de temperature reportee en alarme + contacts anti-intrusion (portes local sprinkleur, atelier, TGBT)", 3, "SPK", "la_prot", "DPGF SPK 3.4.1.")
T("la_arm", "[SPK] Armoire de repartition equipements annexes + disjoncteur depuis TGBT", 3, "SPK", "spk_elec,spk_vis", "DPGF SPK 3.4.1.")
T("la_aff", "[SPK] Affichages d'exploitation, etiquetage, BAPI, reprise peinture des canalisations du local", 3, "SPK", "la_prot", "DPGF SPK 3.4.1.")

# ---------------------------------------------------------------- 11
S(1, "11. SOURCES A / B1 / JOCKEY (apres remise en service de la source B2)")
T("sb1_dep", "[SPK] Depose electropompe source B1 + equipements et canalisations, consignation electricite, cables neutralises", 3, "SPK", "spk_vis,ic_prot", "DPGF SPK 3.5 (Source B1).")
T("sa_comp", "[SPK] Mise en place mesures compensatoires + raccordement provisoire pour coupure de la source A", 1, "SPK", "spk_msb2", LIM + " 2 : coupures de sources ; B2 doit etre revenue en service.")
T("sa_pompe", "[SPK] Remplacement electropompe source A (inclus nourrice pressostatique sources)", 3, "SPK", "sa_comp,spk_pompeA", "DPGF SPK 3.5 (Source A).")
T("sa_jock", "[SPK] Remplacement pompe jockey + alimentation d'aspiration sur eau de ville", 2, "SPK", "sa_comp,spk_pompeA", "DPGF SPK 3.5 (Pompe jockey).")
T("sa_tuy", "[SPK] Reprise tuyauteries aspiration et refoulement source A + vannes reportees en alarme", 3, "SPK", "sa_pompe", "DPGF SPK 3.5.")
T("sa_arm", "[SPK] Remplacement armoire pompe jockey & source A + disjoncteur + cables CR1 en amont coupure generale", 4, "SPK", "sa_comp,spk_elec", "DPGF SPK 3.5.")
T("sa_res", "[SPK] Reserve 30 m3 : remplissage manuel, plaque descriptive, remplacement contact de niveau + report alarme + test", 2, "SPK", "sa_comp", "DPGF SPK 3.5.")
T("sa_nour", "[SPK] Depose nourrice pressostatique (anciennes jockey, A, B1) + cables", 1, "SPK", "sa_pompe,sb1_dep", "DPGF SPK 3.5 (Nourrices).")
T("sa_canne", "[SPK] Nouvelle canne d'essai source A (vannes reportees en alarme)", 2, "SPK", "sa_tuy", "DPGF SPK 3.5 (Systemes d'essai).")
T("sa_seuil", "[SPK] Reglage des seuils de demarrage de chaque source (NF EN 12845)", 1, "SPK", "sa_pompe,b2_nour", "DPGF SPK 3.5 ; CCTP SPK 3.5.6.")
T("sa_ms", "[SPK] Remise en service source A + levee des mesures compensatoires", 1, "SPK", "sa_tuy,sa_arm,sa_res,sa_canne,sa_jock,sa_nour,sa_seuil", LIM + " 2.")

# ---------------------------------------------------------------- 12
S(1, "12. POSTES DE CONTROLE (apres retour des sources)")
for i in range(1, 8):
    prev = "sa_ms" if i == 1 else "pc%d" % (i - 1)
    T("pc%d" % i, "[SPK] Entretien triennal poste de controle PC%d (demontage, joints, clapet compensateur, essai reel point F)" % i, 2, "SPK", prev,
      "DPGF SPK 3.6.1. Un seul PC hors service a la fois ; reseau en eau chaque fin de semaine (CCTP 3.1.4). Duree estimee 2 j/PC.")
T("pc6m", "[SPK] PC6 : depose du vieux manometre + remplacement du pressostat", 1, "SPK", "pc6", "DPGF SPK 3.6.1.")
T("pc_vis", "[SPK] Controle visuel d'ecoulement sur essai des PC + remplacement des gongs hydrauliques par une nourrice commune", 3, "SPK", "pc7", "DPGF SPK 3.6.1.")
T("pc_byp", "[SPK] Bypass sur tous les postes de controle (7) avec vannes reportees en alarme", 7, "SPK", "pc7", "DPGF SPK 3.6.2. ~1 j/PC.")
T("pc_num", "[SPK] Numerotation vannes barrage/test/vidange + schemas a jour sur colonnes montantes", 2, "SPK", "pc_byp,pc_vis", "DPGF SPK 3.6.1 (Remarque Q1) ; CCTP SPK 3.6.1.")

# ---------------------------------------------------------------- 13
S(1, "13. ELECTRICITE, ALARMES, MISE A LA TERRE, PEINTURE (SPK)")
T("el_arm", "[SPK] Armoire electrique locale equipements sprinkleurs (asservissement et protection) dans le local source", 4, "SPK", "spk_elec,la_arm", "DPGF SPK 3.17.")
T("el_cab", "[SPK] Fourniture, installation et cablage de tous les equipements sprinkleurs du local source", 5, "SPK", "el_arm,b2_elec", "DPGF SPK 3.17.")
T("el_tab", "[SPK] Raccordement des alimentations electriques du tableau d'alarme", 2, "SPK", "el_cab", "DPGF SPK 3.17.")
T("el_terre", "[SPK] Tresses de mise a la terre des equipements sprinkleurs + nourrice des postes (raccord boucle de terre du radier)", 2, "SPK", "fd_terre,rs_equip,sa_tuy", LIM + " 3.")
T("al_rep", "[SPK] Report des alarmes creees (niveau reserve, vannes, temperatures, intrusion, CPE...)", 3, "SPK", "el_tab,el_cable,la_det,b2_det", "DPGF SPK 3.16.")
T("al_ver", "[SPK] Verification de toutes les alarmes, existantes et creees", 2, "SPK", "al_rep", "DPGF SPK 3.16.")
T("pt_peint", "[SPK] Peinture des reseaux apparents (y compris raccords mecaniques)", 3, "SPK", "sa_tuy,b2_tuy,la_aff", "DPGF SPK 3.18.")

# ---------------------------------------------------------------- 14
S(1, "14. ESSAIS, MISE EN SERVICE ET REMISE EN SERVICE B2 (SPK)")
T("es_epr", "[SPK] Epreuves hydrauliques des reseaux (locaux B2, cuve, canne d'essai)", 3, "SPK", "b2_tuy,rs_remp", "DPGF SPK 3.22 ; " + LIM + " 3 (essais hydrauliques = SPK).")
T("es_b2", "[SPK] Essais source B2 : GMPD (demarrage, debit 360 m3/h, pression), seuils, debitmetre, canne d'essai", 3, "SPK", "b2_elec,b2_nour,b2_debit,rs_remp,es_epr", "DPGF SPK 3.22.")
T("spk_msb2", "[SPK] REMISE EN SERVICE SOURCE B2 + levee des mesures compensatoires (retour a l'etat de protection)", 1, "SPK", "es_b2,b2_det,al_ver",
  "Jalon de fin d'indisponibilite de la source B2.")
T("es_ident", "[SPK] Identification du materiel et des reseaux (pochoir)", 3, "SPK", "pt_peint", "DPGF SPK 3.22.")
T("es_pc", "[SPK] Verifications, tests et controles des postes de controle, alarmes et points F", 3, "SPK", "pc_num,pc6m,al_ver", "DPGF SPK 3.22.")
T("es_src", "[SPK] Verifications et essais des differentes sources conservees (A, jockey)", 2, "SPK", "sa_ms", "DPGF SPK 3.22.")
T("es_rech", "[SPK] Pieces de rechange protection automatique incendie", 1, "SPK", "es_src", "DPGF SPK 3.22.")
T("es_q1", "[SPK] Levee des remarques du dernier rapport semestriel Q1 (+ remarques complementaires)", 3, "SPK", "es_pc,pt_peint,la_aff", "DPGF SPK 3.11. Duree estimee (provision 3 %).")
T("es_form", "[SPK] Mise en service, seance de formation et d'instruction exploitant", 2, "SPK", "es_pc,es_src,es_ident,es_rech", "DPGF SPK 3.22.")
T("es_doe", "[SPK] DOE lot sprinklage (plans de recolement, notices, PV d'essais)", 5, "SPK", "es_form,es_q1", "DPGF SPK 3.1.2 ; " + LIM + " 3 (DOE chacun pour son lot).")

# ---------------------------------------------------------------- 15
S(1, "15. BRISE-VUE : CHARPENTE, BARDAGE BOIS, PORTE (apres cuve et reseaux)")
T("bv_charp", "[GO/CM] Montage charpente metallique brise-vue (poteaux, pannes, contreventement) + scellement definitif des ancrages", 6, "GO",
  "rs_toit,rs_equip,go_charp,t1_remb", "DPGF GO 5.7.1 ; " + LIM + " 4. CCTP GO 1 : cuve et reseaux avant brise-vue.")
T("bv_ossat", "[GO/Bardage] Sous-construction du bardage (profils omega acier galvanise sur poteaux)", 4, "GO", "bv_charp", "DPGF GO 5.9.1 (m2). Duree estimee.")
T("bv_lames", "[GO/Bardage] Lames de bardage bois douglas a claire-voie (espacement 20 mm), coupes a 45 deg, saturateur", 8, "GO", "bv_ossat,go_bois", "DPGF GO 5.9.2 (m2). Hypothese ~40 m2/jour.")
T("bv_porte", "[GO] Pose porte d'acces cuve B2 (ferme-porte, barre anti-panique, serrure compatible site)", 1, "GO", "bv_ossat,go_porte", "DPGF GO 5.9.3.")

# ---------------------------------------------------------------- 16
S(1, "16. VOIRIES ET ESPACES VERTS - REMISE EN ETAT (VRD)")
T("vr_bord", "[VRD] Remise en place des bordures beton (joints resistants UV et hydrocarbures)", 1, "VRD", "t2_remb,ic_bord", "DPGF GO 5.10.3 (ml).")
T("vr_enr", "[VRD] Refection voie technique : reprofilage GNT 30 cm, geotextile cl.4, enrobe noir 5 cm au droit des reseaux", 4, "VRD", "vr_bord,t1_remb", "DPGF GO 5.10.4 (m2) ; " + LIM + " 6.")
T("vr_pist", "[VRD] Depose des pistes d'acces chantier + evacuation + reprofilage", 2, "VRD", "bv_lames,bv_porte,eu_remb,go_dalle_rest", "CCTP GO 5.3.3.")
T("vr_terre", "[VRD] Mouvements de terres, nivellement espaces verts + apport terre vegetale 0,30 m mini", 3, "VRD", "vr_pist", LIM + " 6.")
T("vr_prep", "[VRD] Preparation avant engazonnement (nettoyage, rotavator 0,20 m, amendements, reglage)", 2, "VRD", "vr_terre", "DPGF GO 5.10.1.")
T("vr_semis", "[VRD] Engazonnement (semis 3 kg/are, roulage, ratissage) - plantations gazon", 2, "VRD", "vr_prep", "DPGF GO 5.10.2 (m2). Controle a 1 mois / tonte a 15 j hors planning.")
T("vr_chem", "[VRD] Refection des cheminements de chantier", 2, "VRD", "vr_pist", LIM + " 6.")
T("vr_cur", "[VRD] Curage + controle camera des reseaux EU en fin de travaux", 1, "VRD", "eu_remb,vr_pist", LIM + " 5.")

# ---------------------------------------------------------------- 17
S(1, "17. FIN DE CHANTIER, DOE, RECEPTION PHASE 1")
T("fin_hui", "[GO] Constat d'huissier contradictoire de fin de travaux", 1, "GO", "vr_semis,vr_chem,vr_enr,vr_cur", "DPGF GO 5.1.1 ; CCTP GO 5.1.1.")
T("go_doe", "[GO] DOE lot GO/VRD : recolement ouvrages enterres, PV essais beton/pieux, fiches techniques", 5, "GO", "fin_hui,fd_essais", "Limites : DOE chacun pour son lot ; CCTP GO 2.3.7.")
T("fin_repli", "[SPK] Nettoyage + repli du chantier : base vie, cloture, armoire de chantier, raccordements", 3, "SPK", "es_form,fin_hui,vr_pist", LIM + " 1 / 2.")
T("fin_opr", "[MOA/MOE] Operations prealables a la reception (OPR) Phase 1", 2, "MOA", "es_doe,go_doe,fin_repli", "Duree estimee.")
T("m_fin", "FIN PHASE 1 - Reception des travaux", 0, "MOA", "fin_opr", "")

# ---------------------------------------------------------------- 18  Hamacs transverses
S(1, "18. PRESTATIONS TRANSVERSES (hamacs - durees calees sur les taches liees)")
SPAN("hm_port", "[GO] Gestion des portails / acces de chantier (ouverture, fermeture, surveillance)", "GO", "ic_clot", "fin_hui", LIM + " 1 : GO phase 1 ; CCTP GO 5.1.3.")
SPAN("hm_abords", "[GO] Entretien et nettoyage des abords, acces et voies (permanent)", "GO", "ic_clot", "fin_hui", "DPGF GO 5.1.11 ; CCTP GO 5.1.11.")
SPAN("hm_homme_go", "[GO/VRD] Homme trafic (voie pompier, arrivees/departs camions) - phases demolition a remise en etat", "GO", "dm_brise", "vr_pist",
     "DPGF GO 5.1.12 ; " + LIM + " 2 (chacun pour son lot).")
SPAN("hm_homme_spk", "[SPK] Homme trafic - livraisons cuve, GMPD, fonte, levage", "SPK", "rs_livr", "b2_gmpd", LIM + " 2.")
SPAN("hm_enc", "[SPK] Encadrement de chantier + location nacelle / bungalow / container", "SPK", "ic_clot", "fin_repli", "DPGF SPK Frais de chantier / 3.1.2.")
SPAN("hm_bennes", "[GO] Bennes de chantier + evacuation gravats (part du lot)", "GO", "dm_brise", "vr_pist", "DPGF GO 5.1.10.")
