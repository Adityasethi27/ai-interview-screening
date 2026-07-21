# Model Evaluation and Metrics

## Why accuracy is not enough
Accuracy (fraction correct) is misleading on **imbalanced** datasets. If 99% of
emails are not spam, a model that always predicts "not spam" is 99% accurate yet
useless. Evaluation must match the real cost of different error types.

## The confusion matrix
For binary classification, predictions fall into four buckets: true positives
(TP), false positives (FP), true negatives (TN), false negatives (FN). Most
metrics are derived from these.

- **Precision** = TP / (TP + FP): of the items predicted positive, how many are
  actually positive. High precision means few false alarms.
- **Recall (sensitivity)** = TP / (TP + FN): of the actual positives, how many did
  we catch. High recall means few misses.
- **F1 score** = harmonic mean of precision and recall: a single number when you
  need to balance the two.
- **Specificity** = TN / (TN + FP): true-negative rate.

## Precision–recall tradeoff
Lowering the decision threshold catches more positives (higher recall) at the cost
of more false positives (lower precision). The right operating point depends on
costs: cancer screening favors recall; spam filtering that must not lose real mail
favors precision.

## ROC and PR curves
- The **ROC curve** plots true-positive rate against false-positive rate across
  thresholds; **AUC** (area under it) summarizes ranking quality independent of
  threshold. AUC of 0.5 is random, 1.0 is perfect.
- The **precision–recall curve** is more informative than ROC on highly
  imbalanced data because it focuses on the positive class.

## Regression metrics
- **MAE** (mean absolute error): average absolute deviation, robust to outliers.
- **MSE / RMSE**: penalize large errors more; RMSE is in the target's units.
- **R²** (coefficient of determination): fraction of variance explained; can be
  negative if the model is worse than predicting the mean.

## Cross-validation
**k-fold cross-validation** splits data into k folds, trains on k−1 and validates
on the held-out fold, rotating k times and averaging. It gives a more reliable
estimate than a single split and uses data efficiently. **Stratified** k-fold
preserves class proportions in each fold — important for imbalanced classification.
For time series, use forward-chaining splits so the model never trains on the
future.

## Data leakage
Leakage is when information unavailable at prediction time sneaks into training,
producing optimistic offline metrics that collapse in production. Classic causes:
fitting scalers/encoders on the full dataset before splitting, target-derived
features, or duplicated rows across train and test. Fit all preprocessing inside
the cross-validation loop, on training folds only.

## Calibration
A classifier is **calibrated** if its predicted probabilities match observed
frequencies (among samples predicted 0.8, about 80% are positive). Calibration
matters when probabilities feed downstream decisions. Check with reliability
diagrams; fix with Platt scaling or isotonic regression.

## Choosing a metric
Pick the metric before modeling, aligned to the business objective and error
costs. Track a single primary metric for model selection plus guardrail metrics
(latency, fairness across groups) so improving one number does not silently harm
another.
