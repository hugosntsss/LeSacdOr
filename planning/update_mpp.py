# -*- coding: utf-8 -*-
# Ajoute les interventions ATSI (lot sprinklage) manquantes dans un planning MS Project (.mpp), en suivant l'ordre du calendrier previsionnel.
# usage : python3 -I update_mpp.py entree.mpp sortie.xml
import sys, os, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jpype, jpype.imports, mpxj
if not jpype.isJVMStarted(): jpype.startJVM()
from org.mpxj import Duration, TimeUnit, Relation, RelationType, TaskMode
from org.mpxj.reader import UniversalProjectReader
from org.mpxj.writer import UniversalProjectWriter
from org.mpxj.writer import FileFormat
from java.time import LocalDateTime
from mpp_engine import working_days, reschedule

inp, outp = sys.argv[1], sys.argv[2]
p = UniversalProjectReader().read(inp)
O = {t.getID().intValue(): t for t in p.getTasks() if t.getID() is not None}   # ID d'origine -> tache
root = O[0]
N = {}; SPEC = []
UID = [max(t.getUniqueID().intValue() for t in p.getTasks() if t.getUniqueID() is not None) + 1]
def nuid(t):
    t.setUniqueID(jpype.JInt(UID[0])); UID[0] += 1

def days(n): return Duration.getInstance(n, TimeUnit.DAYS)
def pred(task, ptask, typ="FS", lag=0):
    ty = {"FS": RelationType.FINISH_START, "SS": RelationType.START_START, "FF": RelationType.FINISH_FINISH}[typ]
    task.addPredecessor(Relation.Builder().predecessorTask(ptask).type(ty).lag(days(lag)))

def R(x): return N[x] if isinstance(x, str) else O[x]

def chapter(key, name, before=None):
    s = root.addTask()
    if before is not None:
        root.removeChildTask(s); root.addChildTaskBefore(s, O[before])
    s.setName(name); nuid(s); N[key] = s
    return s

def add(key, parent, name, dur, preds, src, before=None, lot="SPK"):
    t = parent.addTask()
    if before is not None:
        parent.removeChildTask(t); parent.addChildTaskBefore(t, O[before])
    t.setName(name); nuid(t); t.setText(1, lot); t.setDuration(days(dur)); t.setTaskMode(TaskMode.AUTO_SCHEDULED)
    t.setNotes("Source / hypothèse : " + src)
    N[key] = t
    SPEC.append((key, preds))
    return t

