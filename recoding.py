# ==============
# IMPORT MODULES
# ==============

import pandas as pd
import numpy as np
import os

# ======
# SET WD
# ======
print(os.getcwd())
file_path = "/scratch/project_2010938/Taavi_new/hs-combined-2025-11-11.csv"
print("Exists:", os.path.exists(file_path))
os.chdir('/scratch/project_2010938/Taavi_new/')


# =========
# LOAD DATA
# =========

wholedb = pd.read_csv(file_path, low_memory = False)

# Check and fix siteid names
print(wholedb['siteid'].unique())

print(wholedb['subsiteid'].unique())
print(wholedb['pointtype'].unique())

# Add columns: treatmet, secondary treatment, thinning clarification, trenching
wholedb['treatment'] = pd.Series(pd.NA, dtype="string")
wholedb['2nd_treatment'] = pd.Series(pd.NA, dtype="string")
wholedb['details'] = pd.Series(pd.NA, dtype="string")
wholedb['trenched'] = pd.Series(pd.NA, dtype="boolean")

# ==================
# KARSTULA (FINLAND)
# ==================

Karstula_sites = ['Karstula75', 'Karstula76'] # siteids
Karstula_controls = ['7C1', '7C2', '7C3', 'Control', '1C1', '1C2', '1C3'] # subsiteids
Karstula_nitrogens = ['4N1', '4N2', '4N3', 'Nitrogen fertilization', '8N1', '8N2', '8N3'] # subsiteids

# check structure
wholedb.loc[wholedb['siteid'].isin(Karstula_sites), 'subsiteid'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'].isin(Karstula_sites), 'pointtype'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'].isin(Karstula_sites), 'point'].value_counts(dropna=False)

# treatment
wholedb.loc[wholedb['siteid'].isin(Karstula_sites) & wholedb['subsiteid'].isin(Karstula_controls), 'treatment'] = 'Control'
wholedb.loc[wholedb['siteid'].isin(Karstula_sites) & wholedb['subsiteid'].isin(Karstula_nitrogens), 'treatment'] = 'Nitrogen Fertilization'

# details
wholedb.loc[wholedb['siteid'].isin(Karstula_sites) & wholedb['subsiteid'].isin(Karstula_nitrogens), 'details'] = '180 kg N/ha (every 10 years since 1960)'

# trenched
Karstula_trenched_pointtypes = ['Trenched', 'Trenched, without fabric lid']
Karstula_untrenched_pointtypes = ['Untrenched']

wholedb.loc[wholedb['siteid'].isin(Karstula_sites) & wholedb['pointtype'].isin(Karstula_trenched_pointtypes), 'trenched'] = True
wholedb.loc[wholedb['siteid'].isin(Karstula_sites) & wholedb['pointtype'].isin(Karstula_untrenched_pointtypes), 'trenched'] = False

# fix subsiteids
wholedb.loc[wholedb['siteid'].isin(Karstula_sites) & wholedb['subsiteid'].isin(Karstula_controls), 'subsiteid'] = 'Control'
wholedb.loc[wholedb['siteid'].isin(Karstula_sites) & wholedb['subsiteid'].isin(Karstula_nitrogens), 'subsiteid'] = 'Nitrogen fertilization'

# checking
wholedb.loc[wholedb['siteid'].isin(Karstula_sites), 'treatment'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'].isin(Karstula_sites), 'trenched'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'].isin(Karstula_sites), 'subsiteid'].value_counts(dropna=False)

# =====================
# KACERGINE (LITHUANIA)
# =====================

# check structure
wholedb.loc[wholedb['siteid'] == 'Kacergine', 'subsiteid'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'] == 'Kacergine', 'pointtype'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'] == 'Kacergine', 'point'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'] == 'Kacergine', 'point'].unique()

# treatment
wholedb.loc[(wholedb['siteid'] == 'Kacergine') & (wholedb['subsiteid'] == 'N fertilisation'), 'treatment'] = 'Nitrogen Fertilization'
wholedb.loc[(wholedb['siteid'] == 'Kacergine') & (wholedb['subsiteid'] == 'Clear-cut'), 'treatment'] = 'Nitrogen Fertilization'
wholedb.loc[(wholedb['siteid'] == 'Kacergine') & (wholedb['subsiteid'] == 'Control'), 'treatment'] = 'Control'

