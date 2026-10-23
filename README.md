# Short-term speed estimation and forecasting from low-frequency traffic camera snapshots

Code and data for the manuscript

> **Short-term speed estimation and forecasting from low-frequency traffic camera snapshots: Evidence from a Singapore expressway**

Many cities publish still images from their traffic cameras every few minutes but no video. This study tests whether such snapshots can estimate and forecast expressway speeds. All data are real observations collected from public interfaces in 2022. None are simulated.

- **Images.** Five Land Transport Authority (LTA) cameras on the Bukit Timah Expressway (2703, 2705, 2706, 2707 and 2708) were queried every five minutes from 04:50 to 23:50 through the data.gov.sg Traffic Images API, during one week in each month from February to July 2022. In total there are 44,290 distinct images with at least one detected vehicle. Cameras 2706 and 2707 were used for both directions and the other three for one direction each, which gives seven camera-direction pairs.
- **Reference speeds.** There are 44,884 travel speed records from the Google Maps Directions API for the same seven pairs, collected at the same time stamps from March to June 2022.
- **Detection.** Vehicles were detected with Mask R-CNN and DETR, both pre-trained on COCO and not fine-tuned. Detections were assigned to a direction with a hand-drawn polygon for each camera and direction.
- **Models.** Vehicle counts and image densities feed random forest, support vector regression, XGBoost and LSTM models. The models estimate current speed and forecast speed 5, 15 and 30 minutes ahead. They are compared with a historical speed profile, persistence and an equal-weight combination, using Diebold-Mariano tests.

