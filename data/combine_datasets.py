import pandas as pd
import re

race_df = pd.read_csv('Formula1_2025Season_RaceResults.csv')
quali_df = pd.read_csv('Formula1_2025Season_QualifyingResults.csv')

# Function to convert time strings to seconds
def time_to_seconds(time_str):
    if pd.isna(time_str) or time_str in ['DNF', 'DNS', 'DSQ']:
        return None
    
    # For laptimes like 1:22.167
    if ':' in str(time_str):
        parts = str(time_str).split(':')
        return int(parts[0]) * 60 + float(parts[1])
    
    # For time gaps like +0.895
    elif str(time_str).startswith('+'):
        if 'lap' in str(time_str):  # Handle "+1 lap" format
            return None
        return float(str(time_str).replace('+', ''))
    
    return None

# Process race data
race_df['Race_Seconds'] = race_df['Time/Retired'].apply(time_to_seconds)
race_df['Fastest_Lap_Seconds'] = race_df['Fastest Lap Time'].apply(time_to_seconds)

# Process qualifying data
for q in ['Q1', 'Q2', 'Q3']:
    quali_df[f'{q}_Seconds'] = quali_df[q].apply(time_to_seconds)

# Create a combined dataframe
combined_df = pd.merge(
    race_df,
    quali_df[['Track', 'No', 'Driver', 'Q1_Seconds', 'Q2_Seconds', 'Q3_Seconds']],
    on=['Track', 'No', 'Driver'],
    how='outer'
)

# Add additional features
combined_df['Quali_Position'] = combined_df.groupby('Track')['Q3_Seconds'].rank()
combined_df['Grid_Diff'] = combined_df['Starting Grid'] - combined_df['Quali_Position']
combined_df['Finish_Quali_Diff'] = combined_df['Position'] - combined_df['Quali_Position']