import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.dates as mdates

import recoding
wholedb_co2 = recoding.wholedb
wholedb_co2.info()


# =====================================
# Create a table showing missing values
# =====================================

print(wholedb_co2.info())
columns_of_interest = ['j_flux', 'tsmoisture', 't05', 't10', 't30']
missing_by_site = wholedb_co2.groupby('siteid')[columns_of_interest].apply(lambda x: x.isnull().mean().round(2))
print("=== PROPORTION OF MISSING VALUES IN TEMP, MOIST & FLUX IN EACH SITE ===")
print(missing_by_site)
# Compute proportion of missing values for each column across the entire dataset
missing_proportions_total = wholedb_co2[columns_of_interest].isnull().mean().round(2)
print("=== TOTAL PROPORTION OF MISSING VALUES PER COLUMN ===")
print(missing_proportions_total)

# Table with also total amounts of values

grouped = wholedb_co2.groupby('siteid')[columns_of_interest]
missing = grouped.apply(lambda x: x.isnull().sum())
non_missing = grouped.apply(lambda x: x.notnull().sum())
total = grouped.size()

missing_prop = missing.div(total, axis=0)

summary = pd.concat({
  'non_missing': non_missing,
  'missing': missing,
  'missing_pct': missing_prop * 100,
  'total': total
}, axis= 1).round(1)
print(summary)

summary.to_csv("missing_data_summary.csv")

# ============================
# Missing value heatmap before
# ============================
# Mutate date into two columns

wholedb_co2['date'] = pd.to_datetime(wholedb_co2['date'])
wholedb_co2['day_year'] = wholedb_co2['date'].dt.dayofyear
wholedb_co2['year'] = wholedb_co2['date'].dt.year

# Filter only wanted columns and rename them
wanted_columns = ['j_flux', 't05', 't10', 't30', 'tsmoisture','date', 'day_year', 'year', 'treatment', '2nd_treatment', 'trenched', 'siteid']
missing_df = wholedb_co2[wanted_columns].copy()

#change indexing
missing_df.index = range(missing_df.shape[0])

# Missing values
missing_df.isnull().sum().sort_values(ascending=False)
missing_df.isna().mean()  # fraction missing
plt.figure(figsize=(10, 6))
sns.heatmap(missing_df.isnull(), cbar=False)
plt.title("Missing Data Map Before Filtering")
plt.setp(plt.gca().get_xticklabels(), rotation=45, ha='right', fontsize = 8)
plt.show()
plt.savefig('Plots/Missing_data_heatmap_before.png',
            dpi=600,                    # Very high DPI for manuscripts
            bbox_inches='tight',
            facecolor='white', 
            edgecolor='none',
            format='png',
            pil_kwargs={'optimize': True})
plt.close()


# ===============
# Outlier removal
# ===============

# Renaming of columns first
print(wholedb_co2.columns)

# Remove points with z-score > 3 (or 2.5 for stricter)
threshold = 3
# Apply to original dataframe (handling NaN values)
wholedb_co2_clean = wholedb_co2[~((np.abs(stats.zscore(wholedb_co2['j_flux'], nan_policy='omit')) > threshold) & 
                                  (~wholedb_co2['j_flux'].isna()))]
# ROWS REMOVED WITH Z-SCORE
print(f"Rows before z-score filtering: {len(wholedb_co2)}")
print(f"Rows after z-score filtering: {len(wholedb_co2_clean)}")
print(f"Rows removed with z-score filtering: {len(wholedb_co2) - len(wholedb_co2_clean)}")

## Negative values
# For this we have two approaches. 1st is to remove negative values. 2nd is to change them to 0
# How many negative flux values do we have?
print((wholedb_co2_clean['j_flux'] < 0).sum())

# Remove negative values
wholedb_co2_remove_neg = wholedb_co2_clean[(wholedb_co2_clean['j_flux'] >= 0) | (wholedb_co2_clean['j_flux'].isna())]

# NEGATIVE ROWS REMOVED
print(f"Rows before negative removal: {len(wholedb_co2_clean)}")
print(f"Rows after negative removal: {len(wholedb_co2_remove_neg)}")
print(f"Rows removed with negative removal: {len(wholedb_co2_clean) - len(wholedb_co2_remove_neg)}")

