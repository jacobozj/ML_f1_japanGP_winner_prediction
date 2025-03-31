import pandas as pd


def merge_f1_datasets(race_results_path, qualifying_results_path):
    race_results = pd.read_csv(race_results_path)
    qualifying_results = pd.read_csv(qualifying_results_path)
    
    merged_df = pd.merge(
        race_results,
        qualifying_results,
        on=["Track", "Driver"],
        how="inner"
    )
    
    merged_df = merged_df.drop(columns=["Position_y", "No_y", "Team_y", "Laps_y"])
    
    #rename columns for clarity
    merged_df = merged_df.rename(columns={
        "Position_x": "Race_Position",
        "No_x": "Car_Number",
        "Team_x": "Team",
        "Laps_x": "Laps_Completed",
        "Fastest Lap Time": "Fastest_Lap_Time",
        "Q1": "Qualy_Q1",
        "Q2": "Qualy_Q2",
        "Q3": "Qualy_Q3"
    })
    
    #convert lap times to seconds (handling missing Q2/Q3 times and non-numeric values)
    def time_to_seconds(time_str):
        # print(time_str, "check")
        if pd.isna(time_str) or not isinstance(time_str, str):
            return None
        time_str = time_str.replace('+', '').strip()
        if "DNF" in time_str or "DSQ" in time_str:
            return 9999
        if "1 lap" in time_str:
            return 120
        if "+" in time_str:
            time_str = time_str.split("+")[0].strip()
        try:
            parts = time_str.split(':')
            if len(parts) == 2:
                minutes, seconds = map(float, parts)
                return minutes * 60 + seconds
            elif len(parts) == 3:
                hours, minutes, seconds = map(float, parts)
                return hours * 3600 + minutes * 60 + seconds
            return float(time_str) #if it's already in seconds format
        except ValueError:
            return None
    
    for col in ["Qualy_Q1", "Qualy_Q2", "Qualy_Q3"]:
        merged_df[col] = merged_df[col].apply(time_to_seconds)
    merged_df["Set Fastest Lap"] = merged_df["Set Fastest Lap"].replace({'Yes': 1, 'No': 0})
    merged_df["Fastest_Lap_Time"] = merged_df["Fastest_Lap_Time"].apply(time_to_seconds)
    #compute best qualifying lap time (smallest of Q1, Q2, Q3)
    merged_df["Best_Qualy_Time"] = merged_df[["Qualy_Q1", "Qualy_Q2", "Qualy_Q3"]].min(axis=1, skipna=True)
    
    #convert race time based on first position reference
    def convert_race_time(race_times):
        converted_times = []
        base_time = None
        for time in race_times:
            if ":" in time:
                base_time = time_to_seconds(time)
                converted_times.append(base_time)
            else:
              converted_times.append(base_time + time_to_seconds(time))
        return converted_times
    
    merged_df["Race_Time_Seconds"] = convert_race_time(merged_df["Time/Retired"].tolist())


    #ensure race position and starting grid are integers
    merged_df["Race_Position"] = pd.to_numeric(merged_df["Race_Position"], errors='coerce').fillna(0).astype(int)
    merged_df["Starting Grid"] = pd.to_numeric(merged_df["Starting Grid"], errors='coerce').fillna(0).astype(int)
    
    #compute race improvement (Starting Grid - Final Position)
    merged_df["Race_Improvement"] = merged_df["Starting Grid"] - merged_df["Race_Position"]
    
    #drop rows with missing values in critical columns
    merged_df = merged_df.dropna(subset=["Race_Position", "Starting Grid", "Best_Qualy_Time"])
    
    #convert categorical columns (Track, Driver, Team) into numeric values
    for col in ["Track", "Driver", "Team"]:
        merged_df[col] = merged_df[col].astype('category').cat.codes
    
    #save merged dataset to CSV
    merged_df.to_csv("data/Merged_F1_Dataset.csv", index=False)
    
    return merged_df

race_results_path = "data/Formula1_2025Season_RaceResults.csv"
qualifying_results_path = "data/Formula1_2025Season_QualifyingResults.csv"
merged_f1_data = merge_f1_datasets(race_results_path, qualifying_results_path)
print("Merged dataset saved to data/Merged_F1_Dataset.csv")
print(merged_f1_data.head())

