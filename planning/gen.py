# -*- coding: utf-8 -*-
import re, sys, datetime as dt
from xml.sax.saxutils import escape
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import data_exe as data

START = dt.date(2026, 11, 2)   # lundi - date par defaut (modifiable dans MS Project)
OUT = sys.argv[1] if len(sys.argv) > 1 else "planning.xml"

# ---------------------------------------------------------------- accents
PAIRS = """batiment:bâtiment brossees:brossées conservees:conservées continuite:continuité controlee:contrôlée debut:début decale:décalé devoiements:dévoiements disconnecte:disconnecté echantillons:échantillons ecoulement:écoulement electrochimique:électrochimique estime:estimé etre:être etude:étude exterieur:extérieur manometre:manomètre mecaniques:mécaniques neutralises:neutralisés preparation:préparation pres:près prevention:prévention prevue:prévue profiles:profilés reel:réel systemes:systèmes temperatures:températures usees:usées vegetation:végétation omega:oméga etudes:études reperage:repérage reseaux:réseaux reseau:réseau devoiement:dévoiement depose:dépose deposes:déposes
demolition:démolition demolitions:démolitions tranchee:tranchée tranchees:tranchées reserve:réserve reserves:réserves creees:créées
creation:création electrique:électrique electriques:électriques electricite:électricité electropompe:électropompe etancheite:étanchéité
equipements:équipements equipement:équipement controle:contrôle controles:contrôles generale:générale verification:vérification
verifications:vérifications prealables:préalables operations:opérations reception:réception realise:réalise realisation:réalisation
definit:définit definition:définition delai:délai delais:délais duree:durée durees:durées estimee:estimée estimees:estimées estimes:estimés
releve:relevé apres:après piece:pièce pieces:pièces tariere:tarière materiel:matériel demarrage:démarrage maitrise:maîtrise
evacuation:évacuation epuisement:épuisement epreuves:épreuves etetage:étêtage execution:exécution securite:sécurité
indisponibilite:indisponibilité recepage:recépage proprete:propreté portee:portée peripherique:périphérique peripheriques:périphériques
beches:bêches reservation:réservation reservations:réservations boites:boîtes boite:boîte geometre:géomètre geotextile:géotextile
decennale:décennale echelle:échelle epingle:épingle planeite:planéité corniere:cornière debitmetre:débitmètre etalonnage:étalonnage
ecart:écart electromagnetique:électromagnétique debit:débit temperature:température reportes:reportés reportee:reportée reportees:reportées
numerotation:numérotation schemas:schémas recolement:récolement levee:levée complementaires:complémentaires cloture:clôture
facade:façade glacee:glacée repartition:répartition demontage:démontage demonte:démonté reservoir:réservoir echappement:échappement
reutilisee:réutilisée mecanique:mécanique entree:entrée etiquetage:étiquetage cablage:câblage enterres:enterrés enterre:enterré
butees:butées filetees:filetées penetration:pénétration aerien:aérien aerienne:aérienne aeriens:aériens cables:câbles cable:câble
vegetale:végétale reglage:réglage refection:réfection enrobe:enrobé enrobes:enrobés reemploi:réemploi resistants:résistants
camera:caméra transverses:transverses calees:calées taches:tâches liees:liées ouvres:ouvrés hypothese:hypothèse decalage:décalage
preavis:préavis previsionnel:prévisionnel boulonnee:boulonnée metallique:métallique galvanises:galvanisés galvanise:galvanisé seche:séché
reunion:réunion etablissement:établissement etat:état associes:associés acces:accès grillagee:grillagée reduire:réduire
etudes:études detection:détection coulee:coulée beton:béton plate:plate degres:degrés systeme:système premiere:première
mise:mise definitif:définitif depose:dépose reutilisation:réutilisation retablissement:rétablissement controle:contrôle
specifique:spécifique equipes:équipes elements:éléments prevu:prévu prevues:prévues necessaire:nécessaire exigee:exigée
validee:validée validation:validation resistance:résistance fabrication:fabrication stockage:stockage electriques:électriques
mesures:mesures procedure:procédure presence:présence general:général generaux:généraux
installees:installées cuvelage:cuvelage integrite:intégrité qualite:qualité categorie:catégorie conditionnes:conditionnés conditionne:conditionné
mediane:médiane methode:méthode hydrauliques:hydrauliques definir:définir livre:livré detail:détail zone:zone
mobilisation:mobilisation soumission:soumission ensemble:ensemble heure:heure heures:heures annee:année
metre:mètre metres:mètres arrivee:arrivée arrivees:arrivées departs:départs fenetre:fenêtre
visa:visa fait:fait differentes:différentes
reference:référence references:références protegee:protégée termine:terminé termines:terminés
poussieres:poussières amenee:amenée egalisation:égalisation polyethylene:polyéthylène debord:débord soigne:soigné antiderapantes:antidérapantes seance:séance ci:ci derniere:dernière dernier:dernier semaine:semaine
"""
ACC = {}
for pair in PAIRS.split():
    k, v = pair.split(":")
    ACC[k] = v