# Change negative values to 0
wholedb_co2_neg_to_0 = wholedb_co2_clean.copy()
wholedb_co2_neg_to_0['j_flux'] = wholedb_co2_neg_to_0['j_flux'].clip(lower=0)

# remove values above 5
wholedb_co2_lowpass = wholedb_co2_remove_neg[(wholedb_co2_remove_neg['j_flux'] <= 5) | (wholedb_co2_remove_neg['j_flux'].isna())]
# ROWS REMOVED WITH ABOVE 5 FLUX
print(f"Rows removed with flux value above 5: {len(wholedb_co2_remove_neg) - len(wholedb_co2_lowpass)}")

# remove missing merged_flux observations
wholedb_co2_noNA = wholedb_co2_lowpass[~wholedb_co2_lowpass['j_flux'].isna()]
# ROWS WITHOUT FLUX REMOVED
print(f"Rows removed without a flux value: {len(wholedb_co2_lowpass) - len(wholedb_co2_noNA)}")

# =============================
# Missing value heatmap after
# =============================
missing_df_after = wholedb_co2_noNA.copy()
len(missing_df_after)

missing_df_after['date'] = pd.to_datetime(missing_df_after['date'])
missing_df_after['day_year'] = missing_df_after['date'].dt.dayofyear
missing_df_after['year'] = missing_df_after['date'].dt.year

missing_df_after = missing_df_after[wanted_columns].copy()

# Change indexing for plotting
missing_df_after.index = range(missing_df_after.shape[0])

# Missing values
missing_df_after.isnull().sum().sort_values(ascending=False)
missing_df_after.isna().mean()  # fraction missing
plt.figure(figsize=(10, 6))
sns.heatmap(missing_df_after.isnull(), cbar=False)
plt.title("Missing Data Map After Filtering")
plt.setp(plt.gca().get_xticklabels(), rotation=45, ha='right', fontsize = 8)
plt.show()
plt.savefig('Plots/Missing_data_heatmap_after.png',
            dpi=600,                    # Very high DPI for manuscripts
            bbox_inches='tight',
            facecolor='white', 
            edgecolor='none',
            format='png',
            pil_kwargs={'optimize': True})
plt.close()


# ==================
# Summary statistics
# ==================
sumstats_df = wholedb_co2.copy()
sumstats_df.info()
sumstats_df['treatment'] = sumstats_df['treatment'].astype('category')
sumstats_df['2nd_treatment'] = sumstats_df['2nd_treatment'].astype('category')
sumstats_df['trenched'] = sumstats_df['trenched'].astype('category')

numerical = ['j_flux', 't05', 't10', 't30', 'tsmoisture']
categorical = ['siteid', 'treatment', '2nd_treatment', 'trenched', 'thinning_clarification']

# 1. Summary stats for numerical variables
num_summary = sumstats_df[numerical].describe().T  # Transpose for easier reading
# Compute IQR: Q3 - Q1
num_summary['IQR'] = num_summary['75%'] - num_summary['25%']
# Add Mean ± SD column
num_summary['Mean ± SD'] = num_summary['mean'].round(2).astype(str) + ' ± ' + num_summary['std'].round(2).astype(str)
# Format final table
num_summary_table = num_summary[['Mean ± SD', '50%', 'min', 'max', '25%', '75%', 'IQR']].rename(columns={
    '50%': 'Median',
    'min': 'Min',
    'max': 'Max',
    '25%': 'Q1 (25%)',
    '75%': 'Q3 (75%)'
})

# Optional: Round columns
num_summary_table['IQR'] = num_summary_table['IQR'].round(2)
num_summary_table['Mean ± SD'] = num_summary_table['Mean ± SD'].round(2)
num_summary_table['Q1 (25%)'] = num_summary_table['Q1 (25%)'].round(2)
num_summary_table['Q3 (75%)'] = num_summary_table['Q3 (75%)'].round(2)
num_summary_table['Median'] = num_summary_table['Median'].round(2)
num_summary_table['Max'] = num_summary_table['Max'].round(2)

print("Numerical Variables Summary:")
print(num_summary_table)

# 2. Frequency and percentage for categorical variables
cat_summary_list = []

