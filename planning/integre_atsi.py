# -*- coding: utf-8 -*-
# Remplace les interventions ATSI d'un planning MS Project (.mpp) par les lignes du planning ATSI (semaines respectees : debut au plus tot),
# relie les taches EIFFAGE a ces lignes, recalcule les dates, ecrit un MSPDI (XML).
# usage : python3 -I integre_atsi.py entree.mpp sortie.xml
import sys, os, re, json, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jpype, jpype.imports, mpxj
if not jpype.isJVMStarted(): jpype.startJVM()
from org.mpxj import Duration, TimeUnit, Relation, RelationType, TaskMode, ConstraintType
from org.mpxj.reader import UniversalProjectReader
from org.mpxj.writer import UniversalProjectWriter, FileFormat
from java.time import LocalDateTime
from mpp_engine import working_days, reschedule

inp, outp = sys.argv[1], sys.argv[2]
p = UniversalProjectReader().read(inp)
O = {t.getID().intValue(): t for t in p.getTasks() if t.getID() is not None}
root = O[0]
WD = working_days(p.getDefaultCalendar(), dt.date(2026, 10, 1), 600)
def days(n): return Duration.getInstance(n, TimeUnit.DAYS)
def ldt(d, h=8): return LocalDateTime.of(d.year, d.month, d.day, h, 0)
TY = {"FS": RelationType.FINISH_START, "SS": RelationType.START_START, "FF": RelationType.FINISH_FINISH}

# ------------------------------------------------------------------ 1. tâches ATSI à retirer (lot "SPK")
ATSI_OLD = [t for i, t in O.items() if i != 0 and not t.hasChildTasks() and str(t.getText(1) or "") == "SPK"]
OLD_IDS = {t.getID().intValue() for t in ATSI_OLD}
OLD_NAMES = {t.getID().intValue(): str(t.getName()) for t in ATSI_OLD}

# ------------------------------------------------------------------ 2. liaisons EIFFAGE (avant création des nouvelles tâches)
N = {}; SPEC = []
def R(x): return N[x] if isinstance(x, str) else O[x]
def setpreds(t, specs):
    for r in list(t.getPredecessors()): t.removePredecessor(r.getPredecessorTask(), r.getType(), r.getLag())
    for sp in specs:
        x = sp[0]; ty = sp[1] if len(sp) > 1 else "FS"; lag = sp[2] if len(sp) > 2 else 0
        t.addPredecessor(Relation.Builder().predecessorTask(R(x)).type(TY[ty]).lag(days(lag)))
UIDN = [max(t.getUniqueID().intValue() for t in p.getTasks() if t.getUniqueID() is not None) + 1]
def nuid(t): t.setUniqueID(jpype.JInt(UIDN[0])); UIDN[0] += 1

def iso_monday(week):                       # S43..S53 -> 2026 ; S1..S20 -> 2027
    y = 2026 if week >= 43 else 2027
    return dt.date.fromisocalendar(y, week, 1)
def bar(w1, w2):                            # duree = jours ouvres du lundi de w1 au vendredi de w2 (calendrier du projet)
    a = iso_monday(w1); b = iso_monday(w2) + dt.timedelta(4)
    return a, sum(1 for d in WD if a <= d <= b)
SRC = "Planning ATSI (ind. A, reçu le 20/10/2026), "
def atsi(key, parent, name, w1, w2, preds, before=None, extra=""):
    a, n = bar(w1, w2)
    t = parent.addTask()
    if before is not None: parent.removeChildTask(t); parent.addChildTaskBefore(t, before)
    t.setName(name); nuid(t); t.setText(1, "SPK"); t.setTaskMode(TaskMode.AUTO_SCHEDULED); t.setDuration(days(n))
    t.setConstraintType(ConstraintType.START_NO_EARLIER_THAN); t.setConstraintDate(ldt(max(a, dt.date(2026, 10, 26)), 8))
    t.setNotes("Source / hypothèse : " + SRC + ("semaine S%d" % w1 if w1 == w2 else "semaines S%d à S%d" % (w1, w2)) + " (%s au %s), %d jours ouvrés. Début au plus tôt = semaine d'ATSI ; décalé si une liaison l'impose.%s" % (a.strftime("%d/%m/%Y"), (iso_monday(w2) + dt.timedelta(4)).strftime("%d/%m/%Y"), n, (" " + extra) if extra else ""))
    N[key] = t; SPEC.append((key, preds)); return t