# 2nd_treatment
wholedb.loc[(wholedb['siteid'] == 'Kacergine') & (wholedb['subsiteid'] == 'Clear-cut'), '2nd_treatment'] = 'Clearcut'

# details option 2
wholedb.loc[(wholedb['siteid'] == 'Kacergine') & (wholedb['subsiteid'] == 'N fertilisation'), 'details'] = '180 kg N/ha (2002 & 2024)'
wholedb.loc[(wholedb['siteid'] == 'Kacergine') & (wholedb['subsiteid'] == 'Clear-cut'), 'details'] = '180 kg N/ha (2002)'

# trenched
wholedb.loc[(wholedb['siteid'] == 'Kacergine') & (wholedb['pointtype'] == 'IN'), 'trenched'] = True
wholedb.loc[(wholedb['siteid'] == 'Kacergine') & ~(wholedb['pointtype'] == 'IN'), 'trenched'] = False

# checking
wholedb.loc[wholedb['siteid'] == 'Kacergine', 'treatment'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'] == 'Kacergine', '2nd_treatment'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'] == 'Kacergine', 'details'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'] == 'Kacergine', 'trenched'].value_counts(dropna=False)

# ========================
# RÄNSKÄLÄNKORPI (FINLAND)
# ========================
# check structure
wholedb.loc[wholedb['siteid'] == 'Ränskälänkorpi', 'subsiteid'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'] == 'Ränskälänkorpi', 'pointtype'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'] == 'Ränskälänkorpi', 'point'].value_counts(dropna=False)

# treatment
ccf = ['Continues cover forestry', 'Ccf']
wholedb.loc[(wholedb['siteid'] == 'Ränskälänkorpi') & (wholedb['subsiteid'] == 'Clearcut'), 'treatment'] = 'Clearcut'
wholedb.loc[(wholedb['siteid'] == 'Ränskälänkorpi') & wholedb['subsiteid'].isin(ccf), 'treatment'] = 'Thinning'
wholedb.loc[(wholedb['siteid'] == 'Ränskälänkorpi') & (wholedb['subsiteid'] == 'Control'), 'treatment'] = 'Control'

# separate ditch into clearcut and control based on known measurement points
ditch_condition = (wholedb['siteid'] == 'Ränskälänkorpi') & (wholedb['subsiteid'] == 'Ditch')
clearcut_ditch = wholedb['point'].fillna("").str.startswith(("51", "61", "71", "81", "91", "101"))
wholedb.loc[ditch_condition & clearcut_ditch, 'treatment'] = 'Clearcut'
wholedb.loc[ditch_condition & ~clearcut_ditch, 'treatment'] = 'Control'

# details
wholedb.loc[(wholedb['siteid'] == 'Ränskälänkorpi') & wholedb['subsiteid'].isin(ccf), 'details'] = 'Continuous cover forestry'
wholedb.loc[ditch_condition, 'details'] = 'Ditch water surface measurement'

# trenched
Ränskälä_trenched_pointtypes = ['Trenched, with fabric lid', 'Trenched']
Ränskälä_untrenched_pointtypes = ['Untrenched']

wholedb.loc[(wholedb['siteid'] == 'Ränskälänkorpi') & wholedb['pointtype'].isin(Ränskälä_trenched_pointtypes), 'trenched'] = True
wholedb.loc[(wholedb['siteid'] == 'Ränskälänkorpi') & wholedb['pointtype'].isin(Ränskälä_untrenched_pointtypes), 'trenched'] = False

# Checking
wholedb.loc[wholedb['siteid'] == 'Ränskälänkorpi', 'treatment'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'] == 'Ränskälänkorpi', 'details'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'] == 'Ränskälänkorpi', 'trenched'].value_counts(dropna=False)

