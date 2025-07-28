import pandas as pd

# Load the dataset
df = pd.read_csv("House_with_road_distance.csv")

# Drop rows with missing distances
df = df[df['Driving_Distance_m'].notna()].copy()

# Score: 100 for closest, 0 for farthest
min_dist = df['Driving_Distance_m'].min()
max_dist = df['Driving_Distance_m'].max()


def compute_score(d):
    if max_dist == min_dist:
        return 100
    return 100 * (1 - (d - min_dist) / (max_dist - min_dist))


df['Proximity_Score'] = df['Driving_Distance_m'].apply(compute_score)

# Sort by score (descending)
df_sorted = df.sort_values(by='Proximity_Score', ascending=False)

# Print top 20 to console
print("🏠 Top 20 closest houses:\n")
print(df_sorted.head(20)[['Address', 'Price',
      'Driving_Distance_m', 'Proximity_Score']])

# Save full dataframe with score to new CSV
df_sorted.to_csv("House_with_road_distance_and_score.csv", index=False)
print("\n📁 Full scored dataset saved to 'House_with_road_distance_and_score.csv'")
