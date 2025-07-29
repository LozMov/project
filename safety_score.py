import pandas as pd

CRIME_WEIGHTS = pd.read_csv("crime_types.csv")

CRIME_DATA = pd.read_csv("crime_data_clean.csv")

CRIME_TYPES = CRIME_WEIGHTS["type"]

POPULATION = pd.read_csv("population.csv")

NEIGHBOURHOODS = POPULATION["neighbourhood"].unique()


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


def get_population(neighbourhood, year):
    """Get population for a neighbourhood in a specific year.

    Args:
        neighbourhood (str): The name of the neighbourhood.
        year (int): The year for which to get the population.

    Raises:
        ValueError: If the year is not between 2001 and 2024.

    Returns:
        int: The population of the neighbourhood in the specified year.
    """
    if year < 2001 or year > 2024:
        raise ValueError("Year must be between 2001 and 2024.")

    data = POPULATION[POPULATION["neighbourhood"] == neighbourhood]
    # Check if census data is available for this year
    if year in data["year"].values:
        return data.loc[data["year"] == year, "population"].values[0]

    available_years = sorted(data["year"].values)
    # extrapolation with dampening factor
    if year > available_years[-1]:
        if len(available_years) < 2:
            return data.loc[data["year"] == available_years[-1], "population"].values[0]

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
        return data.loc[data["year"] == lower_year, "population"].values[0]

    pop_lower = data.loc[data["year"] == lower_year, "population"].values[0]
    pop_upper = data.loc[data["year"] == upper_year, "population"].values[0]
    fraction = (year - lower_year) / (upper_year - lower_year)
    return int(pop_lower + fraction * (pop_upper - pop_lower))


def calculate_weighted_crime_rate(neighbourhood, year_range):
    """Calculate the average weighted crime rate per 100,000 people for a
    neighbourhood over a year range.

    Args:
        neighbourhood (str): The name of the neighbourhood.
        year_range (tuple): A tuple containing the start and end year
          (inclusive).

    Raises:
        ValueError: If the year range is invalid (not between 2001 and 2024, or
          start year greater than end year).

    Returns:
        float: The average weighted crime rate per 100,000 people over the
          specified year range.
    """
    if year_range[0] < 2001 or year_range[1] > 2024:
        raise ValueError("Year must be between 2001 and 2024.")
    if year_range[0] > year_range[1]:
        raise ValueError("Start year must be less than or equal to end year.")

    total_weighted_crime_rate = 0

    data = CRIME_DATA[
        (CRIME_DATA["neighbourhood"] == neighbourhood)
        & (CRIME_DATA["year"] >= year_range[0])
        & (CRIME_DATA["year"] <= year_range[1])
    ]

    for year in range(year_range[0], year_range[1] + 1):
        # Calculate weighted crime rate for this year
        weighted_crimes = 0
        for crime_type, count in data[data["year"] == year][["crime_type", "count"]].values:
            weight = CRIME_WEIGHTS[CRIME_WEIGHTS["type"] == crime_type]["weight"].values[0]
            weighted_crimes += count * weight
        # Crime rate per 100,000 people
        population = get_population(neighbourhood, year)
        crime_rate = (weighted_crimes / population) * 100000
        total_weighted_crime_rate += crime_rate

    # Average crime rate over the period
    return total_weighted_crime_rate / (year_range[1] - year_range[0] + 1)


crime_rates = {
    neighbourhood: calculate_weighted_crime_rate(neighbourhood, (2021, 2024))
    for neighbourhood in NEIGHBOURHOODS
}
min_rate = min(crime_rates.values())
max_rate = max(crime_rates.values())
normalized_scores = {
    neighbourhood: normalize(score, min_rate, max_rate)
    for neighbourhood, score in crime_rates.items()
}

print(normalized_scores)
