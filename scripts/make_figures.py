import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import pandas as pd

BASE = r"C:\Users\Traffic_Cameras"
if len(sys.argv) > 1:
    BASE = sys.argv[1]
DATA = os.path.join(BASE, "Data")
RESULTS = os.path.join(BASE, "Results")
FIGS = sys.argv[2] if len(sys.argv) > 2 else os.path.join(RESULTS, "Figures")
os.makedirs(FIGS, exist_ok=True)

# Colours of the R script (ggplot palette cbp1, first three values for Bus, Truck, Car)
VEHICLE_COLOURS = {"Bus": "#999999", "Truck": "#E69F00", "Car": "#56B4E9"}
VEHICLES = ["Bus", "Truck", "Car"]          # stacking order of the R plots, bottom to top
DIRECTIONS = ["Direction: North", "Direction: South"]
ROUTE_TO_DIRECTION = {"b_Woodlands": "Direction: North", "b_PIE": "Direction: South"}

plt.rcParams.update({
    "font.size": 16, "axes.titlesize": 16, "axes.labelsize": 18,
    "xtick.labelsize": 14, "ytick.labelsize": 14, "legend.fontsize": 14,
    "axes.spines.top": False, "axes.spines.right": False,
})


def path(*parts):
    return os.path.join(*parts)


def save(fig, name):
    out = path(FIGS, name)
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("saved", out)


def have(*files):
    missing = [f for f in files if not os.path.exists(f)]
    for f in missing:
        print("  missing input, figure skipped:", f)
    return not missing


def strip_label(ax, text):
    """Facet label on the right-hand side, as facet_grid(direction ~ .) does in ggplot."""
    ax.annotate(text, xy=(1.01, 0.5), xycoords="axes fraction", rotation=270,
                va="center", ha="left", fontsize=15,
                bbox=dict(boxstyle="square,pad=0.3", fc="#e6e6e6", ec="none"))


# ---------------------------------------------------------------------------
# 1. Vehicle counts by hour, with and without the Google speed line
# ---------------------------------------------------------------------------
COUNT_FOLDERS = {
    "MaskR-CNN": ("count_of_vehicles", ""),
    "Transformer": ("count_of_vehicles_transformer", "_Transformer"),
}


def count_files(detector, daytype):
    folder, suffix = COUNT_FOLDERS[detector]
    return {route: path(DATA, folder, f"{route}Average_vehicles_per_Time_on_{daytype}{suffix}.csv")
            for route in ("b_Woodlands", "b_PIE")}


def load_counts(detector, daytype):
    """Long table with Time, direction, Vehicle and Value (average vehicles per image), as df_long in R."""
    frames = []
    for route, f in count_files(detector, daytype).items():
        d = pd.read_csv(f)[["Time", "total_car", "total_truck", "total_bus"]]
        d = d.rename(columns={"total_car": "Car", "total_truck": "Truck", "total_bus": "Bus"})
        d["direction"] = ROUTE_TO_DIRECTION[route]
        frames.append(d)
    wide = pd.concat(frames, ignore_index=True)
    return wide.melt(id_vars=["Time", "direction"], value_vars=VEHICLES, var_name="Vehicle", value_name="Value")


def hourly(long):
    """Sum of the twelve five-minute averages of each hour, hour 04 removed."""
    d = long.copy()
    d["Hour"] = d["Time"].astype(str).str.zfill(5).str[:2]
    d = d.groupby(["Hour", "direction", "Vehicle"], as_index=False)["Value"].sum()
    return d[d["Hour"] != "04"]


def load_speed(daytype):
    f = path(RESULTS, "Google_avg_speed", "march_june_avg_speed_per_route 1.csv")
    s = pd.read_csv(f)
    s["direction"] = np.where(s["Route"] == "b_PIE", "Direction: South", "Direction: North")
    s["Hour"] = s["hour"].astype(int).map(lambda h: f"{h:02d}")
    keep = "weekday" if daytype == "weekdays" else "weekend"
    return s[s["day_type"] == keep][["Hour", "direction", "avg_speed"]]


def plot_density(detector, daytype, fname):
    if not have(*count_files(detector, daytype).values()):
        return
    long = load_counts(detector, daytype)
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    for ax, direction in zip(axes, DIRECTIONS):
        sub = long[long["direction"] == direction]
        for v in VEHICLES:
            x = sub.loc[sub["Vehicle"] == v, "Value"].dropna().to_numpy(float)
            if len(x) < 2 or np.std(x) == 0:
                continue
            grid = np.linspace(min(0, x.min()), x.max() * 1.05, 400)
            bw = 1.06 * np.std(x) * len(x) ** (-1 / 5)          # Gaussian kernel, normal reference bandwidth
            dens = np.exp(-0.5 * ((grid[:, None] - x[None, :]) / bw) ** 2).sum(1) / (len(x) * bw * np.sqrt(2 * np.pi))
            ax.plot(grid, dens, color=VEHICLE_COLOURS[v], label=v)
            ax.fill_between(grid, dens, color=VEHICLE_COLOURS[v], alpha=0.1)
        ax.set_ylabel("Density")
        strip_label(ax, direction)
    axes[-1].set_xlabel("Number of vehicles")
    axes[0].legend(title="Vehicle", frameon=False, loc="upper right")
    save(fig, fname)


