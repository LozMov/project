# get_address_score.py
import pandas as pd


def get_address_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute proximity-based address score from a DataFrame containing driving distances.

    Parameters:
        df (pd.DataFrame): DataFrame containing at least 'Driving_Distance_m' column.

    Returns:
        pd.DataFrame: Original DataFrame with added 'Address_Scores' column,
                      sorted by score descending.
    """
    if 'Driving_Distance_m' not in df.columns:
        raise ValueError(
            "Input DataFrame must contain 'Driving_Distance_m' column.")

    # Drop rows with missing distances
    df = df[df['Driving_Distance_m'].notna()].copy()

    # Compute min/max distance
    min_dist = df['Driving_Distance_m'].min()
    max_dist = df['Driving_Distance_m'].max()

    # Score function: 100 for closest, 0 for farthest
    def compute_score(d):
        if max_dist == min_dist:
            return 100
        return 100 * (1 - (d - min_dist) / (max_dist - min_dist))

    # Apply score
    df['Address_Scores'] = df['Driving_Distance_m'].apply(compute_score)

    # Sort by score
    df = df.sort_values(by='Address_Scores', ascending=False)

    return df