# ===========================
# LLOBERA & SECANELLA (SPAIN)
# ===========================
Spain_sites = ['Llobera', 'Secanella']
Spain_low_thinnings = ['Low thinning + prescribed burning', 'Low thinning']
Spain_high_thinnings = ['High thinning + prescribed burning', 'High-thinning']
Spain_thinnings = Spain_low_thinnings + Spain_high_thinnings
Spain_burnings = ['Low thinning + prescribed burning', 'High thinning + prescribed burning']

# check structure
wholedb.loc[wholedb['siteid'].isin(Spain_sites), 'subsiteid'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'].isin(Spain_sites), 'pointtype'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'].isin(Spain_sites), 'point'].value_counts(dropna=False)

# treatment
wholedb.loc[wholedb['siteid'].isin(Spain_sites) & wholedb['subsiteid'].isin(Spain_thinnings), 'treatment'] = 'Thinning'
wholedb.loc[wholedb['siteid'].isin(Spain_sites) & ~wholedb['subsiteid'].isin(Spain_thinnings), 'treatment'] = 'Control'

# 2nd_treatment
wholedb.loc[wholedb['siteid'].isin(Spain_sites) & wholedb['subsiteid'].isin(Spain_burnings), '2nd_treatment'] = 'Prescribed_burning'
wholedb.loc[
  (wholedb['siteid'].isin(Spain_sites)) &
  (~wholedb['subsiteid'].isin(Spain_burnings)) &
  (wholedb['subsiteid'] != "Control"),
  '2nd_treatment'
] = 'No prescribed_burning'

# details
wholedb.loc[wholedb['siteid'].isin(Spain_sites) & wholedb['subsiteid'].isin(Spain_low_thinnings), 'details'] = '~20% BA removed'
wholedb.loc[wholedb['siteid'].isin(Spain_sites) & wholedb['subsiteid'].isin(Spain_high_thinnings), 'details'] = '~40-50% BA removed'

# trenched
wholedb.loc[wholedb['siteid'].isin(Spain_sites), 'pointtype'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'].isin(Spain_sites) & (wholedb['pointtype'] == 'Trenched'), 'trenched'] = True
wholedb.loc[wholedb['siteid'].isin(Spain_sites) & (wholedb['pointtype'] == 'Untrenched'), 'trenched'] = False

# check
wholedb.loc[wholedb['siteid'].isin(Spain_sites), 'treatment'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'].isin(Spain_sites), '2nd_treatment'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'].isin(Spain_sites), 'details'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'].isin(Spain_sites), 'trenched'].value_counts(dropna=False)

# =================
# DOBROC (SLOVAKIA)
# =================
# check structure
wholedb.loc[wholedb['siteid'] == 'Dobroc', 'subsiteid'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'] == 'Dobroc', 'pointtype'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'] == 'Dobroc', 'point'].value_counts(dropna=False)
wholedb.loc[(wholedb['siteid'] == 'Dobroc') & (wholedb['subsiteid'] == 'DP-MC'), 'point'].value_counts(dropna=False)
wholedb.loc[(wholedb['siteid'] == 'Dobroc') & (wholedb['subsiteid'] == 'DP-MIX'), 'point'].value_counts(dropna=False)

# classify trenching
Dobroc_trenched_points = ['T1', 'T2', 'T3', 'T4']
Dobroc_untrenched_points = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6']

# treatment
wholedb.loc[(wholedb['siteid'] == 'Dobroc') & (wholedb['subsiteid'] == 'DP-MC'), 'treatment'] = 'Control'
wholedb.loc[(wholedb['siteid'] == 'Dobroc') & (wholedb['subsiteid'] == 'DP-MIX'), 'treatment'] = 'Mixed Forest'

# trenched
wholedb.loc[(wholedb['siteid'] == 'Dobroc') & wholedb['point'].isin(Dobroc_trenched_points), 'trenched'] = True
wholedb.loc[(wholedb['siteid'] == 'Dobroc') & wholedb['point'].isin(Dobroc_untrenched_points), 'trenched'] = False