PREV = "Ordre repris du calendrier prévisionnel (lot SPK) - "
# ------------------------------------------------------------------ chapitre : SOURCE A + POSTES DE CONTROLE (avant la consignation de la B2)
cA = chapter("cA", "2. SOURCE A + POSTES DE CONTRÔLE - REMISE EN SERVICE AVANT CONSIGNATION DE LA B2 (ATSI)", before=7)
add("a1", cA, "[ATSI] Consignation source A + mesures compensatoires / raccordement provisoire (la B2 reste en service)", 1, [(3, "SS", 1)], PREV + "n° 29 Consignation source A ; CCTP SPK 3.1.4 ; tableau de limites 2.")
add("a2", cA, "[ATSI] Remplacement de l'électropompe source A (inclus nourrice pressostatique des sources)", 3, [("a1",)], PREV + "n° 30 ; DPGF SPK 3.5 (Source A). Durée estimée.")
add("a3", cA, "[ATSI] Remplacement de la pompe jockey + alimentation d'aspiration sur eau de ville", 2, [("a1",)], PREV + "n° 30 ; DPGF SPK 3.5 (Pompe jockey). Durée estimée.")
add("a4", cA, "[ATSI] Remplacement de l'armoire pompe jockey et source A + disjoncteur + câbles CR1 depuis le TGBT", 3, [("a1",)], "DPGF SPK 3.5 (Source A). Durée estimée.")
add("a5", cA, "[ATSI] Réserve source A (30 m³) : remplissage manuel, plaque descriptive, contact de niveau + report d'alarme", 1, [("a1",)], "DPGF SPK 3.5 (Réserve d'eau). Durée estimée.")
add("a6", cA, "[ATSI] Reprise des tuyauteries d'aspiration et de refoulement source A + vannes reportées en alarme", 2, [("a2",)], "DPGF SPK 3.5 (Source A). Durée estimée.")
add("a7", cA, "[ATSI] Nouvelle canne d'essai source A (vannes reportées en alarme)", 1, [("a6",)], "DPGF SPK 3.5 (Systèmes d'essai).")
add("a8", cA, "[ATSI] Travaux des postes de contrôle : entretien triennal des 7 postes (un seul poste hors service à la fois)", 5, [("a1",)], PREV + "n° 31 Travaux postes de contrôle (10 jours au total) ; DPGF SPK 3.6.1. Réseau en eau chaque fin de semaine.")
add("a9", cA, "[ATSI] Postes de contrôle : bypass sur les 7 postes + vannes reportées en alarme", 3, [("a8",)], "DPGF SPK 3.6.2.")
add("a10", cA, "[ATSI] Postes de contrôle : contrôle visuel d'écoulement, gongs remplacés par une nourrice commune, manomètre et pressostat du PC6", 2, [("a8",)], "DPGF SPK 3.6.1.")
add("a11", cA, "[ATSI] Postes de contrôle : numérotation des vannes de barrage/test/vidange + schémas à jour sur colonnes montantes", 2, [("a9",), ("a10",)], "DPGF SPK 3.6.1 ; CCTP SPK 3.6.1.")
add("a12", cA, "[ATSI] MISE EN SERVICE ET ESSAI SOURCE A + levée des mesures compensatoires - AVANT consignation de la B2", 1,
    [("a2",), ("a3",), ("a4",), ("a5",), ("a6",), ("a7",)], PREV + "n° 32 Mise en service et essai source A. Les postes de contrôle (a8 à a11) tournent en parallèle sans conditionner la vidange de la B2.")

# ------------------------------------------------------------------ dépose B1 (apres dépose du GMPD B2, comme au previsionnel)
add("d1", O[12], "[ATSI] Dépose de la source B1 (électropompe + équipements/canalisations, consignation électrique, câbles neutralisés)", 2, [(15,)], PREV + "n° 36 Dépose source B1 (après n° 35 dépose source B2) ; DPGF SPK 3.5 (Source B1).", before=17)
add("d2", O[12], "[ATSI] Dépose de la nourrice pressostatique (anciennes jockey, A, B1) + câbles", 1, [("d1",)], "DPGF SPK 3.5 (Nourrices pressostatiques).", before=17)

# ------------------------------------------------------------------ local B2 (GMPD et équipements associes)
bef = 46
add("b1", O[41], "[ATSI] Réservoir fuel double peau 500 L + pistolet de remplissage (local B2)", 1, [(45,)], PREV + "n° 37 Travaux local source B2 (GMPD et équipements associés) ; DPGF SPK 3.5.", before=bef)
add("b2", O[41], "[ATSI] Armoire de commande/démarrage du GMPD + câblage + raccordement à l'armoire générale", 3, [(45,)], "DPGF SPK 3.17 ; CCTP SPK 3.5.4. Durée estimée.", before=bef)
add("b3", O[41], "[ATSI] Nourrice pressostatique source B2 + pressostats", 1, [(45,)], "DPGF SPK 3.5 (Nourrices pressostatiques).", before=bef)
add("b4", O[41], "[ATSI] Tuyauterie de la canne d'essai DN150 (refoulement GMPD → pièce de scellement) + étalonnage du débitmètre", 2, [(45,)], "DPGF SPK 3.5 (Systèmes d'essai).", before=bef)
add("b5", O[41], "[ATSI] Ventilation mécanique + clapet coupe-feu (sortie existante réutilisée) + calfeutrement coupe-feu des passages", 2, [(42,)], "DPGF SPK 3.4.1 ; tableau de limites 4 (calfeutrement coupe-feu = SPK).", before=bef)
add("b6", O[41], "[ATSI] Sonde de température + thermostat reportés en alarme, BAES, protection sprinkleur de l'entrée, affichages du local B2", 2, [("b5",)], "DPGF SPK 3.4.1.", before=bef)

