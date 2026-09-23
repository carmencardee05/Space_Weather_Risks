from pathlib import Path

import pandas as pd
import requests


# Configuration

START_DATE = "2017-12-02T00:00:00Z"
END_DATE = "2019-01-30T23:59:59Z"

API_URL = "https://kp.gfz.de/app/json/"

OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "kp_daily_2017-12-02_to_2019-01-30.csv"


def main():

    params = {
        "start": START_DATE,
        "end": END_DATE,
        "index": "Kp",
        "status": "def",
    }

    print(
        f"Downloading Kp data from {START_DATE} "
        f"to {END_DATE}..."
    )

    response = requests.get(
        API_URL,
        params=params,
        timeout=60,
    )

    response.raise_for_status()

    # Get JSON response from GFZ
    data = response.json()

    # Build DataFrame from the timestamp and Kp arrays
    df = pd.DataFrame({
        "date": data["datetime"],
        "Kp": data["Kp"],
    })

    # Convert timestamps
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
        utc=True,
    )

    # Make sure Kp is numeric
    df["Kp"] = pd.to_numeric(
        df["Kp"],
        errors="coerce",
    )

    # Remove invalid rows
    df = df.dropna(
        subset=["date", "Kp"]
    ).copy()

    # Convert 3-hour Kp measurements to daily maximum Kp
    daily_kp = (
        df.groupby(
            df["date"].dt.floor("D")
        )["Kp"]
        .max()
        .reset_index()
        .rename(
            columns={
                "Kp": "daily_max_kp"
            }
        )
    )

    # Save CSV
    daily_kp.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print(f"Saved {len(daily_kp)} daily observations.")
    print(f"Output: {OUTPUT_FILE}")

    print("\nFirst 5 rows:")
    print(daily_kp.head())

    print("\nLast 5 rows:")
    print(daily_kp.tail())


if __name__ == "__main__":
    main()