def accent(s):
    s = s.replace("OEUVRE","ŒUVRE").replace("/elec/","/électricité/").replace("<->", "↔").replace("->", "→").replace(" deg", "°")
    s = re.sub(r"\bm2\b", "m²", s); s = re.sub(r"\bm3\b", "m³", s)
    s = re.sub(r"\bO ?(12,48|14|90)\b", lambda m: "Ø" + ("90" if m.group(1) == "90" else " " + m.group(1)), s)
    s = s.replace("2 x O90", "2 x Ø90")
    s = s.replace("MISE A LA TERRE", "MISE À LA TERRE").replace("A CONFIRMER", "À CONFIRMER").replace("A confirmer", "À confirmer").replace("A valider", "À valider").replace("Mettre la duree a 0", "Mettre la durée à 0")
    def rep(m):
        w = m.group(0); lw = w.lower()
        if lw == "a" and w == "a": return "à"
        if lw in ACC and len(w) > 1:
            acc = ACC[lw]
            if w.isupper(): return acc.upper()
            if w[0].isupper(): return acc[0].upper() + acc[1:]
            return acc
        return w
    return re.sub(r"[A-Za-z]+", rep, s)

# ---------------------------------------------------------------- calendrier
def easter(y):
    a = y % 19; b = y // 100; c = y % 100; d = b // 4; e = b % 4
    f = (b + 8) // 25; g = (b - f + 1) // 3; h = (19 * a + b - d - g + 15) % 30
    i = c // 4; k = c % 4; l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mo = (h + l - 7 * m + 114) // 31; da = ((h + l - 7 * m + 114) % 31) + 1
    return dt.date(y, mo, da)

HOL = {}
for y in (2026, 2027, 2028, 2029):
    e = easter(y)
    for d, n in [(dt.date(y, 1, 1), "Jour de l'an"), (e + dt.timedelta(1), "Lundi de Pâques"), (dt.date(y, 5, 1), "Fête du travail"),
                 (dt.date(y, 5, 8), "Victoire 1945"), (e + dt.timedelta(39), "Ascension"), (e + dt.timedelta(50), "Lundi de Pentecôte"),
                 (dt.date(y, 7, 14), "Fête nationale"), (dt.date(y, 8, 15), "Assomption"), (dt.date(y, 11, 1), "Toussaint"),
                 (dt.date(y, 11, 11), "Armistice 1918"), (dt.date(y, 12, 25), "Noël")]:
        HOL[d] = n

def working_days(start, n):
    out = []; d = start
    while len(out) < n:
        if d.weekday() < 5 and d not in HOL: out.append(d)
        d += dt.timedelta(1)
    return out