for var in categorical:
    counts = sumstats_df[var].value_counts(dropna=False)
    percentages = sumstats_df[var].value_counts(normalize=True, dropna=False) * 100
    df_cat = pd.DataFrame({
        'Variable': var,
        'Category': counts.index.astype(str),
        'Count': counts.values,
        'Percentage (%)': percentages.round(1).values
    })
    cat_summary_list.append(df_cat)

cat_summary_table = pd.concat(cat_summary_list, ignore_index=True)

print("Categorical Variables Summary:")
print(cat_summary_table)

# ===================
# Timeseries plotting
# ===================


# -----------------------------
# Autotrophic vs. heterotrophic
# -----------------------------
df = wholedb_co2.copy()
df.info()
df['date'] = pd.to_datetime(df['date']).dt.date # drop the timestamp

# Check if points appear in multiple sites
# Count how many different sites each point appears in
site_counts_per_point = df.groupby('point')['siteid'].nunique()
site_counts_per_point.unique

# Find points that appear in more than one site
shared_points = site_counts_per_point[site_counts_per_point > 1]

print(shared_points)

# Get all rows with points that appear in multiple sites

overlapping_points_df = df[df['point'].isin(shared_points.index)]

# View how points are spread across sites
overlapping_summary = overlapping_points_df.groupby(['point', 'siteid'], observed=False).size().unstack(fill_value=0)
print(overlapping_summary)

# Lets divide data into sites
site_dfs = {}

for site in df['siteid'].unique():
    site_dfs[site] = df[df['siteid'] == site].copy()


pivoted_site_dfs = {}

for site, df_site in site_dfs.items():
    # Print how many True/False values are present in each site
    print(f"{site}: {df_site['trenched'].value_counts().to_dict()}")

    # Pivot the data
    pivoted = df_site.pivot_table(
        index=['point', 'date', 'day_year', 'year'],
        columns='trenched',
        values='j_flux',
        observed=False
    ).reset_index()

    pivoted.columns.name = None  # remove 'Trenched' from column level

    # Only process if both treatments exist
    if True in pivoted.columns and False in pivoted.columns:
        pivoted = pivoted.rename(columns={
            True: 'flux_trenched',
            False: 'flux_untrenched'
        })

        pivoted['heterotrophic'] = pivoted['flux_trenched']
        pivoted['autotrophic'] = pivoted['flux_untrenched'] - pivoted['flux_trenched']

        pivoted = pivoted.dropna(subset=['flux_trenched', 'flux_untrenched'])

        pivoted_site_dfs[site] = pivoted
    else:
        print(f"Skipping site '{site}' — missing one treatment type (Trenched=True or False)")



## CONTINUE FROM HERE ##

## It looks like Only Dumbravita and Saint Mitre has non-unique 'points'
# lets try some mean comparison to see differences between autrotrophic and heterotrophic fluxes.
df_grouped = df.groupby(['siteid', 'date', 'trenched'], observed = False)['j_flux'].mean().unstack()
print(df_grouped.columns)

df_grouped = df_grouped.dropna(subset=[True, False])

df_grouped = df_grouped.copy()
df_grouped['heterotrophic'] = df_grouped[True]
df_grouped['autotrophic'] = df_grouped[False] - df_grouped[True]

# Plot flux over time
# -------------------
df_plot = df_grouped.reset_index()

df_plot['date'] = pd.to_datetime(df_plot['date'])

# Reshape the dataframe to long format
df_long = df_plot.melt(
    id_vars=['siteid', 'date'],
    value_vars=['autotrophic', 'heterotrophic'],
    var_name='Component',
    value_name='CO2 Flux'
)

# Set up FacetGrid: one subplot per site
g = sns.FacetGrid(
    df_long,
    col='siteid',
    col_wrap=4,  # 4 plots per row, adjust as needed
    height=3.5,
    sharey=True
)

# Add lineplot to each facet
g.map_dataframe(
    sns.lineplot,
    x='date',
    y='CO2 Flux',
    hue='Component',
    marker='o'
)

# Improve legend and appearance
g.add_legend(title="Respiration")
g.set_titles(col_template="{col_name}")
g.tight_layout()

# Format date ticks
for ax in g.axes.flat:
  ax.tick_params(axis='x', rotation=45, labelsize=10)
  ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
  ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

