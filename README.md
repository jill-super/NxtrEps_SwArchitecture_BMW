# Software Architecture — EPS (BMW 5441)

System architecture of the Electric Power Steering (EPS) system: a design
workbook plus an interactive static docs site generated from it.

## Contents

- `Design/Bmw_5441_Design_SysArch_A.xlsx` — source of truth. 11 sheets:
  revision history, release tracker, Level 1 / Level 2 functional architecture,
  functional decomposition, safety view, function descriptions, physical
  interactions, external interfaces, system states, architecture assessment
  (plus one hidden scratch sheet).
- `docs/` — Astro + Starlight site publishing **all** workbook content as
  searchable, interactive pages. Diagrams are converted from the workbook's
  embedded EMF previews to SVG+PNG.

## Sheet → page map

| Workbook sheet | Docs page |
|---|---|
| Rev History | Revision History |
| Release Tracker | Release Tracker |
| System Architecture_Level 1 | Architecture › Level 1 |
| System Architecture_Level 2 | Architecture › Level 2 |
| Functional Decomposition View | Architecture › Functional Decomposition |
| System Safety Architecture View | Architecture › Safety View |
| Description | Design Details › Function Descriptions |
| Interactions | Design Details › Interactions Matrix |
| Identified External Interfaces | Design Details › External Interfaces |
| System States | Design Details › System States |
| Architecture Assessment | Assessment › Method, Scoring |
| Embedded EMF/Visio drawings | Original Diagrams |
