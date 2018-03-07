import orca
import pandas as pd
import zipfile

# path relative to where python is run from
z = zipfile.ZipFile('data/bay_area_test_data_20180302.zip')

# reading data directly from zipfiles is nice, but it doesn't work with symlinks (on my 
# machine at least) - is there a workaround?

@orca.table(cache=True)
def households():
    df = pd.read_csv(z.open('bay_area_test_data/households.csv'))
    return df

@orca.table(cache=True)
def buildings():
    df = pd.read_csv(z.open('bay_area_test_data/buildings.csv'))
    return df

# specify key relationships
orca.broadcast('buildings', 'households', cast_index=True, onto_on='building_id')