# Save as PNG
plt.savefig('auto_vs_hetero/Autotrophic_vs_heterotrophic_by_site.png',
            dpi=600,                    # Very high DPI for manuscripts
            bbox_inches='tight',
            facecolor='white', 
            edgecolor='none',
            format='png',
            pil_kwargs={'optimize': True})

plt.close()

# Do the same but group by treatment instead of site
# --------------------------------------------------

# Group and pivot by treatment and date
df_treatment_grouped = df.groupby(['treatment', 'date', 'trenched'], observed = False)['j_flux'].mean().unstack()

df_treatment_grouped = df_treatment_grouped.dropna(subset=[True, False])

# Compute components
df_treatment_grouped = df_treatment_grouped.copy()
df_treatment_grouped['heterotrophic'] = df_treatment_grouped[True]
df_treatment_grouped['autotrophic'] = df_treatment_grouped[False] - df_treatment_grouped[True]

# Reset index for plotting
df_plot = df_treatment_grouped.reset_index()
df_plot['date'] = pd.to_datetime(df_plot['date'])

# Reshape the dataframe to long format
df_long = df_plot.melt(
    id_vars=['treatment', 'date'],
    value_vars=['autotrophic', 'heterotrophic'],
    var_name='Component',
    value_name='CO2 Flux'
)

# Set up FacetGrid: one subplot per site
g = sns.FacetGrid(
    df_long,
    col='treatment',
    col_wrap=4,  # 4 plots per row, adjust as needed
    height=3.5,
    sharey=True
)

# Add lineplot to each facet
g.map_dataframe(
    sns.lineplot,
    x='date',
    y='CO2 Flux',
    hue='Component',
    marker='o'
)

# Improve legend and appearance
g.add_legend(title="Respiration")
g.set_titles(col_template="{col_name}")
g.tight_layout()

# Format date ticks
for ax in g.axes.flat:
  ax.tick_params(axis='x', rotation=45, labelsize=10)
  ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
  ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

# Save as PNG
plt.savefig('auto_vs_hetero/Autotrophic_vs_heterotrophic_by_treatment.png',
            dpi=600,                    # Very high DPI for manuscripts
            bbox_inches='tight',
            facecolor='white', 
            edgecolor='none',
            format='png',
            pil_kwargs={'optimize': True})

plt.close()



# -----------------------
# Trenched vs. untrenched
# -----------------------
df['trenched'] = df['trenched'].map({True: 'True', False: 'False', pd.NA: 'missing'})

g = sns.FacetGrid(df, col='siteid', col_wrap=4, height=3, aspect=1.2)
#g.map_dataframe(sns.lineplot, x='day_year', y='j_flux', hue='treatment', style='trenched', alpha=0.8, palette=colors)

# Map a lineplot or scatterplot to each facet, colored by Trenched
g.map_dataframe(
  sns.lineplot,
  x = 'day_year',
  y = 'j_flux',
  hue = 'trenched',
  palette = "Set1",
  alpha = 0.8
)

# Get legend handles and labels from the first axis
handles, labels = g.axes.flat[0].get_legend_handles_labels()
# Add legend to the figure
g.fig.legend(handles, labels, title='Trenching', loc='lower right')

# Adjust subplot parameters to make room for legend
plt.subplots_adjust(right=0.78)

# Improve layout
g.set_axis_labels("Date", "CO₂ Flux")
g.set_titles("{col_name}")
g.tight_layout()

# Save as PNG
plt.savefig('auto_vs_hetero/total_vs_hetero_seasonal_comparison.png',
            dpi=600,                    # Very high DPI for manuscripts
            bbox_inches='tight',
            facecolor='white', 
            edgecolor='none',
            format='png',
            pil_kwargs={'optimize': True})

plt.show()


# The timeseries plots are seeminly missing 2 of the 3 german sites.
df['siteid'].nunique()

# ============================================================
# Respiration vs. Temperature/Moisture in different categories
# ============================================================

# lets take a subset with only variables of interest
dfc = df.copy()
variables_of_interest= [
  'date', 'siteid', 't05', 'tsmoisture', 'trenched', 'treatment', 'j_flux', 'day_year', 'year']
dfc = dfc.loc[:,variables_of_interest]
dfc.info()

