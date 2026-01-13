import pandas as pd
import numpy as np
from collections import defaultdict
import os
os.getcwd()
os.chdir('/scratch/project_2010938/Taavi_new')


wholedb = pd.read_csv("hs-combined-2025-11-11.csv", low_memory=False)  # if you have pyarrow installed
print(wholedb['siteid'].unique())

wholedb.describe()

# Luodaan dictionary tarkastelua varten
hierarchy = defaultdict(dict)

for site in wholedb["siteid"].unique():
  site_df = wholedb[wholedb["siteid"] == site]
  subsite_dict = {}
  
  for subsite in site_df["subsiteid"].unique():
    subsite_df = site_df[site_df["subsiteid"] == subsite]
    point_dict = {}
    
    for point in subsite_df["point"].unique():
      point_df = subsite_df[subsite_df["point"] == point]
      pointtypes = point_df["pointtype"].unique().tolist()
      
      point_dict[point] = {
        "count": len(pointtypes),
        "pointtypes": pointtypes
      }
    
    subsite_dict[subsite] = {
      "count": len(point_dict),
      "points": point_dict
    }
  
  hierarchy[site] = {
    "count": len(subsite_dict),
    "subsites": subsite_dict
  }


# Example: print the structure
import pprint
wholedb['siteid'].unique()

# Check structure of RincondelBatovi
pprint.pprint(dict(hierarchy["Kacergine"]))
wholedb.loc[wholedb['siteid'] == "RincondelBatovi", 'tsmoisture'].notna().sum()
wholedb.loc[wholedb['siteid'] == "RincondelBatovi", 't30'].notna().sum()
wholedb.loc[wholedb['subsiteid'] == "Ccf", 'pointtype'].value_counts()

# Check structure of subsitedids'
siteids = wholedb['siteid'].unique()
for site in siteids:
  print(f"\nSiteID: \"{site}\" & n observations ")
  print(f"\nTreatment")
  print(wholedb.loc[wholedb['siteid'] == site, 'subsiteid'].value_counts())
  print(f"\nSubtreatment")
  print(wholedb.loc[wholedb['siteid'] == site, 'pointtype'].value_counts())

# All unique subsiteids
unique_subsites = set()

for site, site_info in hierarchy.items():
    subsites = site_info.get("subsites", {})
    unique_subsites.update(subsites.keys())

print("Unique subsites:")
for subsite in sorted(unique_subsites):
    print(subsite)

for site, site_info in hierarchy.items():
    subsites = site_info.get("subsites", {})
    subsite_names = list(subsites.keys())
    print(f"{site} has subsites: {', '.join(subsite_names) if subsite_names else 'None'}")

