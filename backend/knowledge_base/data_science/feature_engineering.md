# Feature Engineering and Data Preparation

## Why features matter
For most tabular problems, feature quality dominates model choice. Feature
engineering encodes domain knowledge into inputs the model can exploit, often
delivering larger gains than swapping algorithms.

## Handling missing data
Missingness is information. Strategies:
- **Deletion** (drop rows/columns) when missingness is rare and random — but it
  discards data and can bias results if missingness is systematic.
- **Imputation**: mean/median (numeric), mode or a distinct "Missing" category
  (categorical), or model-based (KNN, iterative). Add a **missing-indicator** flag
  so the model can learn from the fact that a value was absent.
Fit imputation on the training folds only to avoid leakage.

## Encoding categorical variables
- **One-hot encoding** creates a binary column per category — safe for low
  cardinality but explodes dimensionality for high-cardinality features.
- **Ordinal encoding** assigns integers when categories have a natural order.
- **Target/mean encoding** replaces a category with the mean target — powerful for
  high cardinality but leaks the target unless done inside cross-validation with
  smoothing.
- **Hashing** trades collisions for fixed dimensionality at very high cardinality.

## Scaling and normalization
Distance- and gradient-based models (KNN, SVM, linear models, neural nets) are
sensitive to feature scale.
- **Standardization** (z-score: subtract mean, divide by std) centers and scales.
- **Min–max normalization** maps to [0, 1].
- **Robust scaling** uses median and IQR, resisting outliers.
Tree-based models are scale-invariant and generally need no scaling. Always fit the
scaler on training data and apply the same transform to validation/test.

## Outliers and skew
Detect outliers with z-scores, IQR, or model-based methods. Depending on cause,
cap (winsorize), transform, or keep them. Right-skewed features (income, counts)
often benefit from **log** or Box-Cox transforms to stabilize variance and linearize
relationships.

## Feature creation
- **Interaction features** (products/ratios) capture combined effects.
- **Datetime decomposition** into hour/day/month/weekend and cyclical encodings
  (sin/cos) exposes seasonality.
- **Aggregations** (group-by counts, means, recency) summarize related records.
- **Text** becomes features via bag-of-words, TF-IDF, or embeddings.
- **Binning** turns continuous variables into categories to capture nonlinearity.

## Feature selection
Fewer, better features reduce overfitting, speed training, and aid interpretability.
- **Filter methods**: rank by correlation, mutual information, or variance.
- **Wrapper methods**: recursive feature elimination using model performance.
- **Embedded methods**: L1 regularization or tree feature importances select during
  training.
Watch for **multicollinearity** (highly correlated features), which destabilizes
linear-model coefficients even if it doesn't hurt predictions.

## Pipelines and leakage prevention
Wrap preprocessing and the model in a single pipeline so every transform is fit on
training data only and reproduced identically at inference. This prevents **data
leakage**, the most common cause of models that look great offline and fail in
production.