# check
wholedb.loc[wholedb['siteid'] == 'Dobroc', 'treatment'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'] == 'Dobroc', 'trenched'].value_counts(dropna=False)

# =====================================================
# KROONDOMEIN, NP HOGE VELUWE, ZWOLSE BOS (NETHERLANDS)
# =====================================================
# check structure
dutchsites = ['Kroondomein', 'NP Hoge Veluwe', 'Zwolse Bos']
wholedb.loc[wholedb['siteid'].isin(dutchsites), 'siteid'].unique()
wholedb.loc[wholedb['siteid'].isin(dutchsites), 'subsiteid'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'].isin(dutchsites), 'pointtype'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'].isin(dutchsites) & (wholedb['subsiteid'] == 'Clearcut'), 'pointtype'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'].isin(dutchsites), 'point'].value_counts(dropna=False)

# treatment
dutch_thinnings = ['High-thinning', 'Shelterwood']
wholedb.loc[wholedb['siteid'].isin(dutchsites) & wholedb['subsiteid'].isin(dutch_thinnings), 'treatment'] = 'Thinning'
wholedb.loc[wholedb['siteid'].isin(dutchsites) & (wholedb['subsiteid'] == 'Clearcut'), 'treatment'] = 'Clearcut'
wholedb.loc[wholedb['siteid'].isin(dutchsites) & (wholedb['subsiteid'] == 'Control'), 'treatment'] = 'Control'

# details
wholedb.loc[wholedb['siteid'].isin(dutchsites) & (wholedb['subsiteid'] == 'High-thinning'), 'details'] = '~16-20% BA removed'
wholedb.loc[wholedb['siteid'].isin(dutchsites) & (wholedb['subsiteid'] == 'Shelterwood'), 'details'] = '~76-83% BA removed'

# trenched
wholedb.loc[wholedb['siteid'].isin(dutchsites) & (wholedb['pointtype'] == 'Trenched'), 'trenched'] = True
wholedb.loc[wholedb['siteid'].isin(dutchsites) & (wholedb['pointtype'] == 'Untrenched'), 'trenched'] = False

# check
wholedb.loc[wholedb['siteid'].isin(dutchsites), 'treatment'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'].isin(dutchsites), 'details'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'].isin(dutchsites), 'trenched'].value_counts(dropna=False)

# ========================================
# KELHEIM, KRANZBERG, WASSERBURG (GERMANY)
# ========================================
# check structure
germansites = ['Kelheim-Parsberg', 'Kranzberg-Freising', 'Wasserburg-Maitenbeth']
wholedb.loc[wholedb['siteid'].isin(germansites), 'siteid'].unique()
wholedb.loc[wholedb['siteid'].isin(germansites), 'subsiteid'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'].isin(germansites), 'pointtype'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'].isin(germansites), 'point'].unique()

# treatment
wholedb.loc[wholedb['siteid'].isin(germansites) & (wholedb['subsiteid'] == 'SB-Mix'), 'treatment'] = 'Mixed Forest'
wholedb.loc[wholedb['siteid'].isin(germansites) & (wholedb['subsiteid'] == 'Spruce'), 'treatment'] = 'Control'

# trenched
wholedb.loc[wholedb['siteid'].isin(germansites) & (wholedb['pointtype'] == 'Trenched'), 'trenched'] = True
wholedb.loc[wholedb['siteid'].isin(germansites) & (wholedb['pointtype'] == 'Untrenched'), 'trenched'] = False

# check
wholedb.loc[wholedb['siteid'].isin(germansites), 'treatment'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'].isin(germansites), 'trenched'].value_counts(dropna=False)

# ====================
# SAINT MITRE (FRANCE)
# ====================
# check structure
wholedb.loc[wholedb['siteid'] == 'Saint Mitre', 'subsiteid'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'] == 'Saint Mitre', 'pointtype'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'] == 'Saint Mitre', 'point'].value_counts(dropna=False)

