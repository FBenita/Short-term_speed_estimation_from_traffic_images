# Short-term speed estimation and forecasting from low-frequency traffic camera snapshots

Code and data for the manuscript

> **Short-term speed estimation and forecasting from low-frequency traffic camera snapshots: Evidence from a Singapore expressway**

We collected images every five minutes from five public cameras on a 11.7 km corridor in Singapore during six weeks of 2022, together with 44,884 travel speed records from the Google Maps API. Vehicles were counted with Mask R-CNN and DETR pre-trained on COCO, and counts and image densities were used by random forest, support vector regression, extreme gradient boosting and long short-term memory models.

## Repository structure

```
├── scripts/
│   ├── roc_pipeline.py        # full analysis: all tables and figures in the paper
│   
└── data/
    ├── Counties_2010-2017_full_dataset_new.csv
```

## Data

- **County panel, 2010–2017.**
  - ACS five-year estimates: vehicles available, commuting mode, poverty, income and population.
  - Census Nonemployer Statistics for taxi and limousine service (NAICS 4853).
  - Ride-hailing entry dates from Lee et al. (2022, *MIS Quarterly*).


## Requirements

Python 3.9+ with numpy, pandas, scipy and matplotlib:

```bash
pip install numpy pandas scipy matplotlib
```

## Reproducing the results

From the repository root:

```bash
python scripts/01_pipeline.py --data data/Counties_2010-2017_full_dataset_new.csv --out results
```

The run takes under a minute with 999 bootstrap draws. It writes:

- `results/Tables/`: LaTeX tables as reported in the paper, plus `all_estimates.csv`.
- `results/Figures/`: Figures (PNG, 300 dpi).
- `results/run_log.tex`: the full log of every estimate.](https://ddum-sutd.github.io/Image-based%20vehicle%20traffic%20monitoring/)

## Citation

If you use this code or data, please cite the accompanying paper.
