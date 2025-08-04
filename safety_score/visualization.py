import pandas as pd
import matplotlib.pyplot as plt
# import numpy as np
# from matplotlib.lines import Line2D

import safety_score


def plot_neighbourhood_bar_chart(population_df, neighbourhood, start_year=2001, end_year=2024, figsize=(12, 8)):
    """
    Create a bar chart showing population trend for a single neighbourhood.
    Real data in one color, interpolated/extrapolated in another.
    
    Args:
    - population_df (pd.DataFrame): DataFrame containing population data.
    - neighbourhood (str): Name of the neighbourhood to plot.
    - start_year (int): First year to show.
    - end_year (int): Last year to show.
    - figsize (tuple): Size of the figure.
    """

    years = list(range(start_year, end_year + 1))
    populations = []
    colors = []
    edge_colors = []
    
    real_color = '#2E86AB'  # Blue for real data
    interp_color = '#A23B72'  # Purple for interpolated data
    extrap_color = '#F18F01'  # Orange for extrapolated data
    
    # Get census years for this neighbourhood
    census_data = population_df[population_df["neighbourhood"] == neighbourhood]
    census_years = sorted(census_data["year"].values)
    last_census_year = census_years[-1]
    
    for year in years:
        pop, is_real = safety_score.get_population_with_type(population_df, neighbourhood, year)
        populations.append(pop)
        
        if is_real:
            colors.append(real_color)
            edge_colors.append('black')
        elif year > last_census_year:
            colors.append(extrap_color)
            edge_colors.append('darkred')
        else:
            colors.append(interp_color)
            edge_colors.append('darkblue')
    
    # Create the plot
    fig, ax = plt.subplots(figsize=figsize)
    
    # Create bars
    bars = ax.bar(years, populations, color=colors, edgecolor=edge_colors, linewidth=2)
    
    # Add value labels on top of bars
    for i, (year, pop) in enumerate(zip(years, populations)):
        # Only label every other year to avoid crowding
        if year % 2 == 0 or year in census_years:
            ax.text(year, pop + max(populations) * 0.01, f'{pop:,}', 
                   ha='center', va='bottom', fontsize=9, rotation=45)
    
    # Styling
    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Population', fontsize=12, fontweight='bold')
    ax.set_title(f'Population Trend: {neighbourhood}\nActual Census Data vs. Interpolated/Extrapolated Values', 
                fontsize=16, fontweight='bold', pad=20)
    
    # Grid
    ax.grid(True, axis='y', alpha=0.3, linestyle='-', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # Format y-axis with comma separators
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
    
    # Set x-axis
    ax.set_xticks(years)
    ax.set_xticklabels(years, rotation=45, ha='right')
    
    # Add horizontal line at 2016 to show extrapolation boundary
    ax.axvline(x=2016.5, color='red', linestyle='--', alpha=0.5, linewidth=2, 
              label='Extrapolation begins')
    
    # Create legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=real_color, edgecolor='black', linewidth=2, label='Census Data (Actual)'),
        Patch(facecolor=interp_color, edgecolor='darkblue', linewidth=2, label='Interpolated'),
        Patch(facecolor=extrap_color, edgecolor='darkred', linewidth=2, label='Extrapolated (After 2016, 0.8 dampening)')
    ]
    ax.legend(handles=legend_elements, loc='upper left', frameon=True, fancybox=True, shadow=True)
    
    # Add statistics box
    growth_rate = ((populations[-1] - populations[0]) / populations[0]) * 100
    stats_text = f'Population Growth ({start_year}-{end_year}): {growth_rate:.1f}%\n'
    stats_text += f'From {populations[0]:,} to {populations[-1]:,}\n'
    stats_text += f'Census years: {", ".join(map(str, census_years))}'
    
    ax.text(0.02, 0.98, stats_text,
           transform=ax.transAxes, 
           fontsize=10, 
           verticalalignment='top',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.8))
    
    plt.tight_layout()
    return fig, ax