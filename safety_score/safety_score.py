import pandas as pd
import os

def min_max_normalize(val, min_val, max_val):
    """Min-max normalization of a value.

    Args:
        val (float): The value to normalize.
        min_val (float): The minimum value in the dataset.
        max_val (float): The maximum value in the dataset.

    Returns:
        float: Normalized value between 0 and 100.
    """
    if max_val == min_val:
        return 50  # default score when data is insufficient
    return round(100 * (1 - (val - min_val) / (max_val - min_val)))


def get_population_with_type(df, neighbourhood, year):
    """Get population for a neighbourhood in a specific year and check if census data is available for that year.

    Args:
        df (pd.DataFrame): DataFrame containing population data.
        neighbourhood (str): The name of the neighbourhood.
        year (int): The year for which to get the population.

    Raises:
        ValueError: If the year is not between 2001 and 2024.

    Returns:
        tuple: A tuple containing the population and a boolean indicating if census data is available for that year.
    """
    if year < 2001 or year > 2024:
        raise ValueError("Year must be between 2001 and 2024.")
    data = df[df["neighbourhood"] == neighbourhood]
    return get_population(df, neighbourhood, year), (year in data["year"].values)


def get_population(df, neighbourhood, year):
    """Get population for a neighbourhood in a specific year.

    Args:
        df (pd.DataFrame): DataFrame containing population data.
        neighbourhood (str): The name of the neighbourhood.
        year (int): The year for which to get the population.

    Raises:
        ValueError: If the year is not between 2001 and 2024.

    Returns:
        int: The population of the neighbourhood in the specified year.
    """
    if year < 2001 or year > 2024:
        raise ValueError("Year must be between 2001 and 2024.")

    data = df[df["neighbourhood"] == neighbourhood]
    # Check if census data is available for this year
    if year in data["year"].values:
        return int(data.loc[data["year"] == year, "population"].values[0])

    available_years = sorted(data["year"].values)
    # extrapolation with dampening factor
    if year > available_years[-1]:
        if len(available_years) < 2:
            return int(data.loc[data["year"] == available_years[-1], "population"].values[0])

        # Use last two data points for extrapolation
        pop_recent = data.loc[data["year"] == available_years[-1], "population"].values[0]
        pop_previous = data.loc[data["year"] == available_years[-2], "population"].values[0]
        years_diff = available_years[-1] - available_years[-2]

        growth_rate = (pop_recent - pop_previous) / years_diff
        dampened_rate = growth_rate * 0.8  # dampening factor of 0.8
        return int(pop_recent + (year - available_years[-1]) * dampened_rate)

    # interpolation
    lower_year = max([y for y in available_years if y <= year])
    upper_year = min([y for y in available_years if y >= year])
    if lower_year == upper_year:
        return int(data.loc[data["year"] == lower_year, "population"].values[0])

    pop_lower = data.loc[data["year"] == lower_year, "population"].values[0]
    pop_upper = data.loc[data["year"] == upper_year, "population"].values[0]
    fraction = (year - lower_year) / (upper_year - lower_year)
    return int(pop_lower + fraction * (pop_upper - pop_lower))


