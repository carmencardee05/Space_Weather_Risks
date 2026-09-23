"""
Process Space-Track orbital history into daily satellite altitude data.

1. Load raw Space-Track GP history data.
2. Convert satellite mean motion to approximate orbital altitude.
3. Puts all the observations together into daily median altitude measurements.
"""

from pathlib import Path
import json

import pandas as pd

from orbital_altitude import mean_motion_to_altitude_km



# Paths



# parent.parent gives the repository root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

PROCESSED_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

INPUT_FILE = RAW_DATA_DIR / (
    "gp_history_25544_43013_40967_33591_37849_39444_"
    "40697_43205_27424_25994_27651_39084_"
    "2017-12-02_to_2019-01-30.json"
)

ALTITUDE_FILE = (
    PROCESSED_DATA_DIR
    / "satellite_altitudes_2017-12-02_to_2019-01-30.csv"
)

DAILY_ALTITUDE_FILE = (
    PROCESSED_DATA_DIR
    / "daily_satellite_altitudes_2017-12-02_to_2019-01-30.csv"
)



# Load and process orbital data


def process_orbital_history():

    print(f"Loading orbital data from:\n{INPUT_FILE}")

    # Give an error if the raw file is missing
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"\nCould not find the Space-Track file:\n"
            f"{INPUT_FILE}\n\n"
            f"Make sure the JSON file is inside:\n"
            f"{RAW_DATA_DIR}"
        )

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        records = json.load(file)

    rows = []

    for record in records:

        try:
            norad_id = int(
                record["NORAD_CAT_ID"]
            )

            object_name = record.get(
                "OBJECT_NAME",
                "",
            )

            epoch = pd.to_datetime(
                record["EPOCH"],
                errors="coerce",
                utc=True,
            )

            mean_motion = float(
                record["MEAN_MOTION"]
            )

            eccentricity = float(
                record.get(
                    "ECCENTRICITY",
                    float("nan"),
                )
            )

            inclination = float(
                record.get(
                    "INCLINATION",
                    float("nan"),
                )
            )

            semi_major_axis, altitude = (
                mean_motion_to_altitude_km(
                    mean_motion
                )
            )

            rows.append(
                {
                    "norad_id": norad_id,
                    "object_name": object_name,
                    "epoch": epoch,
                    "mean_motion_rev_day": mean_motion,
                    "eccentricity": eccentricity,
                    "inclination_deg": inclination,
                    "semi_major_axis_km": semi_major_axis,
                    "altitude_km": altitude,
                }
            )

        except (
            KeyError,
            TypeError,
            ValueError,
        ) as error:

            print(
                f"Skipping invalid record: {error}"
            )

    df = pd.DataFrame(rows)

    if df.empty:
        raise ValueError(
            "No valid orbital records were found."
        )

    df = df.dropna(
        subset=["epoch"]
    )

    df = df.sort_values(
        ["norad_id", "epoch"]
    ).reset_index(
        drop=True
    )

    df.to_csv(
        ALTITUDE_FILE,
        index=False,
    )

    print(
        f"\nSaved {len(df)} processed "
        f"orbital observations to:\n"
        f"{ALTITUDE_FILE}"
    )

    return df


# Calculate daily satellite altitude


def calculate_daily_altitudes(df):

    df = df.copy()

    # Convert each observation timestamp to its UTC day
    df["date"] = (
        df["epoch"].dt.floor("D")
    )

    # Take the median altitude for each satellite
    # on each day
    daily = (
        df.groupby(
            [
                "norad_id",
                "object_name",
                "date",
            ],
            as_index=False,
        )["altitude_km"]
        .median()
        .rename(
            columns={
                "altitude_km":
                "daily_median_altitude_km"
            }
        )
    )

    daily.to_csv(
        DAILY_ALTITUDE_FILE,
        index=False,
    )

    print(
        f"\nSaved {len(daily)} daily "
        f"satellite observations to:\n"
        f"{DAILY_ALTITUDE_FILE}"
    )

    return daily


# Run pipeline


def main():

    orbital_data = (
        process_orbital_history()
    )

    daily_data = (
        calculate_daily_altitudes(
            orbital_data
        )
    )

    print("\nSatellites processed:")

    print(
        daily_data[
            [
                "norad_id",
                "object_name",
            ]
        ]
        .drop_duplicates()
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()