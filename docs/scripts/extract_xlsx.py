#!/usr/bin/env python3
"""Extract all content from Design/Bmw_5441_Design_SysArch_A.xlsx into docs JSON.

Run:  python3 ./scripts/extract_xlsx.py   (from docs/)
Output: src/data/*.json  (checked in, so the site builds without the .xlsx)
Source workbook is NOT copied into the site; see src/content/docs/source.mdx.
"""
import json
import sys
from pathlib import Path

try:
    import openpyxl
except ImportError:
    sys.exit("need openpyxl: pip install openpyxl")

ROOT = Path(__file__).resolve().parents[1]
XLSX = ROOT.parent / "Design" / "Bmw_5441_Design_SysArch_A.xlsx"
# also support running from repo root
if not XLSX.exists():
    alt = Path.cwd() / "Design" / "Bmw_5441_Design_SysArch_A.xlsx"
    if alt.exists():
        XLSX = alt
OUT = Path(__file__).resolve().parent.parent / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)

wb = openpyxl.load_workbook(XLSX, data_only=True)


def rows_values(name):
    ws = wb[name]
    out = []
    for row in ws.iter_rows(values_only=True):
        vals = [( "" if v is None else str(v).strip()) for v in row]
        while vals and vals[-1] == "":
            vals.pop()
        if not vals or all(v == "" for v in vals):
            continue
        out.append(vals)
    return out


def write(name, obj):
    p = OUT / name
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {p} ({len(json.dumps(obj))} chars)")


# ---- Rev History ----
rev = rows_values("Rev History")
# header is row with Date|Event|...
hdr_idx = next(i for i, r in enumerate(rev) if any("Date" in c for c in r))
write("rev-history.json", {"title": rev[0][0] if rev else "Revision History",
                           "header": rev[hdr_idx],
                           "rows": rev[hdr_idx + 1:]})

# ---- Release Tracker ----
rel = rows_values("Release Tracker")
note = next((" ".join(r) for r in rel if any("release tracker" in c.lower() for c in r)), "")
# header row containing "Type of Release"
hdr = next(i for i, r in enumerate(rel) if any("Type of Release" in c for c in r))
write("release-tracker.json", {"note": note, "header": rel[hdr], "rows": rel[hdr + 1:]})

# ---- Level 1 ----
l1 = rows_values("System Architecture_Level 1")
# Sections: requirements table, primary/secondary functions, allocation
req_rows = []
funcs_primary, funcs_secondary = [], []
alloc = []  # (element, function)
mode = "req"
for r in l1:
    joined = " | ".join(r)
    if "Primary Functions" in joined:
        mode = "primary"; continue
    if "Secondary Functions" in joined:
        mode = "secondary"; continue
    if "Allocation of Physical Elements" in joined:
        mode = "alloc"; continue
    if mode == "req" and len(r) >= 3 and r[0] == "" and "Functional Requirements" not in joined:
        # [ '', requirement, allocation, '', capability? ] — layout varies
        req = r[1] if len(r) > 1 else ""
        alloc_s = r[2] if len(r) > 2 else ""
        cap = r[4] if len(r) > 4 else (r[3] if len(r) > 3 else "")
        if req:
            req_rows.append({"requirement": req, "allocation": alloc_s, "capability": cap})
    elif mode == "primary" and len(r) >= 2 and r[1].startswith("P"):
        funcs_primary.append(r[1])
    elif mode == "secondary" and len(r) >= 2 and r[1].startswith("S"):
        funcs_secondary.append(r[1])
    elif mode == "alloc":
        if not r or all(c == "" for c in r):
            continue
        if r[0] in ("Powerpack", "Control Module", "Software"):
            current = r[0]
            # second col may hold function on same row (Control Module | P15...)
            if len(r) > 1 and r[1].startswith(("P", "S")):
                alloc.append({"element": current, "function": r[1]})
        elif r[0] == "" and len(r) > 1 and r[1].startswith(("P", "S")):
            alloc.append({"element": current, "function": r[1]})

capabilities = [r.get("capability") for r in req_rows]
capabilities = [c for c in capabilities if c and c not in ("Capability of the system", "Terminology", "Colour Code",
    "MECHANICAL ACTUATOR", "POWERPACK", "MOTOR SENSING SUB-SYSTEM", "MOTOR ASSEMBLY",
    "CONTROL MODULE", "ELECTRONIC HARDWARE", "SOFTWARE")]
