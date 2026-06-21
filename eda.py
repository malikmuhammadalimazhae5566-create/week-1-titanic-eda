import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def main():
    # Create directory for visualizations
    os.makedirs('visualizations', exist_ok=True)
    
    print("Loading Titanic Dataset...")
    # Load Titanic dataset from seaborn
    df = sns.load_dataset('titanic')
    
    print("\n--- Initial Data Info ---")
    print(df.info())
    print("\n--- Missing Values Before Cleaning ---")
    print(df.isnull().sum())
    
    print("\nCleaning Data...")
    # 1. Handle 'deck' column (too many missing values, drop it)
    df.drop(columns=['deck'], inplace=True, errors='ignore')
    
    # 2. Fill 'age' with median
    df['age'] = df['age'].fillna(df['age'].median())
    
    # 3. Fill 'embarked' and 'embark_town' with mode
    mode_embarked = df['embarked'].mode()[0]
    df['embarked'] = df['embarked'].fillna(mode_embarked)
    
    mode_embark_town = df['embark_town'].mode()[0]
    df['embark_town'] = df['embark_town'].fillna(mode_embark_town)
    
    print("\n--- Missing Values After Cleaning ---")
    print(df.isnull().sum())
    
    print("\nGenerating Visualizations...")
    
    sns.set_theme(style="whitegrid")
    
    # Visualization 1: Count of Survived
    plt.figure(figsize=(8, 5))
    sns.countplot(data=df, x='survived', palette='Set2')
    plt.title('1. Survival Count (0 = No, 1 = Yes)')
    plt.xlabel('Survived')
    plt.ylabel('Count')
    plt.savefig('visualizations/1_survival_count.png', bbox_inches='tight')
    plt.close()
    
    # Visualization 2: Survival by Sex
    plt.figure(figsize=(8, 5))
    sns.countplot(data=df, x='survived', hue='sex', palette='Pastel1')
    plt.title('2. Survival Count by Sex')
    plt.xlabel('Survived')
    plt.ylabel('Count')
    plt.savefig('visualizations/2_survival_by_sex.png', bbox_inches='tight')
    plt.close()
    
    # Visualization 3: Age Distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x='age', bins=30, kde=True, color='skyblue')
    plt.title('3. Distribution of Passenger Ages')
    plt.xlabel('Age')
    plt.ylabel('Frequency')
    plt.savefig('visualizations/3_age_distribution.png', bbox_inches='tight')
    plt.close()
    
    # Visualization 4: Boxplot of Fare by Pclass
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x='pclass', y='fare', palette='Set3')
    plt.title('4. Fare Distribution by Passenger Class')
    plt.xlabel('Passenger Class (Pclass)')
    plt.ylabel('Fare')
    plt.ylim(-10, 200) # Limiting y-axis to focus on the main distribution and hide extreme outliers
    plt.savefig('visualizations/4_fare_by_pclass.png', bbox_inches='tight')
    plt.close()
    
    # Visualization 5: Correlation Heatmap of Numeric Columns
    plt.figure(figsize=(10, 8))
    numeric_cols = df.select_dtypes(include=['int64', 'float64', 'bool']).columns
    correlation_matrix = df[numeric_cols].corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", vmin=-1, vmax=1)
    plt.title('5. Correlation Heatmap of Numeric Features')
    plt.savefig('visualizations/5_correlation_heatmap.png', bbox_inches='tight')
    plt.close()
    
    print("Visualizations saved to 'visualizations' folder.")
    print("\n--- Summary Statistics ---")
    print(df.describe())
    
if __name__ == "__main__":
    main()