def plot_hourly(detector, daytype, fname, with_speed, ylim=(0, 2000)):
    files = list(count_files(detector, daytype).values())
    if with_speed:
        files.append(path(RESULTS, "Google_avg_speed", "march_june_avg_speed_per_route 1.csv"))
    if not have(*files):
        return
    counts = hourly(load_counts(detector, daytype))
    speed = load_speed(daytype) if with_speed else None
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    hours = sorted(counts["Hour"].unique())
    x = np.arange(len(hours))
    for ax, direction in zip(axes, DIRECTIONS):
        sub = counts[counts["direction"] == direction].pivot(index="Hour", columns="Vehicle", values="Value")
        sub = sub.reindex(hours).fillna(0)
        bottom = np.zeros(len(hours))
        for v in VEHICLES:
            ax.bar(x, sub[v].to_numpy(), bottom=bottom, color=VEHICLE_COLOURS[v], width=0.9, label=v)
            bottom += sub[v].to_numpy()
        if ylim is not None:
            ax.set_ylim(*ylim)
        ax.set_ylabel("Average number\nof vehicles")
        if with_speed:
            sp = speed[speed["direction"] == direction].set_index("Hour").reindex(hours)["avg_speed"]
            ax2 = ax.twinx()
            ax2.spines["right"].set_visible(True)
            ax2.plot(x, sp.to_numpy(), color="red", linewidth=2.5, label="Speed")
            ax2.set_ylim(0, 100)
            ax2.set_ylabel("Average speed\n(km/h)")
            ax.annotate(direction, xy=(1.13, 0.5), xycoords="axes fraction", rotation=270, va="center",
                        ha="left", fontsize=15, bbox=dict(boxstyle="square,pad=0.3", fc="#e6e6e6", ec="none"))
        else:
            strip_label(ax, direction)
    axes[-1].set_xticks(x)
    axes[-1].set_xticklabels(hours, rotation=0)
    axes[-1].set_xlabel("Hour")
    handles, labels = axes[0].get_legend_handles_labels()
    if with_speed:
        handles.append(plt.Line2D([0], [0], color="red", linewidth=2.5))
        labels.append("Speed")
    fig.legend(handles[::-1] if not with_speed else handles, labels[::-1] if not with_speed else labels,
               loc="lower center", ncol=len(labels), frameon=False, bbox_to_anchor=(0.5, -0.04))
    save(fig, fname)


def counts_figures():
    for daytype in ("weekdays", "weekends"):
        plot_density("MaskR-CNN", daytype, f"Traffic_on_{daytype}_MaskR-CNN.png")
        plot_hourly("MaskR-CNN", daytype, f"Traffic_on_{daytype}_per_hour_MaskR-CNN.png", with_speed=False)
        plot_hourly("MaskR-CNN", daytype, f"Traffic_on_{daytype}_per_hour_MaskR-CNN_with_speed.png", with_speed=True)
    plot_density("Transformer", "weekdays", "Traffic_on_weekdays_Transformer.png")
    plot_density("Transformer", "weekends", "Traffic_on_weekends_transformer.png")
    # As in the R script, the DETR bars without speed are not capped at 2,000
    plot_hourly("Transformer", "weekdays", "Traffic_on_weekdays_per_hour_transformer.png", with_speed=False, ylim=None)
    plot_hourly("Transformer", "weekends", "Traffic_on_weekends_per_hour_transformer.png", with_speed=False, ylim=None)
    plot_hourly("Transformer", "weekdays", "Traffic_on_weekdays_per_hour_Transformer_with_speed.png", with_speed=True)
    # File name kept exactly as in the R script and the LaTeX source ("weekend", singular)
    plot_hourly("Transformer", "weekends", "Traffic_on_weekend_per_hour_Transformer_with_speed.png", with_speed=True)


