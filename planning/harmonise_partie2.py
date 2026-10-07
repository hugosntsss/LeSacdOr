# -*- coding: utf-8 -*-
# Reprend et harmonise le chapitre 2 (source A / local sprinkleur / postes de controle) d'un planning MS Project.
# usage : python3 -I harmonise_partie2.py entree.mpp sortie.xml
import sys, os, re, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jpype, jpype.imports, mpxj
if not jpype.isJVMStarted(): jpype.startJVM()
from org.mpxj import Duration, TimeUnit, Relation, RelationType
from org.mpxj.reader import UniversalProjectReader
from org.mpxj.writer import UniversalProjectWriter, FileFormat
from java.time import LocalDateTime
from mpp_engine import working_days, reschedule

inp, outp = sys.argv[1], sys.argv[2]
p = UniversalProjectReader().read(inp)
O = {t.getID().intValue(): t for t in p.getTasks() if t.getID() is not None}
root = O[0]; ch = O[7]
def days(n): return Duration.getInstance(n, TimeUnit.DAYS)
TY = {"FS": RelationType.FINISH_START, "SS": RelationType.START_START, "FF": RelationType.FINISH_FINISH}
def setpreds(t, specs):
    for r in list(t.getPredecessors()): t.removePredecessor(r.getPredecessorTask(), r.getType(), r.getLag())
    for sp in specs:
        x = sp[0]; ty = sp[1] if len(sp) > 1 else "FS"; lag = sp[2] if len(sp) > 2 else 0
        t.addPredecessor(Relation.Builder().predecessorTask(O[x]).type(TY[ty]).lag(days(lag)))

NOM = {
 8:  "[ATSI] Source A : consignation + mesures compensatoires / raccordement provisoire (la B2 reste en service)",
 9:  "[ATSI] Source A : remplacement de l'électropompe (inclus nourrice pressostatique des sources)",
 10: "[ATSI] Source A : remplacement de la pompe jockey + alimentation d'aspiration sur eau de ville",
 11: "[ATSI] Source A : remplacement de l'armoire pompe jockey et source A (disjoncteur + câbles CR1 depuis TGBT)",
 12: "[ATSI] Source A : réserve de 30 m³ (remplissage manuel, plaque descriptive, contact de niveau + report d'alarme)",
 21: "[ATSI] Source A : reprise des tuyauteries d'aspiration et de refoulement + vannes reportées en alarme",
 22: "[ATSI] Source A : nouvelle canne d'essai (vannes reportées en alarme)",
 13: "[EIFFAGE] Local source A : percement des voiles béton façade Nord (ventilation haute et basse) + redressement des tableaux",
 14: "[ATSI] Local source A : fourniture et pose des grilles de ventilation (après percement EIFFAGE)",
 15: "[ATSI] Local source A : flocage de la toiture (coupe-feu 1 h)",
 16: "[ATSI] Local source A : armoire de répartition des équipements annexes + disjoncteur depuis le TGBT",
 17: "[ATSI] Local source A : remplacement de la protection sprinkleur du local et des postes (PC n°5 : CPE + vanne d'isolement)",
 18: "[ATSI] Local source A : extension de la protection sprinkleur vers le local eau glacée",
 19: "[ATSI] Local source A : sonde de température reportée en alarme + contacts anti-intrusion (portes local, atelier, TGBT)",
 20: "[ATSI] Local source A : affichages d'exploitation, étiquetage, BAPI, reprise de la peinture des canalisations",
 24: "[ATSI] Postes de contrôle : entretien triennal des 7 postes (un seul poste hors service à la fois)",
 25: "[ATSI] Postes de contrôle : bypass sur les 7 postes + vannes reportées en alarme",
 26: "[ATSI] Postes de contrôle : contrôle visuel d'écoulement, gongs remplacés par une nourrice commune, manomètre et pressostat du PC6",
 27: "[ATSI] Postes de contrôle : numérotation des vannes de barrage/test/vidange + schémas à jour sur colonnes montantes",
 23: "[ATSI] Source A : MISE EN SERVICE ET ESSAI + levée des mesures compensatoires - AVANT consignation de la B2",
}
for i, n in NOM.items(): O[i].setName(n); O[i].setText(1, "EIFFAGE" if i == 13 else "SPK")
ch.setName("2. SOURCE A, LOCAL SPRINKLEUR ET POSTES DE CONTRÔLE (ATSI) - SOURCE A REMISE EN SERVICE AVANT CONSIGNATION DE LA B2")
ch.setNotes("Partie 2 harmonisée, ordre du calendrier prévisionnel (lot SPK) : consignation source A, travaux source A + pompe jockey, travaux du local source A, "
            "travaux des postes de contrôle, mise en service et essai source A, puis consignation de la B2. "
            "Seule la remise en service de la source A conditionne la consignation de la B2 : les travaux du local et des postes de contrôle se poursuivent en parallèle.")
O[23].setNotes("Source / hypothèse : Calendrier prévisionnel n° 32 Mise en service et essai source A. Conditionne la consignation de la B2 (liaison avec la tâche de vidange). "
               "Les travaux du local et des postes de contrôle ne la conditionnent pas.")

# liaisons du chapitre : travaux du local en parallele (plus de file unique), postes de controle apres la consignation source A
setpreds(O[15], [(3,)]); setpreds(O[16], [(3,)])
setpreds(O[18], [(17,)]); setpreds(O[19], [(17,)]); setpreds(O[20], [(18,), (19,)])

# ordre des taches (calendrier previsionnel)
ORDRE = [8, 9, 10, 11, 12, 21, 22, 13, 14, 15, 16, 17, 18, 19, 20, 24, 25, 26, 27, 23]
kids = [O[i] for i in ORDRE]
for t in kids: ch.removeChildTask(t)
for t in kids: ch.addChildTask(t)
p.getTasks().synchronizeTaskIDToHierarchy(); p.updateStructure()

# ordonnancement
WD = working_days(p.getDefaultCalendar())
res, info, idx = reschedule(p, WD)
def ldt(d, h): return LocalDateTime.of(d.year, d.month, d.day, h, 0)
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

# rapport
def f(t): return "%02d/%02d" % (t.getFinish().getDayOfMonth(), t.getFinish().getMonthValue())
def s(t): return "%02d/%02d" % (t.getStart().getDayOfMonth(), t.getStart().getMonthValue())
nm = lambda frag: next(t for t in p.getTasks() if t.getName() is not None and frag in str(t.getName()))
print("tâches:", p.getTasks().size() - 1, "| fin projet", f(root))
chap = next(t for t in p.getTasks() if t.getName() is not None and str(t.getName()).startswith("2. SOURCE A"))
print("chapitre 2 :", s(chap), "→", f(chap))
for t in chap.getChildTasks():
    pr = ",".join("%d%s%s" % (r.getPredecessorTask().getID().intValue(), str(r.getType())[:2], "" if float(r.getLag().getDuration()) == 0 else "+%g" % float(r.getLag().getDuration())) for r in t.getPredecessors())
    print("%3d %-118s %s %s-%s %s" % (t.getID().intValue(), str(t.getName())[:116], str(t.getDuration()), s(t), f(t), pr))
for fr in ["Consignation + VIDANGE", "Essais + REMISE EN SERVICE", "FIN DES TRAVAUX EIFFAGE"]:
    t = nm(fr); print("%-30s %s → %s" % (fr, s(t), f(t)))
