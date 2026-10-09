# Lessons

Short rules learned while building, each with the evidence that taught it. Add one line when a build teaches something that applies beyond one model. Agents read this file; it is not a diary.

| Rule | Why (evidence) |
|---|---|
| Two plates side by side are not joined: put one part across every seam. | Two building-atlas details (porch, solar array) were two separate halves; `check` reports them as floating. |
| Every Technic beam needs a pin or axle into a neighbour in another layer. | The crane boom's beams and panels were placed with no pins: 127 floating parts that the render hid. |
| Read a part's size from `ports PART` (its body box), not from its number. | 60623 is a 4x6 door; guessing a smaller size made the kit report collisions across four courses. |
| Mudguards and wheel arches must clear the tyres. Raise the body until the kit stops naming a tyre. | Vehicle-atlas mudguards sat one plate low, 8 LDU into the plates and tyres. |
| In pin chains, use `along=` to point each beam, not `roll`. | `roll` is relative to the previous part and silently turned a frame rail 90°. |
| Side studs have a direction: check it before mating engines or tiles. | 30414 at `turn=0` faces `-Z`, so the engines pointed forward until it was turned 180°. |
| A round 1x1 plate's socket is `pin_hole[0]`. Use the names `ports` lists. | The kit error listed the real port names. |