LOTCOL = {"VRD": "GO", "SPK/MOA": "SPK", "GO/SPK": "GO + SPK"}
# ---------------------------------------------------------------- modele
class Tk: pass
tasks = []; byk = {}; sums = []
level = 0
order = []   # ordre d'apparition (S ou T)
for it in data.ITEMS:
    if it[0] == "S":
        sm = Tk(); sm.kind = "S"; sm.level = it[1]; sm.name = accent(it[2]); order.append(sm)
        sums.append(sm); cur = it[1]
    elif it[0] == "T":
        _, key, name, dur, lot, preds, src = it
        t = Tk(); t.kind = "T"; t.key = key; t.name = accent(name); t.dur = dur; t.lot = lot; t.src = accent(src)
        t.level = cur + 1; t.links = []; t.span = None
        for p in [x for x in preds.split(",") if x]:
            m = re.match(r"^(\w+)(?::(FS|SS|FF))?([+-]\d+)?$", p)
            assert m, p
            t.links.append((m.group(1), m.group(2) or "FS", int(m.group(3) or 0)))
        tasks.append(t); byk[key] = t; order.append(t)
    else:
        _, key, name, lot, a, b, src = it
        t = Tk(); t.kind = "T"; t.key = key; t.name = accent(name); t.dur = 1; t.lot = lot; t.src = accent(src)
        t.level = cur + 1; t.links = [(a, "SS", 0), (b, "FF", 0)]; t.span = (a, b)
        tasks.append(t); byk[key] = t; order.append(t)
for t in tasks:
    if not t.links and t.key != "m_start":
        t.links = [("m_start", "FS", 0)]
    for k, _, _ in t.links:
        assert k in byk, (t.key, k)

# ---------------------------------------------------------------- ordonnancement (ASAP)
CAL = working_days(START, 900)
TOPO = []
def sched():
    done = {}
    normal = [t for t in tasks if t.span is None]
    pending = list(normal)
    while pending:
        prog = False
        for t in list(pending):
            if all(k in done for k, _, _ in t.links):
                sd = 0; fdmin = 0
                for k, ty, lag in t.links:
                    p = done[k]
                    if ty == "FS":
                        base = p.fd + (0 if p.key == "m_start" else 1)
                        sd = max(sd, base + lag)
                    elif ty == "SS": sd = max(sd, p.sd + lag)
                    elif ty == "FF": sd = max(sd, p.fd + lag - max(t.dur - 1, 0))
                if t.dur == 0:
                    # jalon : finit le jour du dernier predecesseur
                    fd = 0
                    for k, ty, lag in t.links:
                        p = done[k]; fd = max(fd, p.fd + lag if p.key != "m_start" else lag)
                    t.sd = t.fd = fd
                else:
                    t.sd = sd; t.fd = sd + t.dur - 1
                done[t.key] = t; pending.remove(t); prog = True; TOPO.append(t)
        if not prog:
            raise Exception("cycle : " + ", ".join(x.key for x in pending))
    for t in tasks:
        if t.span:
            a, b = byk[t.span[0]], byk[t.span[1]]
            t.sd = a.sd; t.fd = max(b.fd, t.sd); t.dur = t.fd - t.sd + 1
sched()
END = max(t.fd for t in tasks)

# ---------------------------------------------------------------- marges / chemin critique (passe arriere)
succ = {t.key: [] for t in tasks}
for t in tasks:
    if t.span: continue
    for k, ty, lag in t.links:
        succ[k].append((t, ty, lag))
for t in tasks: t.lf = None
for t in reversed(TOPO):
    lf = END
    for s, ty, lag in succ[t.key]:
        sls = s.lf - max(s.dur - 1, 0)       # debut au plus tard du successeur
        if ty == "FS": cand = sls - 1 - lag if t.dur or True else sls
        elif ty == "SS": cand = sls - lag + max(t.dur - 1, 0)
        else: cand = s.lf - lag
        if t.key != "m_start" or True: lf = min(lf, cand)
    t.lf = lf
