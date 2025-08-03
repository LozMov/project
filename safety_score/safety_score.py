import pandas as pd


def normalize(val, min_val, max_val):
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


if __name__ == "__main__":
    # Load data
    CRIME_WEIGHTS = pd.read_csv("crime_types.csv")
    CRIME_DATA = pd.read_csv("crime_data_clean.csv")
    CRIME_TYPES = CRIME_WEIGHTS["type"]
    POPULATION = pd.read_csv("population.csv")
    NEIGHBOURHOODS = POPULATION["neighbourhood"].unique()

    # Calculate crime rates for each neighbourhood
    crime_rates = {
        neighbourhood: calculate_weighted_crime_rate(CRIME_DATA, CRIME_WEIGHTS, POPULATION, neighbourhood, 2021, 2024)
        for neighbourhood in NEIGHBOURHOODS
    }
    min_rate = min(crime_rates.values())
    max_rate = max(crime_rates.values())
    normalized_scores = {
        neighbourhood: normalize(score, min_rate, max_rate)
        for neighbourhood, score in crime_rates.items()
    }

    print(normalized_scores)
