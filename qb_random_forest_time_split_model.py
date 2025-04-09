# =====================================================
# 版本：time_split_model.py（有時間性控制，預測任務用）
# =====================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import cross_val_score, learning_curve
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# Load QB data
qb = pd.read_csv("dat/qb_stats.csv")

# Sort by time to simulate real game sequence
qb = qb.sort_values(by=['gsis_id', 'season', 'week'])

# Create rolling average features (last 3 games)
qb['rolling_pass_yards'] = qb.groupby('gsis_id')['pass_yards'].rolling(3, min_periods=1).mean().reset_index(0, drop=True)
qb['rolling_completions'] = qb.groupby('gsis_id')['completions'].rolling(3, min_periods=1).mean().reset_index(0, drop=True)
qb['rolling_pass_tds'] = qb.groupby('gsis_id')['pass_touchdowns'].rolling(3, min_periods=1).mean().reset_index(0, drop=True)
qb['rolling_interceptions'] = qb.groupby('gsis_id')['interceptions'].rolling(3, min_periods=1).mean().reset_index(0, drop=True)

# Split based on week number: train on week <= 10, test on week > 10
train_data = qb[qb['week'] <= 10].copy()
test_data = qb[qb['week'] > 10].copy()

# Feature selection and preprocessing
train_features = train_data.drop(columns=['avg_epa','gsis_id', 'position', 'depth_chart_position', 'full_name', 'total_epa', 'third_down_rate', 'fourth_down_rate'])
train_features = pd.get_dummies(train_features, columns=['team'])
train_features['birth_date'] = pd.to_datetime(train_features['birth_date'])
train_features['birth_year'] = train_features['birth_date'].dt.year
train_features = train_features.drop(columns=['birth_date'])
train_features = train_features.dropna()
y_train = train_data.loc[train_features.index, 'avg_epa']

# Prepare test set with aligned columns
test_features = test_data[train_features.columns.intersection(test_data.columns)].copy()
test_features = test_features.dropna()
y_test = test_data.loc[test_features.index, 'avg_epa']

# Train model
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(train_features, y_train)

# Predict and evaluate
y_pred = rf_model.predict(test_features)
rmse = lambda y_true, y_pred: np.sqrt(mean_squared_error(y_true, y_pred))
print("QB RMSE:", rmse(y_test, y_pred))
print("QB R2:", r2_score(y_test, y_pred))

# Cross-validation on training set only
cv_rmse_scores = cross_val_score(rf_model, train_features, y_train, cv=5, scoring='neg_root_mean_squared_error')
cv_r2_scores = cross_val_score(rf_model, train_features, y_train, cv=5, scoring='r2')
print(f"Cross-validated RMSE: {-cv_rmse_scores.mean():.3f} ± {cv_rmse_scores.std():.3f}")
print(f"Cross-validated R²: {cv_r2_scores.mean():.3f} ± {cv_r2_scores.std():.3f}")

# Learning curve
train_sizes, train_scores, test_scores = learning_curve(
    rf_model,
    train_features, y_train,
    cv=5,
    scoring='r2',
    train_sizes=np.linspace(0.1, 1.0, 10)
)

train_mean = np.mean(train_scores, axis=1)
test_mean = np.mean(test_scores, axis=1)

plt.figure(figsize=(10, 6))
plt.plot(train_sizes, train_mean, label="Training score")
plt.plot(train_sizes, test_mean, label="Cross-validation score")
plt.xlabel("Training Set Size")
plt.ylabel("R² Score")
plt.title("Learning Curve (Random Forest - Time Aware)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Feature importance
feature_importance = pd.Series(rf_model.feature_importances_, index=train_features.columns).sort_values(ascending=False)
print("Top 10 Feature Importances:")
print(feature_importance.head(10))