# chapitre 0 : prise en charge, études, achats (avant le chantier)
c0 = root.addTask(); root.removeChildTask(c0); root.addChildTaskBefore(c0, O[1]); nuid(c0)
c0.setName("0. ATSI - PRISE EN CHARGE, ÉTUDES ET ACHATS (avant démarrage du chantier)")
c0.setNotes("Lignes du planning ATSI du 15/06/2026 (ind. A) : semaines respectées. La ligne « récolement et DOE (vérification TQC) » n'a pas de barre dans le planning ATSI : non reprise.")
ETU = [
 ("e1", "[ATSI] Prise en charge : vérification concordance pièce marché / pièce A.O", 44, 44),
 ("e2", "[ATSI] Prise en charge : déclaration de l'affaire au service sécurité", 45, 45),
 ("e3", "[ATSI] Prise en charge : vérification des données sur site", 46, 46),
 ("e4", "[ATSI] Prise en charge : calculs de détermination des pompes / réserves", 46, 46),
 ("e5", "[ATSI] Études : plan de risques / plan de zones", 47, 47),
 ("e6", "[ATSI] Études : schémas de principe", 47, 47),
 ("e7", "[ATSI] Études : élaboration PPSPS / PDP", 47, 47),
 ("e8", "[ATSI] Études : visite d'inspection Commune (ATSI / sous-traitant)", 46, 47),
 ("e9", "[ATSI] Études : relevé sur site", 46, 49),
 ("e10", "[ATSI] Études : plans de protection", 48, 49),
 ("e11", "[ATSI] Études : plans d'ensemble", 48, 49),
 ("e12", "[ATSI] Études : validation de l'étude / assureur", 50, 50),
 ("e13", "[ATSI] Études : fiches techniques", 50, 50),
 ("e14", "[ATSI] Études : isos / nomenclatures", 50, 50),
 ("e15", "[ATSI] Études : notes de calcul de vérification", 50, 50),
 ("e16", "[ATSI] Achats (consultation / ordre / livraison) : sources d'eau", 51, 51),
 ("e17", "[ATSI] Achats (consultation / ordre / livraison) : tubes / supportage", 51, 51),
 ("e18", "[ATSI] Achats (consultation / ordre / livraison) : accessoires de montage", 51, 51),
]
for k, nm, a, b in ETU: atsi(k, c0, nm, a, b, [])

# chapitre 2 : montage ATSI (remplace l'ancien chapitre « source A + postes »)
c2 = O[7]
c2.setName("2. ATSI - MONTAGE (planning ATSI : semaines respectées, début au plus tôt)")
c2.setNotes("Les tâches ATSI de ce chapitre sont celles du planning ATSI du 15/06/2026 (ind. A). Chaque ligne ATSI est une tâche unique, à la durée du planning ATSI. "
            "Les tâches EIFFAGE liées à ATSI sont reliées au début ou à la fin de ces lignes (voir les liaisons dans le fichier).")
atsi("m9", c2, "[ATSI] Électricité et alarmes (phase 1)", 3, 3, [])
atsi("m1", c2, "[ATSI] Local sprinkler source A et postes", 4, 6, [(12,)], extra="Après le percement des voiles par EIFFAGE (ventilation).")
atsi("m2", c2, "[ATSI] Local sprinkler source B2", 4, 4, [])
atsi("m3", c2, "[ATSI] Source A et pompe jockey", 5, 6, [])
atsi("m4", c2, "[ATSI] Source B1", 7, 9, [("m3",)])
atsi("m5", c2, "[ATSI] Source B2 (consignation, vidange, déposes cuve et GMPD)", 10, 11, [("m3",), (25,)], extra="Après la remise en service de la source A (GN13) et le dévoiement incendie EIFFAGE.")
atsi("m6", c2, "[ATSI] Réseau enterré (réseaux des tranchées, cuve sur le radier EIFFAGE)", 12, 15, [(57,), (71,), (79,), (73,)], extra="Après le durcissement du radier et l'ouverture des tranchées (fourreaux posés) par EIFFAGE.")
atsi("m7", c2, "[ATSI] Divers travaux système d'essai, nourrice pressostatique", 15, 15, [("m5",)])
atsi("m8", c2, "[ATSI] Postes de contrôle existants et by-pass", 16, 16, [("m5",)])
atsi("m10", c2, "[ATSI] Électricité et alarmes (phase 2)", 16, 16, [("m6",)])