write("level-1.json", {"requirements": req_rows, "primary": funcs_primary,
                       "secondary": funcs_secondary, "allocation": alloc,
                       "capabilities": capabilities})

# ---- Colour code ----
write("colour-code.json", [
    {"code": "MECHANICAL ACTUATOR", "color": "#FFC000"},
    {"code": "POWERPACK", "color": "#F9CFB5"},
    {"code": "MOTOR SENSING SUB-SYSTEM", "color": "#00FFFF"},
    {"code": "MOTOR ASSEMBLY", "color": "#FFFF00"},
    {"code": "CONTROL MODULE", "color": "#00B0F0"},
    {"code": "ELECTRONIC HARDWARE", "color": "#D9D9D9"},
    {"code": "SOFTWARE", "color": "#92D050"},
])

# ---- Level 2 ----
l2 = rows_values("System Architecture_Level 2")
write("level-2.json", {"notes": [r for r in l2]})

# ---- Functional decomposition ----
fd = rows_values("Functional Decomposition View")
decomp = []
for r in fd:
    # layout: ['', '', '', Level1, Level2]
    if len(r) >= 4 and (r[3].startswith("P") or r[3].startswith("S")):
        l1f = r[3]
        l2f = r[4] if len(r) > 4 else ""
        decomp.append({"level1": l1f, "level2": l2f})
write("functional-decomposition.json", decomp)

# ---- Safety view ----
sv = rows_values("System Safety Architecture View")
hdr = next(i for i, r in enumerate(sv) if any("System Functions" in c for c in r))
safety = []
for r in sv[hdr + 1:]:
    # ['', Primary/Secondary, function, nomenclature, fs-concept, ts-concept?]
    cells = (r + ["", "", "", "", "", ""])[:6]
    safety.append({"group": cells[1], "function": cells[2], "nomenclature": cells[3],
                   "fsConcept": cells[4], "tsConcept": cells[5]})
write("safety-view.json", safety)

# ---- Description ----
# Header row: ['', 'Function', '', 'Input', 'Description', 'Output']; data rows: ['', 'P1', name, input, desc, output]
desc = rows_values("Description")
hdr = next(i for i, r in enumerate(desc) if "Input" in r and "Output" in r)
functions = []
for r in desc[hdr + 1:]:
    cells = (r + ["", "", "", "", "", ""])[:6]
    fid = cells[1]
    if not fid:
        continue
    functions.append({"id": fid, "name": cells[2], "input": cells[3],
                      "description": cells[4], "output": cells[5]})
write("function-descriptions.json", functions)

# ---- Interactions ----
inter = rows_values("Interactions")
# row0 title, row1 group header, row2 element header, rest matrix
header = inter[2]
cols = header[2:]  # element names (col index 2..)
matrix = []
for r in inter[3:]:
    if len(r) < 3:
        continue
    if "Note:" in " ".join(r):
        continue
    group = r[0]
    row_elem = r[1]
    if not row_elem:
        continue
    cells = (r[2:] + [""] * len(cols))[:len(cols)]
    matrix.append({"group": group, "element": row_elem,
                   "cells": [{"to": c, "relation": v} for c, v in zip(cols, cells)]})
write("interactions.json", {"columns": cols, "rows": matrix,
                            "note": "Interactions are shown from Rows to Columns. 'Connected to' = downstream, 'Connected with' = upstream."})

# ---- External interfaces ----
ext = rows_values("Identified External Interfaces")
# data starts after row with From|To|Mode|Medium
hdr = next(i for i, r in enumerate(ext) if "From" in r and "To" in r)
interfaces = []
current_group = ""
for r in ext[hdr + 1:]:
    cells = (r + ["", "", "", "", ""])[:5]
    if cells[0]:
        current_group = cells[0]
    name = cells[1]
    if not name:
        continue
    interfaces.append({"group": current_group, "signal": name, "from": cells[2],
                       "to": cells[3], "mode": cells[4] if len(cells) > 4 else "",
                       "medium": r[5] if len(r) > 5 else ""})
# fix: medium is 6th col
write("external-interfaces.json", interfaces)

