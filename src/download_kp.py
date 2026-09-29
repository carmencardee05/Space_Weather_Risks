from pathlib import Path

import pandas as pd
import requests



# Configuration


# Starlink Group 4-7 event window
START_DATE = "2022-02-01T00:00:00Z"
END_DATE = "2022-02-15T23:59:59Z"

API_URL = "https://kp.gfz.de/app/json/"



# Paths


PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# full 3-hour Kp measurements
KP_3H_FILE = (
    OUTPUT_DIR
    / "kp_3hour_2022-02-01_to_2022-02-15.csv"
)


# Save daily maximum Kp values
DAILY_KP_FILE = (
    OUTPUT_DIR
    / "kp_daily_2022-02-01_to_2022-02-15.csv"
)



# Download Kp


def main():

    params = {
        "start": START_DATE,
        "end": END_DATE,
        "index": "Kp",
        "status": "def",
    }


    print(
        f"Downloading Kp data from "
        f"{START_DATE} to {END_DATE}..."
    )


    response = requests.get(
        API_URL,
        params=params,
        timeout=60,
    )

    response.raise_for_status()


    data = response.json()


   
    # Build 3 hr kp dataframe
   

    df = pd.DataFrame(
        {
            "datetime":
                data["datetime"],

            "Kp":
                data["Kp"],
        }
    )


    # Convert timestamps
    df["datetime"] = pd.to_datetime(
        df["datetime"],
        errors="coerce",
        utc=True,
    )


   
    df["Kp"] = pd.to_numeric(
        df["Kp"],
        errors="coerce",
    )


    # Remove invalid rows
    df = df.dropna(
        subset=[
            "datetime",
            "Kp",
        ]
    ).copy()


    
    # Classify geomagnetic storm measurements
 

    # Kp >= 5 corresponds to geomagnetic storm conditions
    df["storm"] = (
        df["Kp"]
        >= 5
    )




    df.to_csv(
        KP_3H_FILE,
        index=False,
    )


    print(
        f"\nSaved {len(df)} "
        f"3-hour Kp observations."
    )

    print(
        f"Output:\n"
        f"{KP_3H_FILE}"
    )


    # Calculate daily maximum Kp


    df["date"] = (
        df["datetime"]
        .dt.floor("D")
    )


    daily_kp = (
        df.groupby(
            "date",
            as_index=False,
        )["Kp"]
        .max()
        .rename(
            columns={
                "Kp":
                    "daily_max_kp"
            }
        )
    )


    # Classify storm days
    daily_kp["storm_day"] = (
        daily_kp[
            "daily_max_kp"
        ]
        >= 5
    )


    # Save daily Kp
   

    daily_kp.to_csv(
        DAILY_KP_FILE,
        index=False,
    )


    print(
        f"\nSaved {len(daily_kp)} "
        f"daily Kp observations."
    )

    print(
        f"Output:\n"
        f"{DAILY_KP_FILE}"
    )


    # Print results

    print(
        "\n3-hour Kp measurements:\n"
    )

    print(
        df[
            [
                "datetime",
                "Kp",
                "storm",
            ]
        ].to_string(
            index=False
        )
    )


    print(
        "\nDaily maximum Kp:\n"
    )

    print(
        daily_kp.to_string(
            index=False
        )
    )


    # Show storm measurements
    storms = df[
        df["storm"]
    ]

    print(
        "\nKp >= 5 measurements:\n"
    )

    if storms.empty:

        print(
            "No Kp >= 5 measurements "
            "were found."
        )

    else:

        print(
            storms[
                [
                    "datetime",
                    "Kp",
                ]
            ].to_string(
                index=False
            )
        )


if __name__ == "__main__":
    main()