# chapitre 11 : essais et réception ATSI
c11 = root.addTask(); nuid(c11)
c11.setName("11. ATSI - ESSAIS ET RÉCEPTION")
for k, nm, w, pr in [("x1", "[ATSI] Essais : essais d'étanchéité des réseaux", 17, [("m6",), ("m8",), ("m10",)]),
                     ("x2", "[ATSI] Essais : rinçage des réseaux (par bâtiments)", 17, [("m6",), ("m8",), ("m10",)]),
                     ("x3", "[ATSI] Essais : essais des alarmes (avec le sous-traitant)", 17, [("m6",), ("m8",), ("m10",)]),
                     ("r1", "[ATSI] Réception : prévisite et opérations préalables à la réception", 18, [("x1",), ("x2",), ("x3",)]),
                     ("r2", "[ATSI] Réception : réception client / organisme vérificateur", 18, [("x1",), ("x2",), ("x3",)]),
                     ("r3", "[ATSI] Réception : revue de fin d'affaire", 18, [("x1",), ("x2",), ("x3",)])]:
    atsi(k, c11, nm, w, w, pr)

# ------------------------------------------------------------------ 3. relier les tâches EIFFAGE aux lignes ATSI
RELINK = {
 6:  [(2,)],                                   # dépose bordures : était après la clôture ATSI (retirée)
 28: [(25,), ("m5", "SS", 2)],                 # dépose réseaux enterrés : après la vidange (2 j en début de ligne B2)
 35: [(30,), (25,), ("m5", "SS", 6)],          # démolition radier : après dépose brise-vue et dépose cuve (vidange 2 j + cuve 4 j)
 38: [("m5", "SS", 4)],                        # dépose pièces de scellement B2 : après dépose GMPD
 39: [(38,), ("m4",)],                         # démolition dalle GE : après B1 déposée
 54: [(52,), ("e16",)],                        # aspiration sous radier : fournitures ATSI livrées (achats)
 59: [(38,), ("e16",)],                        # pose pièces de scellement B2
 60: [(40,), ("e16",)],                        # pose pièce de scellement GE
 68: [(60,), (61,), ("m6",)],                  # restauration dalle GE : après pose refoulement (réseau enterré)
 75: [(73,), ("m6",)],                         # raccordement EU : après le réseau EU aérien ATSI (ligne réseau enterré)
 77: [(71,), (76,), ("m6",)],                  # remblaiement tranchée 1 : après pose ATSI
 78: [(71,)],                                  # réouverture tranchée 2 : plus derrière le remblaiement de la tranchée 1 (évite un cycle avec la ligne ATSI)
 83: [(79,), ("m6",)],                         # remblaiement tranchée 2 : après pose ATSI
 93: [("m6",)],                                # charpente brise-vue : après la cuve et les réseaux (ligne réseau enterré)
}
BEFORE = {i: [(r.getPredecessorTask().getID().intValue(), str(r.getType())[:2]) for r in O[i].getPredecessors()] for i in RELINK}
for i, specs in RELINK.items(): pass
# attention : les liaisons avec les nouvelles tâches (clés texte) ne peuvent être posées qu'une fois les tâches créées -> déjà créées ci-dessus
for i, specs in RELINK.items(): setpreds(O[i], specs)
for key, preds in SPEC:
    if preds: setpreds(N[key], preds)

# audit : tâches EIFFAGE qui avaient une liaison vers une tâche ATSI retirée et qui n'ont pas été reliées
lost = []
for t in p.getTasks():
    if t.getID() is None or t.getID().intValue() in OLD_IDS or t.getID().intValue() in RELINK: continue
    for r in t.getPredecessors():
        if r.getPredecessorTask().getID().intValue() in OLD_IDS: lost.append((str(t.getName())[:70], OLD_NAMES[r.getPredecessorTask().getID().intValue()][:60]))
# retrait des tâches ATSI d'origine (leurs liaisons restantes sont supprimées)
for t in ATSI_OLD:
    for r in list(t.getPredecessors()): t.removePredecessor(r.getPredecessorTask(), r.getType(), r.getLag())