# ---- System states ----
ss = rows_values("System States")
states, transitions, conditions, faults = [], [], [], []
for r in ss:
    pass  # parsed below positionally
# States: col 8 holds 'S1 OFF' / 'S2 Initialization' / ...; col 9 holds behaviour lines.
# First occurrence per state starts the state; subsequent non-empty col-9 lines append.
STATE_NAMES = {"S1 OFF": ("S1", "OFF"), "S2 Initialization": ("S2", "Initialization"),
               "S3 Enable": ("S3", "Enable"), "S4 Disable": ("S4", "Disable")}
seen_states: dict = {}
for r in ss:
    cells = (r + [""] * 10)[:10]
    key = cells[8].strip()
    beh = cells[9].strip()
    if key in STATE_NAMES and beh:
        sid = STATE_NAMES[key][0]
        seen_states.setdefault(sid, {"id": sid, "name": STATE_NAMES[key][1], "behaviour": []})
        if beh not in seen_states[sid]["behaviour"]:
            seen_states[sid]["behaviour"].append(beh)
    elif key == "" and beh and seen_states:
        # continuation behaviour line belongs to the most recently seen state
        # only before the Sx/Cx legend rows
        if beh.startswith("System ") and any(k in beh for k in ("draws", "waits", "assists", "communicat", "recieves", "receives", "performs", "has no", "does not")):
            last = list(seen_states.values())[-1]
            if beh not in last["behaviour"]:
                last["behaviour"].append(beh)
for sid in ["S1", "S2", "S3", "S4"]:
    if sid in seen_states:
        states.append(seen_states[sid])
# Transitions: Present State | Condition | Future State
for r in ss:
    if len(r) >= 15 and r[12] in ("S1 OFF", "S2 Initialization", "S3 Enable", "S4 Disable") \
            and r[13].startswith("C") and r[14].startswith("S"):
        transitions.append({"from": r[12], "condition": r[13], "to": r[14]})
# Conditions C1..C12 live in col 8 from the faults block onward, with
# continuation lines in col 9 (+ AND/OR in col 10)
cond_map = {}
current_c = None
for r in ss:
    cells = (r + [""] * 11)[:11]
    head = cells[8].strip()
    body = cells[9].strip()
    op = cells[10].strip()
    if len(head) in (2, 3) and head.startswith("C") and head[1:].isdigit() and body:
        current_c = head
        cond_map.setdefault(current_c, []).append(body + (f" [{op}]" if op else ""))
    elif current_c and head == "" and body:
        cond_map[current_c].append(body + (f" [{op}]" if op else ""))
    elif head.startswith("C") is False and head not in ("", "System State"):
        # keep current_c across fault rows? reset only on new Cn
        pass
for k in sorted(cond_map, key=lambda x: int(x[1:])):
    conditions.append({"id": k, "definition": cond_map[k]})
# Faults F1..F3, Rest
for r in ss:
    if len(r) >= 6 and r[2] in ("F1", "F2", "F3", "Rest"):
        faults.append({"id": r[2], "definition": r[3] if len(r) > 3 else "",
                       "response": r[4] if len(r) > 4 else "", "type": r[5] if len(r) > 5 else ""})
write("system-states.json", {"states": states, "transitions": transitions,
                             "conditions": conditions, "faults": faults})

# ---- Assessment ----
aa = rows_values("Architecture Assessment")
# KPPs: after "System Key Performance Parameters" list (9 items)
kpp_start = next(i for i, r in enumerate(aa) if any("System Key Performance Parameters" in c for c in r))
kpps = []
for r in aa[kpp_start + 1:kpp_start + 12]:
    if r and r[-1] and "Step" not in " ".join(r) and "Affected parameters" not in " ".join(r):
        kpps.append(r[-1])
kpps = kpps[:9]
# Criteria table header contains 'S No' and 'Weightage' (offset by leading empty col)
crit_hdr = next(i for i, r in enumerate(aa) if "S No" in r and "Weightage" in " ".join(r)
                and "Related Parameters" in " ".join(r))
