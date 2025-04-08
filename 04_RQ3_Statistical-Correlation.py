### This code is used to calculate the statistical (significant) correlation analysis between the crystal occurence and the elevaltion level. 
### The result is used for the RQ3 analysis.

# --- STEP 0: IMPORT NECESSARY LIBRARIES ---
import pandas as pd
from scipy.stats import pearsonr, spearmanr
import statsmodels.formula.api as smf
import seaborn as sns
import matplotlib.pyplot as plt


# --- STEP 1: LOAD & CLEAN DATASET ---
# Load your finalized dataset
df = pd.read_excel("03_Finalized_Dataset.xlsx")

# Drop rows with missing values in relevant columns
df_clean = df.dropna(subset=["Altitude", "Mineral", "Mineral Category", "Altitude Category"])


# --- STEP 2: ENCODE CATEGORICAL VARIABLES ---
# Encode string columns for correlation/regression
df_clean["Mineral_enc"] = df_clean["Mineral"].astype("category").cat.codes
df_clean["Mineral_Category_enc"] = df_clean["Mineral Category"].astype("category").cat.codes
df_clean["Altitude_Category_enc"] = df_clean["Altitude Category"].astype("category").cat.codes


# --- STEP 3: FUNCTION FOR CORRELATION & REGRESSION ANALYSIS ---
# This function performs Pearson and Spearman correlation, as well as linear regression analysis. It also prints the results in a formatted manner.
def run_analysis(x, y, df, label):
    pearson_corr, pearson_p = pearsonr(df[x], df[y])
    spearman_corr, spearman_p = spearmanr(df[x], df[y])
    model = smf.ols(f"{y} ~ {x}", data=df).fit()

    print(f"\n--- {label} ---")
    print(f"Pearson r = {pearson_corr:.3f}, p = {pearson_p:.4f}")
    print(f"Spearman ρ = {spearman_corr:.3f}, p = {spearman_p:.4f}")
    print(f"Linear Regression R² = {model.rsquared:.3f}, Model p = {model.f_pvalue:.4f}")

    if pearson_p < 0.001:
        print("➡ Highly statistically significant (p < 0.001)")
    elif pearson_p < 0.05:
        print("➡ Statistically significant (p < 0.05)")
    else:
        print("➡ Not statistically significant")


# --- STEP 4: RUN ANALYSIS FOR ALL COMBINATIONS ---
# The following combinations will be analyzed:
# 1. Altitude vs Mineral
run_analysis("Altitude", "Mineral_enc", df_clean, "Altitude vs Mineral")

# 2. Altitude vs Mineral Category
run_analysis("Altitude", "Mineral_Category_enc", df_clean, "Altitude vs Mineral Category")

# 3. Altitude Category vs Mineral
run_analysis("Altitude_Category_enc", "Mineral_enc", df_clean, "Altitude Category vs Mineral")

# 4. Altitude Category vs Mineral Category
run_analysis("Altitude_Category_enc", "Mineral_Category_enc", df_clean, "Altitude Category vs Mineral Category")


# --- STEP 5: 2x2 VISUALIZATION OF ALL COMBINATIONS (SCATTERPLOTS) ---

# Create scatter plot layout
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("All Scatter Plots – Altitude Relationships", fontsize=16)

# Plot 1: Altitude vs Mineral (encoded) 
sns.scatterplot(x="Altitude", y="Mineral_enc", data=df_clean, ax=axes[0, 0], alpha=0.5)
axes[0, 0].set_title("Altitude vs Mineral")
axes[0, 0].set_xlabel("Altitude")
axes[0, 0].set_ylabel("Mineral (encoded)")

# Plot 2: Altitude vs Mineral Category (encoded)
sns.scatterplot(x="Altitude", y="Mineral_Category_enc", data=df_clean, ax=axes[0, 1], alpha=0.5)
axes[0, 1].set_title("Altitude vs Mineral Category")
axes[0, 1].set_xlabel("Altitude")
axes[0, 1].set_ylabel("Mineral Category (encoded)")

# Plot 3: Altitude Category (encoded) vs Mineral (encoded)
sns.scatterplot(x="Altitude_Category_enc", y="Mineral_enc", data=df_clean, ax=axes[1, 0], alpha=0.5)
axes[1, 0].set_title("Altitude Category vs Mineral")
axes[1, 0].set_xlabel("Altitude Category (encoded)")
axes[1, 0].set_ylabel("Mineral (encoded)")

# Plot 4: Altitude Category (encoded) vs Mineral Category (encoded)
sns.scatterplot(x="Altitude_Category_enc", y="Mineral_Category_enc", data=df_clean, ax=axes[1, 1], alpha=0.5)
axes[1, 1].set_title("Altitude Category vs Mineral Category")
axes[1, 1].set_xlabel("Altitude Category (encoded)")
axes[1, 1].set_ylabel("Mineral Category (encoded)")

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()


# --- STEP 6: 2x1 VISUALIZATION OF MINERAL CATEGORY COMBINATIONS (BOXPLOTS) ---
# This section creates box plots to visualize the distribution of altitude and altitude categories across different mineral categories. 
# There was no boxplot created for the minerals itself as it would be too crowded and not meaningful.

# Create box plot layout
fig, axes = plt.subplots(2, 1, figsize=(14, 10))
fig.suptitle("Box Plots – Mineral Category vs Altitude / Altitude Category", fontsize=16)

# Plot 1: Altitude vs Mineral Category
sns.boxplot(x="Mineral Category", y="Altitude", data=df_clean, ax=axes[0])
axes[0].set_title("Altitude vs Mineral Category")
axes[0].set_xlabel("Mineral Category")
axes[0].set_ylabel("Altitude (m)")
axes[0].tick_params(labelrotation=90)

# Plot 2: Altitude Category (encoded) vs Mineral Category
sns.boxplot(x="Mineral Category", y="Altitude_Category_enc", data=df_clean, ax=axes[1])
axes[1].set_title("Altitude Category vs Mineral Category")
axes[1].set_xlabel("Mineral Category")
axes[1].set_ylabel("Altitude Category (encoded)")
axes[1].tick_params(labelrotation=90)

# Layout adjustments
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()


# --- STEP 7: 2x2 VISUALIZATION OF ALL COMBINATIONS (HISTOGRAMS) ---
# This section creates histograms to visualize the distribution of altitude and mineral and their categories.

# Create histogram layout
plt.figure(figsize=(12, 6))

# Plot 1: Histogram of Mineral Category by Altitude Category
sns.histplot(data=df_clean, x="Mineral Category", hue="Altitude Category", multiple="stack")
plt.title("Mineral Category by Altitude Category")
plt.xlabel("Mineral Category")
plt.ylabel("Count")
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()