# ---------------------------------------------------------------------------
# 2. Detection confidence scores
# ---------------------------------------------------------------------------
def grouped_boxplot(ax, groups, hues, data, colours, value, group_col, hue_col, width=0.8):
    n = len(hues)
    w = width / n
    for i, g in enumerate(groups):
        for j, h in enumerate(hues):
            vals = data.loc[(data[group_col] == g) & (data[hue_col] == h), value].dropna().to_numpy()
            if len(vals) == 0:
                continue
            pos = i - width / 2 + w * (j + 0.5)
            bp = ax.boxplot(vals, positions=[pos], widths=w * 0.9, patch_artist=True, showfliers=True,
                            flierprops=dict(marker="o", markersize=2, alpha=0.3, markeredgecolor="black"),
                            medianprops=dict(color="black"))
            for patch in bp["boxes"]:
                patch.set_facecolor(colours[j])
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels(groups)


def plot_scores():
    f_rcnn = path(RESULTS, "Accuracy", "maskrcnn_march_june_vehicle_summary.csv")
    f_detr = path(RESULTS, "Accuracy", "transformer_march_june_vehicle_summary.csv")
    if not have(f_rcnn, f_detr):
        return
    rcnn = pd.read_csv(f_rcnn, usecols=lambda c: c in ("Detection_Score", "Route", "Detection_Class"))
    detr = pd.read_csv(f_detr, usecols=lambda c: c in ("Detection_Score", "Route", "Detection_Class"))
    rcnn["Source"] = "Mask R-CNN"
    detr["Source"] = "DETR"
    filt = rcnn[rcnn["Detection_Score"] > 0.3].copy()        # same rule as the R script and the paper
    filt["Source"] = "Mask R-CNN (score > 0.3)"
    d = pd.concat([rcnn, filt, detr], ignore_index=True)
    d["direction"] = np.where(d["Route"] == "b_PIE", "Direction: South", "Direction: North")
    groups = ["Mask R-CNN", "Mask R-CNN (score > 0.3)", "DETR"]
    hues = DIRECTIONS
    colours = ["#66c2a5", "#fc8d62"]
    fig, ax = plt.subplots(figsize=(12, 8))
    grouped_boxplot(ax, groups, hues, d, colours, "Detection_Score", "Source", "direction")
    ax.set_ylabel("Detection score")
    ax.legend([plt.Rectangle((0, 0), 1, 1, fc=c, ec="black") for c in colours], hues,
              loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=2, frameon=False)
    save(fig, "Boxplots_with_acc.png")


# ---------------------------------------------------------------------------
# 3. Accuracy with and without the 0.3 score filter (Mask R-CNN, M2)
# ---------------------------------------------------------------------------
def plot_filter_bars():
    f = path(RESULTS, "Tables_paper.xlsx")
    if not have(f):
        return
    df = pd.read_excel(f, sheet_name="Table rcnn acc")
    for c in ("RMSE", "MAE", "EVS"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["Direction"] = np.where(df["Direction"] == "b_Woodlands", "North", "South")
    means = df.groupby(["Direction", "Filter"])[["RMSE", "MAE", "EVS"]].mean()
    filters = list(dict.fromkeys(df["Filter"]))
    colours = ["#1f78b4", "#e31a1c"]
    fig, axes = plt.subplots(1, 3, figsize=(10, 6))
    x = np.arange(2)
    w = 0.8 / len(filters)
    for ax, metric in zip(axes, ("RMSE", "MAE", "EVS")):
        for j, flt in enumerate(filters):
            vals = [means.loc[(dirn, flt), metric] if (dirn, flt) in means.index else np.nan
                    for dirn in ("North", "South")]
            ax.bar(x - 0.4 + w * (j + 0.5), vals, width=w, color=colours[j % 2], label=str(flt))
        ax.set_xticks(x)
        ax.set_xticklabels(["North", "South"])
        ax.set_title(metric)
        ax.set_xlabel("Direction")
    axes[0].set_ylabel("Value")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=len(labels), frameon=False, bbox_to_anchor=(0.5, -0.06))
    fig.tight_layout()
    save(fig, "Barplot_errors_filtered_accuracy.png")


