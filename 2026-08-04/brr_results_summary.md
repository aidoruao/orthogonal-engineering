# BRR Results Summary (2026-08-04)


### v1 — blank init, strict parse (both models, D=4, 3 seeds)

- **qwen2.5-1.5b / blank** (n=3): first=20 best=20 (depth 0.0), peak qpt=0.50952, final qpt=0.01080, tokens=1871, degraded runs=0/3, plateau@2.0
- **tinyllama-1.1b / blank** (n=3): first=47 best=47 (depth 0.0), peak qpt=0.15635, final qpt=0.01343, tokens=1620, degraded runs=2/3, plateau@2.5

### v2 — priming A/B (exemplar vs blank, D=4, 3 seeds)

- **qwen2.5-1.5b / unprimed** (n=3): first=32 best=32 (depth 0.0), peak qpt=0.08000, final qpt=0.01600, tokens=2000, depth-to-40=0.0 (of 1 reached), degraded runs=0/3, plateau@2.0
- **qwen2.5-1.5b / primed** (n=3): first=60 best=60 (depth 0.0), peak qpt=0.15000, final qpt=0.03000, tokens=2000, depth-to-40=0.0 (of 3 reached), degraded runs=2/3, plateau@2.0
- **tinyllama-1.1b / unprimed** (n=3): first=60 best=60 (depth 0.0), peak qpt=0.19559, final qpt=0.02564, tokens=1240, depth-to-40=0.0 (of 3 reached), degraded runs=3/3, plateau@3.5
- **tinyllama-1.1b / primed** (n=3): first=67 best=67 (depth 0.0), peak qpt=0.25864, final qpt=0.01799, tokens=1335, depth-to-40=0.0 (of 3 reached), degraded runs=3/3, plateau@2.5

### Priming effect (F15 test)

- tinyllama-1.1b: priming Δbest=+6.7, Δpeak_qpt=+0.063045, Δtokens=-95 (positive = priming wins)
- qwen2.5-1.5b: priming Δbest=+28.0, Δpeak_qpt=+0.070000, Δtokens=+0 (positive = priming wins)