# ================================================================
# subsiteids (Saint Mitre points as strings)
conditions = {
    "mtt": [str(i) for i in list(range(1, 5)) + list(range(41, 45)) + list(range(53, 57)) + list(range(93, 97))],
    "mtuv": [str(i) for i in list(range(9, 13)) + list(range(49, 53)) + list(range(61, 65)) + list(range(101, 105))],
    "mtnuv": [str(i) for i in list(range(5, 9)) + list(range(45, 49)) + list(range(57, 61)) + list(range(97, 101))],
    "ntt": [str(i) for i in list(range(25, 29)) + list(range(33, 37)) + list(range(77, 81)) + list(range(85, 89))],
    "ntnuv": [str(i) for i in list(range(29, 33)) + list(range(37, 41)) + list(range(81, 85)) + list(range(89, 93))],
    "htt": [str(i) for i in list(range(13, 17)) + list(range(65, 69)) + list(range(117, 121)) + list(range(105, 109))],
    "htuv": [str(i) for i in list(range(21, 25)) + list(range(73, 77)) + list(range(125, 129)) + list(range(113, 117))],
    "htnuv": [str(i) for i in list(range(17, 21)) + list(range(69, 73)) + list(range(121, 125)) + list(range(109, 113))]
}

mapping = {
    "mtt": "Medium thinning / Trenching",
    "mtuv": "Medium thinning / Pine with understory vegetation",
    "mtnuv": "Medium thinning / Pine without understory vegetation",
    "ntt": "No thinning / Trenching",
    "ntnuv": "No thinning / Pine without understory vegetation",
    "htt": "High thinning / Trenching",
    "htuv": "High thinning / Pine with understory vegetation",
    "htnuv": "High thinning / Pine without understory vegetation"
}

# recode subsiteids to match correct points
#for key, label in mapping.items():
#    wholedb.loc[
#        (wholedb["siteid"] == "Saint Mitre") &
#        (wholedb["point"].isin(conditions[key])),
#        "subsiteid"
#    ] = label

# remove rows where point doesnt match subsiteid.
# Build expected point → subsiteid mapping
expected_pairs = []
for key, label in mapping.items():
    for p in conditions[key]:
        expected_pairs.append((p, label))

expected_df = pd.DataFrame(expected_pairs, columns=["point", "expected_subsiteid"])

# Merge expected subsite info
wholedb = wholedb.merge(
    expected_df,
    how="left",
    on="point",
    suffixes=("", "_expected")
)

# Filter in place — keep only valid Saint Mitre rows or all other sites
wholedb = wholedb[
    (wholedb["siteid"] != "Saint Mitre") |
    (wholedb["subsiteid"] == wholedb["expected_subsiteid"])
].copy()

# Drop helper column
wholedb.drop(columns=["expected_subsiteid"], inplace=True)

print("✅ Removed mismatched Saint Mitre rows. Remaining rows:", len(wholedb))
# ====================================================================================================================

# treatment
stmitre_subsites = pd.Series(wholedb.loc[wholedb['siteid'] == 'Saint Mitre', 'subsiteid'].unique())
stmitre_thinnings = stmitre_subsites[stmitre_subsites.str.contains(r"medium|high", case=False, na=False)]

wholedb.loc[(wholedb['siteid'] == 'Saint Mitre') & wholedb['subsiteid'].isin(stmitre_thinnings), 'treatment'] = 'Thinning'
wholedb.loc[(wholedb['siteid'] == 'Saint Mitre') & ~wholedb['subsiteid'].isin(stmitre_thinnings), 'treatment'] = 'Control'

# 2nd_treatment
stmitre_understory = stmitre_subsites[stmitre_subsites.str.contains("with understory", case=False, na=False)]
stmitre_no_understory = stmitre_subsites[stmitre_subsites.str.contains("without understory", case=False, na=False)]

wholedb.loc[(wholedb['siteid'] == 'Saint Mitre') & wholedb['subsiteid'].isin(stmitre_understory), '2nd_treatment'] = 'Understory vegetation'
wholedb.loc[(wholedb['siteid'] == 'Saint Mitre') & wholedb['subsiteid'].isin(stmitre_no_understory), '2nd_treatment'] = 'No understory vegetation'

# details
stmitre_h_thinning = stmitre_thinnings[stmitre_thinnings.str.contains("high", case=False, na=False)]
stmitre_m_thinning = stmitre_thinnings[stmitre_thinnings.str.contains("medium", case=False, na=False)]

wholedb.loc[(wholedb['siteid'] == 'Saint Mitre') & wholedb['subsiteid'].isin(stmitre_h_thinning), 'details'] = '~60% BA removed'
wholedb.loc[(wholedb['siteid'] == 'Saint Mitre') & wholedb['subsiteid'].isin(stmitre_m_thinning), 'details'] = '~30% BA removed'