# ---------------------------------------------------------------------------
# 4a. Violin plot of forecast errors (port of the R figure, with the 15-minute XGB bug fixed)
# ---------------------------------------------------------------------------
def plot_forecast_violins():
    files = {(det, r): path(DATA, "Deviations_Forecasting", f"{r}_{det}.csv")
             for det in ("rcnn", "transformer") for r in ("b_Woodlands", "b_PIE")}
    if not have(*files.values()):
        return
    horizons = [("1", "t+1 (5 min)"), ("3", "t+3 (15 min)"), ("6", "t+6 (30 min)")]
    models = [("lstm", "LSTM", "#8dd3c7"), ("xgb", "XGB", "#ffffb3")]
    fig, axes = plt.subplots(1, 2, figsize=(12, 8), sharey=True)
    for ax, (det, title) in zip(axes, [("rcnn", "Mask R-CNN"), ("transformer", "DETR")]):
        d = pd.concat([pd.read_csv(files[(det, "b_Woodlands")]), pd.read_csv(files[(det, "b_PIE")])])
        for i, (k, _) in enumerate(horizons):
            for j, (m, _, colour) in enumerate(models):
                # The R script used xgb_m2_1_diff for the XGB 15-minute violin; the correct column is used here
                vals = d[f"{m}_m2_{k}_diff"].dropna().to_numpy()
                parts = ax.violinplot(vals, positions=[i + (j - 0.5) * 0.4], widths=0.38, showextrema=False)
                for b in parts["bodies"]:
                    b.set_facecolor(colour)
                    b.set_edgecolor("black")
                    b.set_alpha(1)
        ax.axhline(0, linestyle="--", color="black")
        ax.set_xticks(range(3))
        ax.set_xticklabels([h for _, h in horizons])
        ax.set_title(title)
        ax.set_xlabel("Horizon")
        ax.set_yticks(range(-50, 51, 10))
    axes[0].set_ylabel("Deviation (km/hr)")
    fig.legend([plt.Rectangle((0, 0), 1, 1, fc=c, ec="black") for _, _, c in models], [n for _, n, _ in models],
               loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.04))
    save(fig, "Boxplots_forecasting_violins.png")


# ---------------------------------------------------------------------------
# 4b. Replacement figure: estimation error by the size of the departure from the usual speed
# ---------------------------------------------------------------------------
DEPARTURE_BINS = [-np.inf, -20, -10, -5, 5, 10, np.inf]
DEPARTURE_LABELS = ["below \u221220", "\u221220 to \u221210", "\u221210 to \u22125", "\u22125 to 5", "5 to 10", "above 10"]
METHODS = [  # column (or rule), legend label, colour, marker, line style
    ("profile", "Historical profile", "#4d4d4d", "s", "-"),
    ("xgb", "XGB (images)", "#1f78b4", "o", "-"),
    ("lstm", "LSTM (images)", "#33a02c", "^", "-"),
    ("avg", "Average of XGB and profile", "#e31a1c", "D", "--"),
]


def plot_error_by_departure():
    # Looked for in Data first, then next to this script
    candidates = [path(DATA, "test_week_current_speed.csv"),
                  path(os.path.dirname(FIGS.rstrip("/\\")), "test_week_current_speed.csv"),
                  path(os.path.dirname(os.path.abspath(__file__)), "test_week_current_speed.csv")]
    f = next((c for c in candidates if os.path.exists(c)), candidates[0])
    if not have(f):
        print("  test_week_current_speed.csv is written by benchmarks.py; copy it into the Data folder")
        return
    d = pd.read_csv(f)
    d["avg"] = 0.5 * (d["xgb"] + d["profile"])
    d["departure"] = d["observed"] - d["profile"]
    d["bin"] = pd.cut(d["departure"], DEPARTURE_BINS, labels=DEPARTURE_LABELS, right=True)
    detectors = ["Mask R-CNN", "DETR"]
    directions = ["North", "South"]
    fig, axes = plt.subplots(2, 2, figsize=(12, 8.5), sharex=True, sharey=True)
    x = np.arange(len(DEPARTURE_LABELS))
    for r, det in enumerate(detectors):
        for c, dirn in enumerate(directions):
            ax = axes[r, c]
            sub = d[(d["detector"] == det) & (d["direction"] == dirn)]
            g = sub.groupby("bin", observed=False)
            for col, label, colour, marker, ls in METHODS:
                rmse = g.apply(lambda t: np.sqrt(np.mean((t["observed"] - t[col]) ** 2)) if len(t) else np.nan)
                ax.plot(x, rmse.to_numpy(), marker=marker, color=colour, linestyle=ls, linewidth=1.8,
                        markersize=7, label=label)
            ax.set_yscale("log")
            ax.set_yticks([2, 5, 10, 20, 40])
            ax.set_yticklabels(["2", "5", "10", "20", "40"])
            ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
            ax.grid(axis="y", color="#dddddd", linewidth=0.8)
            ax.set_title(f"{det}, {dirn.lower()}bound", fontsize=15)
            if r == 1:
                n = g.size().reindex(DEPARTURE_LABELS).fillna(0).astype(int)
                ax.set_xticks(x)
                ax.set_xticklabels([f"{lab}\n(n={k})" for lab, k in zip(DEPARTURE_LABELS, n)], fontsize=11)
                ax.set_xlabel("Observed minus profile speed (km/h)")
            if c == 0:
                ax.set_ylabel("RMSE (km/h, log scale)")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, -0.05), fontsize=13)
    fig.tight_layout()
    save(fig, "Errors_by_departure.png")


if __name__ == "__main__":
    print("Reading from", BASE)
    counts_figures()
    plot_scores()
    plot_filter_bars()
    plot_forecast_violins()
    plot_error_by_departure()
