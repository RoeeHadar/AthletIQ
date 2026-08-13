# ML architecture reference

## When

Only if PRD/SRS confirms an ML component (AthletIQ: yes — win/lose prediction).

## Owns

ML **placement** in the system (training job, artifact store, serving path) inside architecture docs. Methodology detail stays in `docs/06-design/ml-design.md`.

## Required themes

- Offline train vs online serve
- Baseline + LR/XGBoost MVP; NumPy NN post-MVP as documented stretch
- Evaluation vs baseline feeds model card / success metrics

## Do not

- Treat PyTorch as allowed for the from-scratch NN stretch (NumPy only)
- Invent numeric metrics — Grill-Me or Open Question