An earlier tutorial on the image pipeline is on the project website: [Image-based vehicle traffic monitoring](https://ddum-sutd.github.io/Image-based%20vehicle%20traffic%20monitoring/).

## Repository structure

```
├── README.md
├── LICENSE
├── CITATION.cff
├── requirements.txt                  # scripts (collection, benchmarks, figures)
├── requirements-models.txt           # modelling notebooks (TensorFlow 2.10, XGBoost 1.7)
├── scripts/
│   ├── 01_collect_image_urls.py      # image links from the data.gov.sg Traffic Images API
│   ├── 02_collect_google_speeds.py   # travel times from the Google Maps Directions API
│   ├── benchmarks.py                 # profile, persistence, combination and Diebold-Mariano tests
│   ├── make_figures.py               # all data figures of the paper
│   └── Traffic_plots.R               # original R version of the figures (superseded by make_figures.py)
├── notebooks/
│   ├── 03_detect_vehicles_maskrcnn.ipynb      # Mask R-CNN on Google Colab (TPU)
│   ├── 04_count_vehicles_by_direction.ipynb   # masks, counts, image density, merge with speeds
│   ├── 05_summaries_for_figures.ipynb         # averages by time of day and detection summaries
│   ├── 06_build_model_inputs.ipynb            # neighbouring-camera features, model input files
│   ├── models_maskrcnn/                       # training and test, Mask R-CNN features
│   │   ├── b_PIE.ipynb                        # southbound
│   │   ├── b_Woodlands.ipynb                  # northbound
│   │   ├── 2way.ipynb                         # both directions pooled
│   │   ├── speed_prediction_Result_Analysis.ipynb
│   │   ├── output_test_septem_v1 - Copy.csv   # model input (features and speeds)
│   │   ├── *_preprocessing_models/            # fitted scalers and encoder
│   │   └── *_best_models/                     # saved test predictions, selected parameters, errors
│   ├── models_detr/                           # same, DETR features
│   └── models_maskrcnn_score30/               # Mask R-CNN with detections scored above 0.3
├── data/
│   ├── cameras/
│   │   ├── camera_masks.csv            # direction polygons, order along the route, neighbours
│   │   └── google_od_pairs.csv         # origin and destination of each Google route
│   ├── google_speeds/                  # raw Directions API records, one file per pair and day
│   ├── features/                       # image features merged with speeds, one file per pair and day
│   └── figure_inputs/                  # small summary files read by make_figures.py
│       ├── Data/...
│       └── Results/...
└── results/                            # written by the scripts
```

Large files are archived only on Zenodo (see Data).

## Data

| Data | Where | Content |
|---|---|---|
| Camera masks and Google origin-destination pairs | `data/cameras/` | 7 camera-direction pairs |
| Google Maps travel times | `data/google_speeds/` | Route length (m) and travel time in traffic (s) every 5 minutes, March to June 2022 |
| Image features | `data/features/`, `notebooks/models_*/` | Counts and image density per image and direction, with neighbouring-camera features and the reference speed |
| Saved test predictions | `notebooks/models_*/*_best_models/` | June 2022 predictions of every model and specification |
| Detections | Zenodo data record | Every Mask R-CNN and DETR detection for the five cameras: image URL, time stamp, class, score and bounding box (about 0.9 GB) |
| Trained models | Zenodo data record | Selected RF, SVR, XGBoost (`.pkl`) and LSTM (`.h5`) models |

The image URLs in the detection files still resolved in October 2026. The same links can be recovered with `scripts/01_collect_image_urls.py`, because the API answers historical queries. The images themselves are not redistributed.

**Licences and terms.**
- The camera images contain information from the Traffic Images dataset accessed from data.gov.sg, made available under the [Singapore Open Data Licence version 1.0](https://data.gov.sg/open-data-licence).
- The travel times were obtained from the Google Maps Directions API and remain subject to the [Google Maps Platform Terms of Service](https://cloud.google.com/maps-platform/terms).
- Code is released under the MIT licence. Derived data produced in this project are released under CC BY 4.0.

## Requirements

- Scripts: Python 3.9 or later.

  ```bash
  pip install -r requirements.txt
  ```

- Modelling notebooks: Python 3.9 or 3.10.

  ```bash
  pip install -r requirements-models.txt
  ```

  Use the versions in `requirements-models.txt` to load the saved `.pkl` and `.h5` models.

## Reproducing the results

**Quick path, from the saved predictions (about one minute).** This reproduces the benchmark table, the significance tests, the typical and atypical comparison, and all data figures:

```bash
python scripts/benchmarks.py notebooks results
python scripts/make_figures.py data/figure_inputs results/figures
```

`benchmarks.py` writes:

- `benchmark_accuracy.csv`
- `diebold_mariano_tests.csv`
- `typical_atypical_intervals.csv`
- `test_week_current_speed.csv`, which is the input of `Errors_by_departure.png`

`make_figures.py` writes the PNG figures, at 300 dpi.

**Full path.** Run the steps in order. Each notebook has a cell at the top with its input and output folders. Set them to the folders of this repository, because the original runs used local Windows and Colab paths.

| Step | File | Input | Output |
|---|---|---|---|
| 1 | `scripts/01_collect_image_urls.py` | data.gov.sg API | image links per camera and time stamp |
| 2 | `scripts/02_collect_google_speeds.py` | Google Maps API key, `data/cameras/google_od_pairs.csv` | travel times (new data only, since the API does not return past travel times) |
| 3 | `notebooks/03_detect_vehicles_maskrcnn.ipynb` | image links | Mask R-CNN detections |
| 4 | `notebooks/04_count_vehicles_by_direction.ipynb` | detections, `camera_masks.csv`, travel times | features per image and direction |
| 5 | `notebooks/05_summaries_for_figures.ipynb` | outputs of step 4 | `data/figure_inputs/` |
| 6 | `notebooks/06_build_model_inputs.ipynb` | outputs of step 4 | model input files |
| 7 | `notebooks/models_*/b_PIE.ipynb`, `b_Woodlands.ipynb`, `2way.ipynb` | model input files | selected models and June predictions |
| 8 | `notebooks/models_*/speed_prediction_Result_Analysis.ipynb` | outputs of step 7 | error tables and the February and July figures |
| 9 | `scripts/benchmarks.py`, `scripts/make_figures.py` | outputs of steps 5 and 7 | benchmark tables and figures |

To run step 2 you need your own key, set as an environment variable and never written into a file:

```bash
export GOOGLE_MAPS_API_KEY="your-key"     # Windows: set GOOGLE_MAPS_API_KEY=your-key
```

**Known gaps.**
- The notebook used to run DETR was not preserved. Its outputs, every DETR detection, are in the Zenodo data record, so every later step can be reproduced.
- The 2,000 images annotated to measure detection accuracy are not included.
- Hyperparameter search and LSTM training on a GPU are not fully deterministic. Retraining can give slightly different numbers from the saved predictions, which are the ones reported in the paper.

## Citation

If you use this code or data, please cite the paper and the Zenodo archive (see `CITATION.cff`):

- Paper: *to be added on acceptance*
- Code and data: Zenodo, DOI *to be added on release*

## Contact

Francisco Benita, School of Engineering and Sciences, Tecnologico de Monterrey.