def calculate_weighted_crime_rate(crime_df, weight_df, population_df, neighbourhood, start_year, end_year):
    """Calculate the average weighted crime rate per 100,000 people for a
    neighbourhood over a year range.

    Args:
        crime_df (pd.DataFrame): DataFrame containing crime data.
        weight_df (pd.DataFrame): DataFrame containing crime weights.
        population_df (pd.DataFrame): DataFrame containing population data.
        neighbourhood (str): The name of the neighbourhood.
        start_year (int): The starting year of the range (inclusive).
        end_year (int): The ending year of the range (inclusive).

    Raises:
        ValueError: If the year range is invalid (not between 2001 and 2024, or
          start year greater than end year).

    Returns:
        float: The average weighted crime rate per 100,000 people over the
          specified year range.
    """
    if start_year < 2001 or end_year > 2024:
        raise ValueError("Year must be between 2001 and 2024.")
    if start_year > end_year:
        raise ValueError("Start year must be less than or equal to end year.")

    total_weighted_crime_rate = 0

    data = crime_df[
        (crime_df["neighbourhood"] == neighbourhood)
        & (crime_df["year"] >= start_year)
        & (crime_df["year"] <= end_year)
    ]

    for year in range(start_year, end_year + 1):
        # Calculate weighted crime rate for this year
        weighted_crimes = 0
        for crime_type, count in data[data["year"] == year][["crime_type", "count"]].values:
            weight = weight_df[weight_df["type"] == crime_type]["weight"].values[0]
            weighted_crimes += count * weight
        # Crime rate per 100,000 people
        population = get_population(population_df, neighbourhood, year)
        crime_rate = (weighted_crimes / population) * 100000
        total_weighted_crime_rate += crime_rate

    # Average crime rate over the period
    return total_weighted_crime_rate / (end_year - start_year + 1)


def get_safety_score_data(start_year=2016, end_year=2021):
    """Get a dataframe with the safety scores for each neighbourhood.

    Args:
        start_year (int): The starting year of the range.
        end_year (int): The ending year of the range (inclusive).

    Returns:
        pd.DataFrame: A dataframe with the safety scores for each neighbourhood.    
    """
    # Load data from the same directory
    pwd = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    CRIME_WEIGHTS = pd.read_csv("crime_types.csv")
    CRIME_DATA = pd.read_csv("crime_data_clean.csv")
    POPULATION = pd.read_csv("population.csv")
    NEIGHBOURHOODS = POPULATION["neighbourhood"].unique()

    # Create a new dataframe to store the safety scores
    safety_scores = pd.DataFrame(columns=["Neighborhood", "Weighted Crime Rate"])
    # Calculate the weighted crime rate for each neighbourhood
    for neighbourhood in NEIGHBOURHOODS:
        safety_scores.loc[neighbourhood] = [
            neighbourhood,
            calculate_weighted_crime_rate(CRIME_DATA, CRIME_WEIGHTS, POPULATION, neighbourhood, start_year, end_year)
        ]
    # Min-max normalization
    min_rate = safety_scores["Weighted Crime Rate"].min()
    max_rate = safety_scores["Weighted Crime Rate"].max()
    safety_scores["Min-max Normalized Score"] = safety_scores["Weighted Crime Rate"].apply(lambda x: min_max_normalize(x, min_rate, max_rate))

    # Z-score normalization
    mean = safety_scores["Weighted Crime Rate"].mean()
    std = safety_scores["Weighted Crime Rate"].std()
    safety_scores["Z-score Normalized Score"] = (safety_scores["Weighted Crime Rate"] - mean) / std
    safety_scores["Z-score Normalized Score"] = 50 + -safety_scores["Z-score Normalized Score"] * 50 / 3
    safety_scores["Z-score Normalized Score"] = safety_scores["Z-score Normalized Score"].round().astype(int)

    os.chdir(pwd)

    return safety_scores


if __name__ == "__main__":
    print(get_safety_score_data().head())
    house_with_address_scores = pd.read_csv("../get_neighborhoods/houses_with_neighborhoods.csv")
    # Add safety score column to the house_with_address_scores dataframe
    df = get_safety_score_data()
    print(df)
    # Add safety score by neighbourhood names
    house_with_address_scores["Min-max Normalized Score"] = house_with_address_scores["Neighborhood"].map(df.set_index("Neighborhood")["Min-max Normalized Score"])
    house_with_address_scores["Z-score Normalized Score"] = house_with_address_scores["Neighborhood"].map(df.set_index("Neighborhood")["Z-score Normalized Score"])
    print(house_with_address_scores.head(10))
    # house_with_address_scores.to_csv("house_with_address_scores.csv", index=False)