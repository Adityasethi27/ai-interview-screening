# Machine Learning Fundamentals

## What learning means
A machine learning model is a function whose parameters are fit from data rather
than hand-coded. We assume the data is drawn from some unknown distribution and
the goal is **generalization**: performing well on new, unseen samples from that
same distribution, not merely memorizing the training set.

## Supervised, unsupervised, and reinforcement learning
- **Supervised learning** uses labeled examples `(x, y)`. The model learns a
  mapping from inputs to targets. Classification predicts discrete labels;
  regression predicts continuous values.
- **Unsupervised learning** has no labels. It finds structure: clustering groups
  similar points, dimensionality reduction compresses features, density
  estimation models the data distribution.
- **Reinforcement learning** learns a policy by interacting with an environment
  and receiving rewards; it optimizes long-term cumulative reward rather than
  fitting fixed targets.

## The bias–variance tradeoff
Generalization error can be decomposed into three parts: **bias**, **variance**,
and irreducible noise.
- **Bias** is error from wrong assumptions — a model too simple to capture the
  underlying pattern (underfitting). High-bias models have high training *and*
  test error.
- **Variance** is sensitivity to the particular training set — a model so
  flexible it fits noise (overfitting). High-variance models have low training
  error but high test error.
Increasing model capacity typically lowers bias but raises variance. The art is
choosing capacity (and regularization) that minimizes total error. More training
data reduces variance without increasing bias, which is why data often beats
model complexity.

## Overfitting and underfitting
**Overfitting** happens when a model captures noise specific to the training set.
Symptoms: a widening gap between training and validation performance. Remedies:
- more data or data augmentation,
- reducing model capacity (fewer parameters, shallower trees),
- **regularization**,
- early stopping,
- dropout (for neural networks),
- cross-validation to tune hyperparameters honestly.

**Underfitting** is the opposite: the model is too constrained. Remedies include
adding features, increasing capacity, training longer, or reducing regularization.

## Regularization
Regularization discourages overly complex solutions by adding a penalty to the
loss.
- **L2 (ridge)** penalizes the sum of squared weights, shrinking weights toward
  zero smoothly and improving conditioning.
- **L1 (lasso)** penalizes the sum of absolute weights, driving some exactly to
  zero and thus performing feature selection.
- **Elastic net** combines L1 and L2.
The regularization strength (often λ) trades training fit against weight size and
is tuned on a validation set. Conceptually, regularization is a way of encoding a
prior preference for simpler hypotheses (Occam's razor).

## Train / validation / test discipline
Split data into training (fit parameters), validation (tune hyperparameters and
choose models), and test (a single, final, untouched estimate of generalization).
Any decision made using the test set leaks information and inflates the estimate.
For small datasets, **k-fold cross-validation** reuses data efficiently by
rotating which fold serves as validation.

## The curse of dimensionality
As the number of features grows, the volume of the input space grows
exponentially and data becomes sparse. Distances become less meaningful and more
data is needed to cover the space. This motivates feature selection,
dimensionality reduction, and models with strong inductive biases.

## No free lunch
No single learning algorithm is optimal across all possible problems. Performance
depends on how well a model's assumptions (inductive bias) match the true
structure of the data. This is why practitioners try multiple model families and
validate empirically rather than trusting one method universally.