# trenched
stmitre_trenched = stmitre_subsites[stmitre_subsites.str.contains("Trenching", case=False, na=False)]
stmitre_untrenched = stmitre_subsites[~stmitre_subsites.str.contains("Trenching", case=False, na=False)]

wholedb.loc[(wholedb['siteid'] == 'Saint Mitre') & wholedb['subsiteid'].isin(stmitre_trenched), 'trenched'] = True
wholedb.loc[(wholedb['siteid'] == 'Saint Mitre') & wholedb['subsiteid'].isin(stmitre_untrenched), 'trenched'] = False

# check
wholedb.loc[(wholedb['siteid'] == 'Saint Mitre'), 'treatment'].value_counts(dropna=False)
wholedb.loc[(wholedb['siteid'] == 'Saint Mitre'), '2nd_treatment'].value_counts(dropna=False)
wholedb.loc[(wholedb['siteid'] == 'Saint Mitre'), 'details'].value_counts(dropna=False)
wholedb.loc[(wholedb['siteid'] == 'Saint Mitre'), 'trenched'].value_counts(dropna=False)
wholedb.loc[wholedb["siteid"].str.lower() == "saint mitre", "subsiteid"].value_counts()


# ==========================
# RINCONDEL BATOVI (URUGUAY)
# ==========================
# check structure
wholedb.loc[wholedb['siteid'] == 'RincondelBatovi', 'subsiteid'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'] == 'RincondelBatovi', 'pointtype'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'] == 'RincondelBatovi', 'point'].value_counts(dropna=False)

# re-name "Fbtafuera" to Forest Between Rows
wholedb.loc[(wholedb['siteid'] == 'RincondelBatovi') & (wholedb['subsiteid'] == 'Fbtafuera'), 'subsiteid'] = 'Forest Between Row'

# treatment
afforestation = ['Forest Between Row', 'Forest In Row']
wholedb.loc[(wholedb['siteid'] == 'RincondelBatovi') & wholedb['subsiteid'].isin(afforestation), 'treatment'] = 'Afforestation'
wholedb.loc[(wholedb['siteid'] == 'RincondelBatovi') & (wholedb['subsiteid'] == 'Campo Natural'), 'treatment'] = 'Control'

# trenched
wholedb.loc[(wholedb['siteid'] == 'RincondelBatovi') & (wholedb['pointtype'] == 'Trenched'), 'trenched'] = True
wholedb.loc[(wholedb['siteid'] == 'RincondelBatovi') & (wholedb['pointtype'] == 'Untrenched'), 'trenched'] = False

# details
wholedb.loc[(wholedb['siteid'] == 'RincondelBatovi') & (wholedb['subsiteid'] == 'Forest In Row'), 'details'] = 'Forest In Row'
wholedb.loc[(wholedb['siteid'] == 'RincondelBatovi') & (wholedb['subsiteid'] == 'Forest Between Row'), 'details'] = 'Forest Between Row'
wholedb.loc[(wholedb['siteid'] == 'RincondelBatovi') & (wholedb['subsiteid'] == 'Campo Natural'), 'details'] = 'Natural Pasture'

# check
wholedb.loc[wholedb['siteid'] == 'RincondelBatovi', 'treatment'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'] == 'RincondelBatovi', 'details'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'] == 'RincondelBatovi', 'trenched'].value_counts(dropna=False)

# ===========================
# DUMBRAVITA TRENCH (ROMANIA)
# ===========================
# check
wholedb.loc[wholedb['siteid'] == 'DumbravitaTrench', 'subsiteid'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'] == 'DumbravitaTrench', 'pointtype'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'] == 'DumbravitaTrench', 'point'].value_counts(dropna=False)

# treatment
wholedb.loc[wholedb['siteid'] == 'DumbravitaTrench', 'treatment'] = 'Control'

