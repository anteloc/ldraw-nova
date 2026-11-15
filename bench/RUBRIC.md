# Visual rubric

Automatic checks cannot judge whether a model looks right; earlier toolkit changes were accepted on passing checks while the user rejected the models. Score every benchmark model with this rubric, blind to toolkit revision and agent model.

## Prepare blind sheets

```sh
.venv/bin/python bench/score.py sheets output/bench/baseline output/bench/candidate --out output/bench/blind
```

This renders home, front, right and top views of every delivered model from all suites under `output/bench/blind/model-NN/`, shuffled together. `key.json` maps the anonymous IDs back to runs; do not open it until scoring is finished. Score from the four images only, at the size they open.

## Score five dimensions from 1 to 5

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| Identity | The subject is not recognisable | Recognisable after reading the brief | Recognisable at thumbnail size |
| Features | Several required features missing | All present, some crude | All present and convincing |
| Construction | Parts float, intersect or stick out | Minor visible defects | No visible defect |
| Finish | Bare studs and gaps on show surfaces | Mostly finished surfaces | Deliberate studs only; clean lines |
| Character | Generic box with details | Some distinctive choices | A design someone would want to build |

Use whole numbers. Fill `output/bench/blind/rubric.json`, one object per anonymous model:

```json
"model-07": {"identity": 4, "features": 3, "construction": 4, "finish": 3, "character": 3,
             "notes": "Grille reads well; knobs float in front of the case."}
```

Then copy the scores to their runs, which also computes each mean:

```sh
.venv/bin/python bench/score.py unblind output/bench/blind
```

A model is accepted when its static checks pass, every required feature in its brief is present, the rubric mean is at least 3.5 and no dimension is below 3. Report failures as failures; an unfinished run has no completion time.
