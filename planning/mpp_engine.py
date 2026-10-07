# -*- coding: utf-8 -*-
# Moteur d'ordonnancement (ASAP, FS/SS/FF + decalages, contrainte FNET) calqué sur un fichier MS Project lu avec MPXJ.
import datetime as dt
import jpype, jpype.imports, mpxj
if not jpype.isJVMStarted(): jpype.startJVM()
from java.time import LocalDate, LocalDateTime
from org.mpxj import TimeUnit

def days_of(d):
    """Duration MPXJ -> jours (8 h/jour)."""
    v = float(d.getDuration()); u = str(d.getUnits())
    return v if u == "d" else v / 8 if u == "h" else v * 5 if u == "w" else v / 480 if u == "m" else v

def working_days(cal, start=dt.date(2026, 10, 1), n=900):
    out, d = [], start
    while len(out) < n:
        if d.weekday() < 5 and cal.isWorkingDate(LocalDate.of(d.year, d.month, d.day)): out.append(d)
        d += dt.timedelta(1)
    return out

def reschedule(p, WD):
    """Calcule (sd, fd) en indices de jours ouvres pour toutes les taches feuilles. Retourne {id: (sd, fd)}."""
    idx = {d: i for i, d in enumerate(WD)}
    P0 = p.getProjectProperties().getStartDate().toLocalDate()
    P0 = dt.date(P0.getYear(), P0.getMonthValue(), P0.getDayOfMonth())
    base = next(i for i, d in enumerate(WD) if d >= P0)
    leaves = [t for t in p.getTasks() if t.getID() is not None and t.getID().intValue() != 0 and not t.hasChildTasks()]
    info = {}
    for t in leaves:
        tid = t.getID().intValue(); pr = []
        for r in t.getPredecessors():
            lag = days_of(r.getLag()) if r.getLag() is not None else 0
            pr.append((r.getPredecessorTask().getID().intValue(), str(r.getType()), lag))
        cons = None; snet = None
        ct = str(t.getConstraintType())
        if ct in ("FINISH_NO_EARLIER_THAN", "START_NO_EARLIER_THAN"):
            c = t.getConstraintDate(); cd = dt.date(c.getYear(), c.getMonthValue(), c.getDayOfMonth())
            if ct == "FINISH_NO_EARLIER_THAN": cons = max(i for i, d in enumerate(WD) if d <= cd)      # dernier jour ouvre <= date
            else: snet = min(i for i, d in enumerate(WD) if d >= cd)                                   # premier jour ouvre >= date
        info[tid] = dict(t=t, dur=int(round(days_of(t.getDuration()))), pr=pr, cons=cons, snet=snet)
    res = {}; pending = set(info)
    while pending:
        prog = False
        for tid in sorted(pending):
            I = info[tid]
            if all(pid in res or pid not in info for pid, _, _ in I["pr"]):
                sd = base if I["snet"] is None else max(base, I["snet"]); fmin = None
                for pid, ty, lag in I["pr"]:
                    if pid not in res: continue
                    ps, pf = res[pid]
                    if ty == "FS": sd = max(sd, pf + 1 + int(lag))
                    elif ty == "SS": sd = max(sd, ps + int(lag))
                    elif ty == "FF": fmin = pf + int(lag) if fmin is None else max(fmin, pf + int(lag))
                d = I["dur"]
                if d == 0:
                    fd = sd - 1 if I["pr"] else sd
                    fd = max([pf for pid, ty, lag in I["pr"] if pid in res for ps, pf in [res[pid]]] + [base]) if I["pr"] else base
                    res[tid] = (fd, fd)
                else:
                    fd = sd + d - 1
                    if fmin is not None and fmin > fd: sd = fmin - d + 1; fd = fmin
                    if I["cons"] is not None and I["cons"] > fd: fd = I["cons"]
                    res[tid] = (sd, fd)
                pending.discard(tid); prog = True
        if not prog: raise Exception("cycle: %s" % sorted(pending))
    return res, info, idx