# 2nd_treatment
dumbravita_subsites = pd.Series(wholedb.loc[wholedb['siteid'] == 'DumbravitaTrench', 'subsiteid'].unique())
dumbravita_understory = dumbravita_subsites[dumbravita_subsites.str.contains("with", case=False, na=False)]
dumbravita_no_understory = dumbravita_subsites[dumbravita_subsites.str.contains("no", case=False, na=False)]

wholedb.loc[(wholedb['siteid'] == 'DumbravitaTrench') & wholedb['subsiteid'].isin(dumbravita_understory), '2nd_treatment'] = 'Understory vegetation'
wholedb.loc[(wholedb['siteid'] == 'DumbravitaTrench') & wholedb['subsiteid'].isin(dumbravita_no_understory), '2nd_treatment'] = 'No understory vegetation'

# details
dumbravita_shrubs = ['grass+shrubs/with understorey', 'grass+shrubs/no understorey']
wholedb.loc[(wholedb['siteid'] == 'DumbravitaTrench') & wholedb['subsiteid'].isin(dumbravita_shrubs), 'details'] = 'Shrubs can have small perennial plants'

# trenched
wholedb.loc[(wholedb['siteid'] == 'DumbravitaTrench') & (wholedb['pointtype'] == 'Trenched'), 'trenched'] = True
wholedb.loc[(wholedb['siteid'] == 'DumbravitaTrench') & (wholedb['pointtype'] == 'Control'), 'trenched'] = False

# check
wholedb.loc[wholedb['siteid'] == 'DumbravitaTrench', 'treatment'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'] == 'DumbravitaTrench', '2nd_treatment'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'] == 'DumbravitaTrench', 'trenched'].value_counts(dropna=False)

# ===========================================
# ST CHRISTOL, GAMIZ, DUMBRAVITA (WP 5 SITES)
# ===========================================
# check
wp5_sites = ['St Christol', 'Gamiz', 'Dumbravita']
wholedb.loc[wholedb['siteid'].isin(wp5_sites), 'subsiteid'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'].isin(wp5_sites), 'pointtype'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'].isin(wp5_sites), 'point'].value_counts(dropna=False)

# treatment
wholedb.loc[wholedb['siteid'].isin(wp5_sites) & (wholedb['subsiteid'] == 'thinning'), 'treatment'] = 'Thinning'
wholedb.loc[wholedb['siteid'].isin(wp5_sites) & (wholedb['subsiteid'] == 'clear_cut'), 'treatment'] = 'Clearcut'
wholedb.loc[wholedb['siteid'].isin(wp5_sites) & (wholedb['subsiteid'] == 'control'), 'treatment'] = 'Control'

# 2nd_treatment
wholedb.loc[wholedb['siteid'].isin(wp5_sites) & (wholedb['pointtype'] == 'slash'), '2nd_treatment'] = 'Slash'
wholedb.loc[wholedb['siteid'].isin(wp5_sites) & (wholedb['pointtype'] == 'no_slash'), '2nd_treatment'] = 'No slash'
wholedb.loc[wholedb['siteid'].isin(wp5_sites) & (wholedb['treatment'] == 'Control'), '2nd_treatment'] = pd.NA

# details
wholedb.loc[wholedb['siteid'].isin(wp5_sites) & (wholedb['subsiteid'] == 'thinning'), 'details'] = '~50% BA removed'

# trenched
wholedb.loc[wholedb['siteid'].isin(wp5_sites), 'trenched'] = False

# check
wholedb.loc[wholedb['siteid'].isin(wp5_sites), 'treatment'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'].isin(wp5_sites), '2nd_treatment'].value_counts(dropna=False)
wholedb.loc[wholedb['siteid'].isin(wp5_sites), 'details'].value_counts(dropna=False)

# ==================
# Recoding the names
# ==================
# Dumbravita
#wholedb.loc[wholedb['siteid'] == 'DumbravitaTrench', 'siteid'] = 'Dumbravita'

# Karstula
#wholedb.loc[wholedb['siteid'].isin(Karstula_sites), 'siteid'] = 'Karstula'

# ======================
# SAVE RECODED DATAFRAME
# ======================
holisoils_recoded = wholedb.copy()
holisoils_recoded.to_csv("holisoils_recoded.csv", index=False)
print("Script run succesfully")