# ------------------------------------------------------------------ réseaux enterrés : suite SPK
add("r1", O[56], "[ATSI] Remplacement du réseau aérien DN200 de l'arrivée enterrée jusqu'à la nourrice des postes (local A)", 3, [(63,)], PREV + "n° 39 Pose réseaux enterrés SPK ; DPGF SPK 3.5 (Réseaux enterrés).", before=64)
add("r2", O[56], "[ATSI] Tirage des câbles TGBT → pénétration et reports d'alarme dans les fourreaux d'EIFFAGE", 3, [(58,), (62,)], "Tableau de limites 5 (Électricité) ; DPGF SPK 3.17.", before=64)

# ------------------------------------------------------------------ cuve : clapet EA avant remplissage
add("c1", O[69], "[ATSI] Clapet anti-pollution type EA sur l'arrivée eau de ville DN65 + vers EU + vanne de contre-barrage", 1, [(71,)], "DPGF SPK 3.5 (Systèmes d'essai). Nécessaire au remplissage de la cuve.", before=72)

# ------------------------------------------------------------------ nouveaux chapitres en fin de planning
cE = chapter("cE", "10. ÉLECTRICITÉ, ALARMES, MISE À LA TERRE ET PEINTURE (ATSI)")
add("e1", cE, "[ATSI] Armoire électrique du local source + câblage des équipements sprinkleurs + raccordement du tableau d'alarme", 5, [(51,)], "DPGF SPK 3.17. Durée estimée.")
add("e2", cE, "[ATSI] Tresses de mise à la terre des équipements + nourrice des postes (raccord à la boucle de terre du radier EIFFAGE)", 2, [(33,), (72,)], "DPGF SPK 3.17 ; tableau de limites 3.")
add("e3", cE, "[ATSI] Report des alarmes créées + vérification de toutes les alarmes", 3, [("e1",), ("b6",), (54,)], "DPGF SPK 3.16.")
add("e4", cE, "[ATSI] Peinture des réseaux apparents (raccords mécaniques compris)", 3, [("a6",), (52,), ("r1",)], "DPGF SPK 3.18.")
cF = chapter("cF", "11. ESSAIS, MISE EN SERVICE ET DOE (ATSI)")
add("f1", cF, "[ATSI] Réglage des seuils de démarrage des sources (NF EN 12845) + essais des sources conservées", 2, [(75,)], PREV + "n° 40 Mise en service et essai source B2 ; DPGF SPK 3.5 et 3.22.")
add("f2", cF, "[ATSI] Identification du matériel et des réseaux (pochoir) + étiquetage", 2, [("e4",)], "DPGF SPK 3.22 ; CCTP SPK 3.19.")
add("f3", cF, "[ATSI] Vérifications, tests et contrôles des postes de contrôle, alarmes et points F", 3, [("a11",), ("e3",)], "DPGF SPK 3.22.")
add("f4", cF, "[ATSI] Levée des remarques du dernier rapport semestriel Q1 (+ remarques complémentaires)", 3, [("f3",)], "DPGF SPK 3.11. Durée estimée.")
add("f5", cF, "[ATSI] Mise en service, séance de formation et d'instruction + pièces de rechange", 2, [("f1",), ("f2",), ("f3",)], "DPGF SPK 3.22.")
add("f6", cF, "[ATSI] DOE du lot sprinklage (plans de récolement, notices, PV d'essais)", 4, [("f4",), ("f5",)], "DPGF SPK 3.1.2 ; tableau de limites 3 (DOE chacun pour son lot).")
add("f7", cF, "[ATSI] Nettoyage + repli de la base vie et de la clôture ATSI", 2, [("f5",)], "Tableau de limites 1 et 2.")

# ------------------------------------------------------------------ liaisons
for key, preds in SPEC:
    for pr in preds:
        x = pr[0]; typ = pr[1] if len(pr) > 1 else "FS"; lag = pr[2] if len(pr) > 2 else 0
        pred(N[key], R(x), typ, lag)