# define our plotting function
def facet_scatter_regression_plot(data, y_var, x_var, facet_by='siteid', trenched='all', col_wrap=4, height=4):
  """
  Creates faceted scatterplots with regression lines for two selected variables,
  adding correlation coefficient (r) and number of observations (n) to each facet.
  
  Parameters:
      data (DataFrame): The data source
      x_var (str): Column name for x-axis
      y_var (str): Column name for y-axis
      facet_by (str): Column to facet by (default 'country')
      trenched (str): indicator wether to filter data by trenching
      col_wrap (int): Number of plots per row
      height (int): Height of each facet
      
  Returns:
      Seaborn FacetGrid object
  """

  # Label definitions
  var_labels = {
      't05': "Soil temperature (°C) at 5cm",
      'tsmoisture': "Soil moisture at 5cm",
      'j_flux': "CO₂ Flux (g/m⁻² h⁻¹)"
  }

  var_names = {
      't05': "temperature",
      'tsmoisture': "moisture",
      'j_flux': "co2_flux"
  }

  if x_var not in var_labels or y_var not in var_labels:
      raise ValueError(f"x_var or y_var not recognized. Choose from: {list(var_labels.keys())}")

  x_label = var_labels[x_var]
  y_label = var_labels[y_var]
  x_name = var_names[x_var]
  y_name = var_names[y_var]

  # Create the plot
  g = sns.lmplot(
      data=data,
      x=x_var,
      y=y_var,
      col=facet_by,
      col_wrap=col_wrap,
      height=height,
      scatter_kws={
          's': 40,
          'alpha': 0.6,
          'marker': 'o',
          'color': 'blue',
          'edgecolor': 'black'
      },
      line_kws={'color': 'red'}
  )
  
  g.set_axis_labels(x_label, y_label)
  g.set_titles("{col_name}")
  plt.tight_layout()
  
  # Add correlation coefficient and n to each facet
  for ax, facet_value in zip(g.axes.flatten(), g.col_names):
      group_data = data[data[facet_by] == facet_value]
      
      x = group_data[x_var]
      y = group_data[y_var]
      # Drop NaNs
      mask = x.notna() & y.notna()
      x_clean = x[mask]
      y_clean = y[mask]

      if len(x_clean) > 1:
          r, _ = stats.pearsonr(x_clean, y_clean)
          r_text = f"r = {r:.2f}, n = {len(x_clean)}"
      else:
          r_text = f"n = {len(x_clean)}"

      # Annotate inside the top left corner
      ax.text(0.05, 0.95, r_text, transform=ax.transAxes,
              ha='left', va='top', fontsize=10,
              bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.7))

  
  if trenched == 'all':
    directory = 'scatterplots/'
  elif trenched == True:
    directory = 'scatterplots/trenched/'
  elif trenched == False:
    directory = 'scatterplots/untrenched/'
  else:
    raise TypeError("Wrong argument in (trenched). Plot cannot be saved")
  
  # Save before showing (optional)
  filename = f"{y_name}_{x_name}_comparison_by_{facet_by}.png"
  plt.savefig(f"{directory}{filename}",
              dpi=600,
              bbox_inches='tight',
              facecolor='white',
              edgecolor='none',
              format='png',
              pil_kwargs={'optimize': True})
  plt.close()
  
  return g


# ---------------------------------------
# PLOT THIS FOR ALL, TRENCHED, UNTRENCHED
# ALSO WITH DIFFERENT VARIABLES
# ---------------------------------------

# Define all combinations
trenched_options = ['all', True, False]
facet_options = ['siteid', 'treatment']
var_pairs = [
    ('t05', 'j_flux'),
    ('tsmoisture', 'j_flux'),
    ('tsmoisture', 't05'),
]

# Generate and save plots for all trenched conditions
for trenched in trenched_options:
    if trenched == 'all':
        df_sub = dfc  # use the full dataset
    elif trenched is True:
        df_sub = dfc[dfc['trenched'] == 'True']
    elif trenched is False:
        df_sub = dfc[dfc['trenched'] == 'False']
    else:
      raise TypeError("Wrong argument in (trenched). Plot cannot be save")

    for facet_by in facet_options:
        for x_var, y_var in var_pairs:
            print(f"Plotting {y_var} vs. {x_var}, by {facet_by}, trenched = {trenched}")
            facet_scatter_regression_plot(
                data=df_sub,
                x_var=x_var,
                y_var=y_var,
                trenched=trenched,
                facet_by=facet_by
            )