for t in tasks:
    t.crit = (t.span is None and t.lf is not None and t.lf - t.fd <= 0 and t.key != "m_start") or (t.key == "m_start")

# ---------------------------------------------------------------- sommaires
def span_of(idx):
    s = order[idx]; kids = []
    for j in range(idx + 1, len(order)):
        o = order[j]
        if o.kind == "S" and o.level <= s.level: break
        if o.kind == "T": kids.append(o)
    return kids
for i, o in enumerate(order):
    if o.kind == "S":
        k = span_of(i)
        o.sd = min(x.sd for x in k); o.fd = max(x.fd for x in k); o.dur = o.fd - o.sd + 1

# ---------------------------------------------------------------- export XML
def ts(d, end=False):
    return d.strftime("%Y-%m-%dT") + ("17:00:00" if end else "08:00:00")
def dur(d): return "PT%dH0M0S" % (d * 8)

uid = {}; n = 0
for o in order:
    n += 1; o.uid = n; o.id = n
# WBS
cnt = [0] * 10
for o in order:
    cnt[o.level - 1] += 1
    for j in range(o.level, 10): cnt[j] = 0
    o.wbs = ".".join(str(c) for c in cnt[:o.level])

x = []
w = x.append
w('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
w('<Project xmlns="http://schemas.microsoft.com/project">')
w("<SaveVersion>14</SaveVersion>")
w("<Name>Planning EXE Phase 1 (15 semaines) - Decathlon Campus - Sprinklage + Gros Œuvre</Name>")
w("<Title>26_083 DECATHLON CAMPUS - Planning EXE Phase 1 - GO/VRD/CM/Bardage + SPRINKLAGE</Title>")
w("<Subject>Planning détaillé Phase 1 (2026) - Lot Gros Œuvre / VRD / CM / Bardage et Lot Sprinklage</Subject>")
w("<Company>Decathlon Campus - Villeneuve d'Ascq</Company>")
w("<CreationDate>%s</CreationDate>" % dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
w("<LastSaved>%s</LastSaved>" % dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
w("<ScheduleFromStart>1</ScheduleFromStart>")
w("<StartDate>%s</StartDate><FinishDate>%s</FinishDate>" % (ts(START), ts(CAL[END], True)))
w("<FYStartDate>1</FYStartDate><CriticalSlackLimit>0</CriticalSlackLimit><CurrencyDigits>2</CurrencyDigits>")
w("<CurrencySymbol>€</CurrencySymbol><CurrencySymbolPosition>1</CurrencySymbolPosition><CalendarUID>1</CalendarUID>")
w("<DefaultStartTime>08:00:00</DefaultStartTime><DefaultFinishTime>17:00:00</DefaultFinishTime>")
w("<MinutesPerDay>480</MinutesPerDay><MinutesPerWeek>2400</MinutesPerWeek><DaysPerMonth>20</DaysPerMonth>")
w("<DefaultTaskType>1</DefaultTaskType><DefaultFixedCostAccrual>3</DefaultFixedCostAccrual><DefaultStandardRate>0</DefaultStandardRate>")
w("<DefaultOvertimeRate>0</DefaultOvertimeRate><DurationFormat>7</DurationFormat><WorkFormat>2</WorkFormat><EditableActualCosts>0</EditableActualCosts>")
w("<HonorConstraints>1</HonorConstraints><EarnedValueMethod>0</EarnedValueMethod><InsertedProjectsLikeSummary>0</InsertedProjectsLikeSummary>")
w("<MultipleCriticalPaths>0</MultipleCriticalPaths><NewTasksEffortDriven>0</NewTasksEffortDriven><NewTasksEstimated>0</NewTasksEstimated>")
w("<SplitsInProgressTasks>1</SplitsInProgressTasks><SpreadActualCost>0</SpreadActualCost><SpreadPercentComplete>0</SpreadPercentComplete>")
w("<TaskUpdatesResource>1</TaskUpdatesResource><FiscalYearStart>0</FiscalYearStart><WeekStartDay>1</WeekStartDay>")
w("<MoveCompletedEndsBack>0</MoveCompletedEndsBack><MoveRemainingStartsBack>0</MoveRemainingStartsBack><MoveRemainingStartsForward>0</MoveRemainingStartsForward>")
w("<MoveCompletedEndsForward>0</MoveCompletedEndsForward><BaselineForEarnedValue>0</BaselineForEarnedValue><AutoAddNewResourcesAndTasks>1</AutoAddNewResourcesAndTasks>")
w("<StatusDate>%s</StatusDate><CurrentDate>%s</CurrentDate>" % (ts(START), ts(START)))
w("<Autolink>1</Autolink><NewTaskStartDate>0</NewTaskStartDate>")
w("<NewTasksAreManual>0</NewTasksAreManual><DefaultTaskEVMethod>0</DefaultTaskEVMethod><ProjectExternallyEdited>0</ProjectExternallyEdited>")
w("")
w("<ExtendedAttributes>")
for fid, fname, alias in [(188743731, "Text1", "Lot")]:
    w("<ExtendedAttribute><FieldID>%d</FieldID><FieldName>%s</FieldName><Alias>%s</Alias></ExtendedAttribute>" % (fid, fname, escape(alias)))
w("</ExtendedAttributes>")
# calendrier
w("<Calendars><Calendar><UID>1</UID><Name>Standard (lun-ven, jours fériés FR)</Name><IsBaseCalendar>1</IsBaseCalendar><IsBaselineCalendar>0</IsBaselineCalendar><BaseCalendarUID>-1</BaseCalendarUID><WeekDays>")
w("<WeekDay><DayType>1</DayType><DayWorking>0</DayWorking></WeekDay>")
for dtp in range(2, 7):
    w("<WeekDay><DayType>%d</DayType><DayWorking>1</DayWorking><WorkingTimes><WorkingTime><FromTime>08:00:00</FromTime><ToTime>12:00:00</ToTime></WorkingTime>"
      "<WorkingTime><FromTime>13:00:00</FromTime><ToTime>17:00:00</ToTime></WorkingTime></WorkingTimes></WeekDay>" % dtp)
w("<WeekDay><DayType>7</DayType><DayWorking>0</DayWorking></WeekDay></WeekDays><Exceptions>")
for d in sorted(HOL):
    if d.weekday() >= 5: continue
    w("<Exception><EnteredByOccurrences>0</EnteredByOccurrences><TimePeriod><FromDate>%sT00:00:00</FromDate><ToDate>%sT23:59:00</ToDate></TimePeriod>"
      "<Occurrences>1</Occurrences><Name>%s</Name><Type>1</Type><DayWorking>0</DayWorking></Exception>" % (d, d, escape(HOL[d])))
w("</Exceptions></Calendar></Calendars>")
w("<Tasks>")
for o in order:
    w("<Task><UID>%d</UID><ID>%d</ID><Name>%s</Name><Active>1</Active><Manual>0</Manual><Type>1</Type><IsNull>0</IsNull>"
      "<WBS>%s</WBS><OutlineNumber>%s</OutlineNumber><OutlineLevel>%d</OutlineLevel><Priority>500</Priority>" % (o.uid, o.id, escape(o.name), o.wbs, o.wbs, o.level))
    if o.kind == "S":
        w("<Start>%s</Start><Finish>%s</Finish><Duration>%s</Duration><DurationFormat>7</DurationFormat><Work>PT0H0M0S</Work>"
          "<EffortDriven>0</EffortDriven><Estimated>0</Estimated><Milestone>0</Milestone><Summary>1</Summary><Critical>0</Critical><ConstraintType>0</ConstraintType>"
          % (ts(CAL[o.sd]), ts(CAL[o.fd], True), dur(o.dur)))
    else:
        ms = o.dur == 0
        if ms:
            d0 = CAL[o.sd]; s_ = ts(d0) if o.key == "m_start" else ts(d0, True); f_ = s_
        else:
            s_ = ts(CAL[o.sd]); f_ = ts(CAL[o.fd], True)
        w("<Start>%s</Start><Finish>%s</Finish><Duration>%s</Duration><DurationFormat>7</DurationFormat><Work>PT0H0M0S</Work>"
          "<EffortDriven>0</EffortDriven><Estimated>0</Estimated><Milestone>%d</Milestone><Summary>0</Summary><Critical>%d</Critical><ConstraintType>0</ConstraintType>"
          % (s_, f_, dur(o.dur), 1 if ms else 0, 1 if o.crit else 0))
        if o.src: w("<Notes>%s</Notes>" % escape("Source / hypothèse : " + o.src))
        for k, ty, lag in o.links:
            tcode = {"FF": 0, "FS": 1, "SF": 2, "SS": 3}[ty]
            w("<PredecessorLink><PredecessorUID>%d</PredecessorUID><Type>%d</Type><CrossProject>0</CrossProject><LinkLag>%d</LinkLag><LagFormat>7</LagFormat></PredecessorLink>"
              % (byk[k].uid, tcode, lag * 4800))
        w("<ExtendedAttribute><FieldID>188743731</FieldID><Value>%s</Value></ExtendedAttribute>" % escape(LOTCOL.get(o.lot, o.lot)))
    w("</Task>")
w("</Tasks></Project>")
open(OUT, "w", encoding="utf-8").write("\n".join(x))

# ---------------------------------------------------------------- rapport
def D(i): return CAL[i].strftime("%d/%m/%Y")
print("Taches:", len(tasks), " Debut:", D(0), " Fin:", D(END), " Duree:", END + 1, "jours ouvres")
for o in order:
    if o.kind == "S" and o.level == 1:
        print("%-75s %s -> %s (%d j)" % (o.name[:75], D(o.sd), D(o.fd), o.dur))
print("\nChemin critique :")
for t in sorted([t for t in tasks if t.crit], key=lambda t: t.sd):
    print("  %s -> %s  %3dj  %s" % (D(t.sd), D(t.fd), t.dur, t.name[:90]))
b = byk
print("\nIndisponibilite B2: vidange", D(b["spk_vidange"].sd), "-> remise en service", D(b["spk_msb2"].fd), "=", b["spk_msb2"].fd - b["spk_vidange"].sd + 1, "j ouvres")
print("Hamacs:", [(t.key, t.dur) for t in tasks if t.span])

# ---------------------------------------------------------------- export Excel (assistant d'import Project)
import openpyxl
from openpyxl.styles import Font
wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Planning"
ws.append(["ID", "Niveau hiérarchique", "Nom", "Durée", "Prédécesseurs", "Lot", "Source / hypothèse"])
for c in ws[1]: c.font = Font(bold=True)
ids = {o: i + 1 for i, o in enumerate(order)}
for o in order:
    if o.kind == "S":
        ws.append([ids[o], o.level, o.name, None, None, None, None]); continue
    pr = []
    for k, ty, lag in o.links:
        if byk[k].key == "m_start" and ty == "FS" and not lag and o.key != "m_start":
            code = "FD"
        else:
            code = {"FS": "FD", "SS": "DD", "FF": "FF"}[ty]
        txt = str(ids[byk[k]]) + code
        if lag: txt += "%+d j" % lag
        pr.append(txt)
    d = "0 jour" if o.dur == 0 else "%d jours" % o.dur
    ws.append([ids[o], o.level, o.name, d, ";".join(pr), LOTCOL.get(o.lot, o.lot), o.src])
for col, wd in zip("ABCDEFG", (6, 10, 110, 10, 22, 10, 80)): ws.column_dimensions[col].width = wd
wb.save(OUT.replace(".xml", "_import_Excel.xlsx"))