criteria = []
for r in aa[crit_hdr + 1:]:
    if any("Required Information" in c for c in r):
        break
    # normalize: drop leading empties -> [S No, KPP, Related, Selection, ..., Weightage]
    cells = [c for c in r]
    while cells and cells[0] == "":
        cells.pop(0)
    if not cells:
        continue
    if cells[0].isdigit():
        cells = (cells + ["", "", "", "", ""])[:6]
        # weightage is last non-empty
        weight = next((c for c in reversed(cells) if c != ""), "")
        criteria.append({"no": cells[0], "kpp": cells[1], "related": cells[2],
                         "selection": cells[3], "weightage": weight})
    else:
        # continuation row for related/selection text
        if criteria:
            extra_rel = cells[1] if len(cells) > 1 else ""
            extra_sel = cells[2] if len(cells) > 2 else ""
            if extra_rel:
                criteria[-1]["related"] += "; " + extra_rel
            if extra_sel:
                criteria[-1]["selection"] += "; " + extra_sel
# Scoring: single header row holds TWO side-by-side tables (Alt1 cols 1..8, Alt2 cols 11..18)
score_hdr = next(i for i, r in enumerate(aa) if r.count("S No") >= 1 and "Weighted KPP Score" in " ".join(r)
                 and "Individual Criteria Score" in " ".join(r) and "Status" in " ".join(r))
alts = [{"alt": 1, "rows": [], "score": ""}, {"alt": 2, "rows": [], "score": ""}]
for r in aa[score_hdr + 1:]:
    if any("Architecture Assessment Score" in c for c in r):
        # score numbers are the Weighted total per alt block
        nums = [c for c in r if c not in ("", "Architecture Assessment Score")]
        if len(nums) >= 1:
            alts[0]["score"] = nums[0]
        if len(nums) >= 2:
            alts[1]["score"] = nums[1]
        break
    if not any(c.strip() for c in r):
        continue
    # pad to 19 cols (leading '' + 9 + '' + 9 ...)
    padded = (r + [""] * 20)[:20]
    left = [padded[1], padded[2], padded[3], padded[4], padded[5], padded[6], padded[7], padded[8]]
    right = [padded[11], padded[12], padded[13], padded[14], padded[15], padded[16], padded[17], padded[18]]
    if any(left):
        alts[0]["rows"].append({"no": left[0], "kpp": left[1], "criterion": left[2], "status": left[3],
                                "individual": left[4], "kppScore": left[5], "weightage": left[6],
                                "weighted": left[7]})
    if any(right):
        alts[1]["rows"].append({"no": right[0], "kpp": right[1], "criterion": right[2], "status": right[3],
                                "individual": right[4], "kppScore": right[5], "weightage": right[6],
                                "weighted": right[7]})
write("assessment.json", {"kpps": kpps, "criteria": criteria, "alternatives": alts,
                          "legend": {"1": "Fully meets selection criteria",
                                     "0.5": "Partially meets the selection criteria",
                                     "0": "Does not meet the selection criteria"}})

# ---- Diagrams manifest ----
write("diagrams.json", {
    "level1": [
        {"file": "image8.svg", "fallback": "image8.png", "label": "Level 1 functional architecture diagram (sheet drawing, part 1)"},
        {"file": "image9.svg", "fallback": "image9.png", "label": "Level 1 functional architecture diagram (sheet drawing, part 2)"}
    ],
    "level2": [
        {"file": "image10.svg", "fallback": "image10.png", "label": "Level 2 diagram fragment 1"},
        {"file": "image11.svg", "fallback": "image11.png", "label": "Level 2 diagram fragment 2"},
        {"file": "image12.svg", "fallback": "image12.png", "label": "Level 2 diagram fragment 3"},
        {"file": "image13.svg", "fallback": "image13.png", "label": "Level 2 diagram fragment 4"},
        {"file": "image14.svg", "fallback": "image14.png", "label": "Level 2 diagram fragment 5"}
    ],
    "safety": [{"file": "image15.svg", "fallback": "image15.png", "label": "Safety view diagram"}],
    "states": [{"file": "image16.svg", "fallback": "image16.png", "label": "System states diagram"}],
    "ports": ["image1.svg", "image2.svg", "image3.svg", "image4.svg", "image5.svg", "image6.svg", "image7.svg"],
    "note": "SVGs converted from the workbook's embedded EMF previews (xl/media/*.emf, Visio/OLE drawings on Level-1, Level-2, Safety and States sheets). Original .emf files are not shipped; see Source page."
})

print("done.")