for t in p.getTasks():
    if t.getID() is None: continue
    for r in list(t.getPredecessors()):
        if r.getPredecessorTask().getID() is not None and r.getPredecessorTask().getID().intValue() in OLD_IDS:
            t.removePredecessor(r.getPredecessorTask(), r.getType(), r.getLag())
for t in ATSI_OLD: t.remove()

# chapitres devenus vides (ex. « cuve ») : retirés ; renumérotation continue des chapitres 1..n
EMPTY = [c for c in list(root.getChildTasks()) if not c.hasChildTasks()]
EMPTY_NAMES = [str(c.getName()) for c in EMPTY]
for c in EMPTY: c.remove()
n = 0
for c in root.getChildTasks():
    nm = str(c.getName())
    if re.match(r"^\d+\.\s", nm) and not nm.startswith("0. "):
        n += 1; c.setName(re.sub(r"^\d+\.\s", "%d. " % n, nm))

# début du projet : la première ligne ATSI est S44 (26/10/2026) ; EIFFAGE démarre toujours le 02/11/2026
p.getProjectProperties().setStartDate(ldt(dt.date(2026, 10, 26), 8))
first = next(t for t in p.getTasks() if t.getName() is not None and str(t.getName()).startswith("[EIFFAGE] Constat d'huissier"))
first.setConstraintType(ConstraintType.START_NO_EARLIER_THAN); first.setConstraintDate(ldt(dt.date(2026, 11, 2), 8))

# numérotation des chapitres (0, 1, 2, ... 10 inchangés ; 11 = ATSI essais/réception)
p.getTasks().synchronizeTaskIDToHierarchy(); p.updateStructure()

# ------------------------------------------------------------------ 4. ordonnancement
res, info, idx = reschedule(p, WD)
for tid, (sd, fd) in res.items():
    t = info[tid]["t"]
    if info[tid]["dur"] == 0: t.setStart(ldt(WD[fd], 17)); t.setFinish(ldt(WD[fd], 17))
    else: t.setStart(ldt(WD[sd], 8)); t.setFinish(ldt(WD[fd], 17))
def dd(x): return dt.date(x.getYear(), x.getMonthValue(), x.getDayOfMonth())
def roll(t):
    if not t.hasChildTasks(): return idx[dd(t.getStart())], idx[dd(t.getFinish())]
    r = [roll(c) for c in t.getChildTasks()]; a, b = min(x[0] for x in r), max(x[1] for x in r)
    t.setStart(ldt(WD[a], 8)); t.setFinish(ldt(WD[b], 17)); t.setDuration(days(b - a + 1)); return a, b
a, b = roll(root)
p.getProjectProperties().setFinishDate(ldt(WD[b], 17))
UniversalProjectWriter(FileFormat.MSPDI).write(p, outp)

# ------------------------------------------------------------------ 5. rapport
D = lambda x: x.strftime("%d/%m/%Y")
sf = lambda t: dd(t.getStart()); ff = lambda t: dd(t.getFinish())
print("tâches:", p.getTasks().size() - 1, "| ATSI retirées:", len(ATSI_OLD), "| ajoutées:", len(N), "| projet", D(sf(root)), "→", D(ff(root)))
print("\n-- lignes ATSI : semaine prévue / dates obtenues --")
for k, t in N.items():
    wk_start = ldt(dd(t.getConstraintDate()))
    pushed = dd(t.getStart()) > dd(t.getConstraintDate())
    print("%-3s %-72s prévu %s  obtenu %s → %s %s" % (k, str(t.getName())[7:79], D(dd(t.getConstraintDate())), D(sf(t)), D(ff(t)), "<< DÉCALÉ" if pushed else ""))
fin = next(t for t in p.getTasks() if t.getName() is not None and str(t.getName()) == "FIN DES TRAVAUX EIFFAGE")
print("\nFIN DES TRAVAUX EIFFAGE :", D(ff(fin)), "| 15 semaines depuis le 02/11/2026 = 12/02/2027")
print("liaisons EIFFAGE perdues (à vérifier):", lost, "| chapitres vides retirés:", EMPTY_NAMES)
json.dump({"relink": {str(i): BEFORE[i] for i in BEFORE}, "old": OLD_NAMES}, open(outp + ".audit.json", "w"), ensure_ascii=False)
