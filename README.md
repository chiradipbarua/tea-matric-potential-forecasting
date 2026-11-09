# Tea-garden soil matric-potential forecasting: analysis code

Code accompanying the article:

> Barua, C., Sarma, A.K., Mitra, S. *Tea-garden soil matric-potential forecasting using zero-shot and parameter-efficiently adapted foundation models.* Computers and Electronics in Agriculture (under revision).

The repository contains the evaluation metrics, figure scripts and the experiment runner used for the revision analyses (five-seed Chronos-2 LoRA training, matched target-only GRU controls and individual-channel Chronos-2 forecasts). The field observations are not included; they are available from the corresponding author on reasonable request (cbarua@iitg.ac.in).

## Contents

| Path | Description |
|---|---|
| `metrics.py` | Point metrics (MAE, RMSE, median AE, bias, R², Pearson r, ±10/±15 kPa proportions, MSE skill), interval metrics and proper scores (coverage, width, pinball loss, interval score, WIS), finite-rank conformal expansion, warning confusion metrics and joint-calendar moving-block bootstrap MAE differences. |
| `publication_figures.py` | Scripts for Figures 1, 3, 6 and 7. Figures 1 and 3 are schematics; Figures 6 and 7 are drawn from aggregate estimate tables (see `SCHEMAS.md`). |
| `revision_gpu/` | Runner and scoring script for the revision experiments (LoRA seeds 13, 42, 2026, 3407, 9001; GRU controls with 168- and 336-h contexts; individual-channel forecasts). |
| `SCHEMAS.md` | Expected input fields, units and eligibility rules. |
| `tests/` | Unit tests on synthetic data. |

## Installation

Python 3.11 or newer is recommended.

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

The GPU runner additionally needs PyTorch, chronos-forecasting, PEFT and Transformers (`requirements-gpu.txt`; install the CUDA build of PyTorch that matches your GPU). The revision experiments used Python 3.11.15, PyTorch 2.11.0+cu128, chronos-forecasting 2.2.2, PEFT 0.19.1 and Transformers 4.57.6 with the `amazon/chronos-2` checkpoint at revision `29ec3766d36d6f73f0696f85560a422f50e8498c`, on an NVIDIA RTX 4070 SUPER (12 GB).

## Usage

Schematic figures:

```bash
python publication_figures.py --output-dir outputs
```

Empirical figure panels from aggregate tables:

```bash
python publication_figures.py --output-dir outputs --coverage-csv coverage.csv --alert-csv alerts.csv
```

Revision experiments (requires the study input files listed in `revision_gpu/README.md`):

```bash
python revision_gpu/run_gpu_revision.py --input-dir /path/to/inputs --task check --output /path/to/results
python revision_gpu/verify_scoring.py --input-dir /path/to/inputs
```

## Notes

- Metrics assume that observations and forecasts are already aligned on common eligible endpoints; quality control, sensor aggregation and episode labelling are done beforehand (see `SCHEMAS.md`).
- Warning confusion counts refer to forecast origins, not to distinct drying episodes.
- Undefined ratios (e.g. precision with no alerts) are returned as NaN rather than zero.
- The repository does not include the original zero-shot and local-model inference scripts.

## Licence

Code is released under the MIT Licence (see `LICENSE`). Model weights and third-party packages keep their own licences and are not redistributed here.

## Citation

Please cite the article above and this repository (see `CITATION.cff`).
