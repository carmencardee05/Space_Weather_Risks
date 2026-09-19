"""
script:
1. Loads daily satellite altitude data.
2. Loads daily Kp geomagnetic activity.
3. Calculates daily altitude changes.
4. Classifies storm and quiet days.
5. Compares orbital decay between the two conditions.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


PROCESSED_DATA_DIR = Path("data/processed")
RESULTS_DIR = Path("results")

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

ALTITUDE_FILE = (
    PROCESSED_DATA_DIR
    / "daily_satellite_altitudes_2017-12-02_to_2019-01-30.csv"
)

KP_FILE = (
    PROCESSED_DATA_DIR
    / "kp_daily_2017-12-02_to_2019-01-30.csv"
)

MERGED_FILE = (
    PROCESSED_DATA_DIR
    / "daily_satellite_altitude_kp.csv"
)

RESULTS_FILE = (
    RESULTS_DIR
    / "storm_vs_quiet_decay.csv"
)

# Kp >= 5 corresponds to geomagnetic storm conditions
STORM_THRESHOLD = 5

# Satellites selected from exploratory analysis because their
# altitude histories show relatively clear natural decay trends.
ANALYSIS_SATELLITES = [
    27651,
    33591,
    39444,
]



# Load and merge data


def load_and_merge_data():

    altitude = pd.read_csv(ALTITUDE_FILE)
    kp = pd.read_csv(KP_FILE)

    altitude["date"] = pd.to_datetime(
        altitude["date"],
        errors="coerce",
        utc=True,
    )

    kp["date"] = pd.to_datetime(
        kp["date"],
        errors="coerce",
        utc=True,
    )

    altitude = altitude.dropna(subset=["date"]).copy()
    kp = kp.dropna(subset=["date"]).copy()

    merged = altitude.merge(
        kp,
        on="date",
        how="inner",
    )

    merged = merged.sort_values(
        ["norad_id", "date"]
    ).reset_index(drop=True)

    merged.to_csv(
        MERGED_FILE,
        index=False,
    )

    print(f"Merged observations: {len(merged)}")

    return merged



# Calculate daily altitude changes


def calculate_altitude_change(df):

    df = df.copy()

    df["daily_altitude_change_km"] = (
        df.groupby("norad_id")[
            "daily_median_altitude_km"
        ].diff()
    )

    # Negative altitude change indicates orbital decay.
    # Convert decay to a positive quantity for easier interpretation.
    df["orbital_decay_km"] = (
        -df["daily_altitude_change_km"]
    )

    df["storm_day"] = (
        df["daily_max_kp"] >= STORM_THRESHOLD
    )

    return df



# Analyze individual satellites


def analyze_satellites(df):

    results = []

    for norad_id in ANALYSIS_SATELLITES:

        satellite = df[
            df["norad_id"] == norad_id
        ].dropna(
            subset=[
                "orbital_decay_km",
                "daily_max_kp",
            ]
        )

        if satellite.empty:
            print(
                f"No observations available for {norad_id}."
            )
            continue

        storm = satellite[
            satellite["storm_day"]
        ]

        quiet = satellite[
            ~satellite["storm_day"]
        ]

        if len(storm) < 5 or len(quiet) < 5:
            print(
                f"Not enough observations for {norad_id}."
            )
            continue

        storm_decay = storm[
            "orbital_decay_km"
        ].mean()

        quiet_decay = quiet[
            "orbital_decay_km"
        ].mean()

        extra_decay = (
            storm_decay - quiet_decay
        )

        # Pearson correlation between Kp and orbital decay
        correlation, p_value = stats.pearsonr(
            satellite["daily_max_kp"],
            satellite["orbital_decay_km"],
        )

        # Relative increase in decay during storm conditions
        if quiet_decay != 0:

            decay_ratio = (
                storm_decay / quiet_decay
            )

            percent_change = (
                (storm_decay - quiet_decay)
                / abs(quiet_decay)
                * 100
            )

        else:
            decay_ratio = np.nan
            percent_change = np.nan

        results.append(
            {
                "norad_id": norad_id,
                "storm_observations": len(storm),
                "quiet_observations": len(quiet),
                "storm_mean_decay_km_day": storm_decay,
                "quiet_mean_decay_km_day": quiet_decay,
                "extra_decay_km_day": extra_decay,
                "storm_to_quiet_ratio": decay_ratio,
                "percent_change": percent_change,
                "pearson_r": correlation,
                "pearson_p_value": p_value,
            }
        )

    results_df = pd.DataFrame(results)

    results_df.to_csv(
        RESULTS_FILE,
        index=False,
    )

    return results_df



# Run analysis


def main():

    data = load_and_merge_data()

    data = calculate_altitude_change(data)

    results = analyze_satellites(data)

    print("\nStorm vs. quiet orbital decay results:\n")

    print(
        results.to_string(index=False)
    )

    print(
        f"\nResults saved to:\n{RESULTS_FILE}"
    )


if __name__ == "__main__":
    main()
