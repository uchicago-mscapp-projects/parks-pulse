import shapely
import pathlib
import pandas as pd
from clean_hazards import clean_fire_data, clean_boundary


def fire_mapping():
    """
    This function links fire records to the national parks in which they
    occured by coordinates.

    Inputs: None

    Returns: (.csv)
        Cleaned .csv file of fires mapped to national parks.
    """
    boundary = clean_boundary()
    fire = clean_fire_data()
    fire["park_name"] = None
    fire["park_id"] = None
    
    for i, fire_row in fire.iterrows():
        point = shapely.geometry.Point(fire_row["X"], fire_row["Y"])
        for _, boundary_row in boundary.iterrows():
            if fire_row["state"] == boundary_row["state"]:
                if point.within(boundary_row["bbox"]):
                    fire["park_name"].values[i] = boundary_row["park_name"]
                    fire["park_id"].values[i] = boundary_row["park_id"]
                    break
                break

    fire.dropna(inplace=True)
    fire.to_csv(pathlib.Path(__file__).parent / "cleaned_data/np-fires.csv", index=False)


def fire_processing():
    """
    This function processes linked fires file to produce analysis-relevant
    fire records by annual count and acres burnt.

    Inputs: None

    Returns: (.csv)
        Cleaned .csv files of fires mapped to national parks, by annual count
        and total acress burnt.
    """
    filename = pathlib.Path(__file__).parent / "cleaned_data/np-fires.csv"
    cols_to_use = ["park_name", "state", "discovery_date", "acres"]
    df = pd.read_csv(filename, usecols=cols_to_use)

    df["year"] = pd.DatetimeIndex(df["discovery_date"]).year
    df = df.drop("discovery_date", axis=1)

    time_series_acres = df.groupby(["park_name", "year"])["acres"].sum().to_frame(name = 'acres_burnt').reset_index()
    time_series_count = df.groupby(["park_name", "year"])["year"].size().to_frame(name = 'count').reset_index()

    time_series_count.to_csv(pathlib.Path(__file__).parent /
                             "cleaned_data/np-fires-annual.csv", index=False)
    time_series_acres.to_csv(pathlib.Path(__file__).parent /
                             "cleaned_data/np-fires-annual-acres.csv", index=False)
