import pandas as pd
import os

input_file = 'data/NBA_Play_Types_16_24.csv'
output_dir = 'data/plays/'

os.makedirs(output_dir, exist_ok=True)
df = pd.read_csv(input_file)

for season in df['SEASON'].unique():
    year = season.split('-')[1]
    full_year = '20' + year
    season_df = df[df['SEASON'] == season]
    output_file = f'{output_dir}NBA_{full_year}_Plays.csv'
    season_df.to_csv(output_file, index=False)
    
    print(f'Saved {season} data to {output_file}')
