# Modeling and Applied Algorithms

## Model families and when to use them
- **Linear/logistic regression**: interpretable baselines; strong when the
  relationship is roughly linear and you need coefficients you can explain.
- **Decision trees**: capture nonlinearity and interactions, need little
  preprocessing, but overfit easily alone.
- **k-nearest neighbors**: simple, non-parametric; suffers in high dimensions and
  at inference cost.
- **Support vector machines**: effective in high-dimensional spaces with clear
  margins; kernels handle nonlinearity.
- **Ensembles** (below): usually the best off-the-shelf performance on tabular data.
Always start with a simple, well-understood baseline before reaching for complexity.

## Ensemble methods
Ensembles combine many models to beat any single one by reducing bias or variance.
- **Bagging** (e.g. **Random Forests**) trains many high-variance models on
  bootstrapped samples and averages them, reducing **variance**. Random Forests
  also randomize the features considered per split to decorrelate trees.
- **Boosting** (e.g. **Gradient Boosting**, XGBoost, LightGBM) trains models
  sequentially, each correcting the previous one's errors, reducing **bias**.
  Powerful but more prone to overfitting and sensitive to hyperparameters and
  noisy labels.
- **Stacking** trains a meta-model on the predictions of diverse base models.
Bagging parallelizes and is robust; boosting is sequential and often more accurate
with careful tuning.

## Dimensionality reduction
High-dimensional data is sparse, slow, and prone to overfitting (curse of
dimensionality).
- **PCA** projects data onto orthogonal directions of maximum variance, an
  unsupervised linear method useful for compression, denoising, and visualization;
  components are ranked by explained variance. It assumes variance equals
  information and requires scaling first.
- **t-SNE / UMAP** are nonlinear techniques for visualization that preserve local
  structure but distort global distances — use for exploration, not as model inputs.
- **Feature selection** reduces dimensions while keeping interpretability, unlike
  PCA which produces abstract combined components.

## Clustering
Unsupervised grouping of similar points.
- **k-means** partitions into k spherical clusters by minimizing within-cluster
  variance; you must choose k (elbow/silhouette) and it is sensitive to scaling and
  initialization.
- **Hierarchical clustering** builds a dendrogram, no preset k, but is costlier.
- **DBSCAN** finds density-based clusters of arbitrary shape and labels outliers,
  without needing k.

## Handling imbalanced data
When one class is rare, models optimize overall accuracy by ignoring the minority.
Remedies:
- **Resampling**: oversample the minority (**SMOTE** synthesizes new minority
  points) or undersample the majority.
- **Class weights**: penalize minority errors more in the loss.
- **Threshold tuning**: move the decision threshold using a precision–recall
  tradeoff rather than defaulting to 0.5.
- **Right metrics**: evaluate with precision, recall, F1, and PR-AUC — never plain
  accuracy.
Apply resampling only to training folds, never to validation/test, to avoid leakage.

## Interpretability
Stakeholders often need to know *why* a model predicts what it does.
- **Global**: coefficients, tree feature importances, permutation importance.
- **Local**: **SHAP** and LIME explain individual predictions.
Interpretability supports debugging, fairness auditing, and trust — sometimes worth
trading a little accuracy for a model people will actually deploy.

## From model to decision
A good data scientist connects the model to the business decision it informs:
choosing the metric that reflects real costs, quantifying uncertainty, monitoring
for **data drift** after deployment, and retraining as the data distribution shifts.