pred(O[11], N["a12"])                                   # la B2 n'est consignée qu'après remise en service de la source A
pred(O[74], N["c1"])                                    # remplissage de la cuve : clapet EA posé
for k in ("b2", "b3", "b4", "b6", "r1"): pred(O[75], N[k])   # remise en service B2 : équipements du local et réseau aérien

# ------------------------------------------------------------------ numérotation des chapitres, ID, structure
import re
n = 0
for c in root.getChildTasks():
    nm = str(c.getName())
    if re.match(r"^\d+\.\s", nm):
        n += 1; c.setName(re.sub(r"^\d+\.\s", "%d. " % n, nm))
p.getTasks().synchronizeTaskIDToHierarchy(); p.updateStructure()

# ------------------------------------------------------------------ ordonnancement
WD = working_days(p.getDefaultCalendar())
res, info, idx = reschedule(p, WD)
def ldt(d, h): return LocalDateTime.of(d.year, d.month, d.day, h, 0)
for tid, (sd, fd) in res.items():
    t = info[tid]["t"]
    if info[tid]["dur"] == 0: t.setStart(ldt(WD[fd], 17)); t.setFinish(ldt(WD[fd], 17))
    else: t.setStart(ldt(WD[sd], 8)); t.setFinish(ldt(WD[fd], 17))
def roll(t):
    if not t.hasChildTasks(): return idx[t.getStart().toLocalDate() if False else dt.date(t.getStart().getYear(), t.getStart().getMonthValue(), t.getStart().getDayOfMonth())], idx[dt.date(t.getFinish().getYear(), t.getFinish().getMonthValue(), t.getFinish().getDayOfMonth())]
    ss, ff = [], []
    for c in t.getChildTasks():
        a, b = roll(c); ss.append(a); ff.append(b)
    a, b = min(ss), max(ff)
    t.setStart(ldt(WD[a], 8)); t.setFinish(ldt(WD[b], 17)); t.setDuration(days(b - a + 1))
    return a, b
a, b = roll(root)
p.getProjectProperties().setFinishDate(ldt(WD[b], 17))
UniversalProjectWriter(FileFormat.MSPDI).write(p, outp)

# ------------------------------------------------------------------ rapport
def D(t): s = t.getFinish(); return "%02d/%02d/%04d" % (s.getDayOfMonth(), s.getMonthValue(), s.getYear())
def S(t): s = t.getStart(); return "%02d/%02d/%04d" % (s.getDayOfMonth(), s.getMonthValue(), s.getYear())
byname = lambda frag: next(t for t in p.getTasks() if t.getName() is not None and frag in str(t.getName()))
print("tâches:", p.getTasks().size() - 1, "| début", S(root), "| fin projet (ATSI compris)", D(root))
for f in ["MISE EN SERVICE ET ESSAI SOURCE A", "Consignation + VIDANGE", "Essais + REMISE EN SERVICE", "FIN DES TRAVAUX EIFFAGE", "DOE du lot sprinklage", "Nettoyage + repli"]:
    t = byname(f); print("%-38s %s → %s" % (f, S(t), D(t)))
fin = byname("FIN DES TRAVAUX EIFFAGE"); fd = idx[dt.date(fin.getFinish().getYear(), fin.getFinish().getMonthValue(), fin.getFinish().getDayOfMonth())]
print("fin EIFFAGE : jour ouvré n°", fd + 1, "| limite 15 semaines = 12/02/2027 (jour ouvré n°", idx[dt.date(2027, 2, 12)] + 1, ")")
import json
rows = []
for k, t in N.items():
    if k in ("cA", "cE", "cF"): continue
    rows.append((int(t.getID()), str(t.getName()), str(t.getDuration()), S(t), D(t), ";".join("%d%s%s" % (r.getPredecessorTask().getID().intValue(), str(r.getType())[:2], "" if float(r.getLag().getDuration()) == 0 else "+%gj" % float(r.getLag().getDuration())) for r in t.getPredecessors()), str(t.getNotes())))
json.dump(rows, open(outp + ".added.json", "w"), ensure_ascii=False)
