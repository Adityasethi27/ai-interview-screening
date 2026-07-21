# Optimization, Training, and Neural Networks

## Loss functions
Training minimizes a loss that measures disagreement between predictions and
targets. Common choices:
- **Mean squared error** for regression (penalizes large errors quadratically).
- **Mean absolute error** for regression when robustness to outliers matters.
- **Cross-entropy / log loss** for classification, which measures the distance
  between predicted probability distributions and true labels and pairs naturally
  with softmax/sigmoid outputs.
Choosing a loss encodes what kind of mistakes you care about.

## Gradient descent
Gradient descent updates parameters in the direction that most reduces the loss:
`θ ← θ − η · ∇L(θ)`, where `η` is the learning rate.
- **Batch gradient descent** uses the whole dataset per step: stable but slow.
- **Stochastic gradient descent (SGD)** uses one sample per step: noisy but fast
  and able to escape shallow local minima.
- **Mini-batch** (the usual choice) balances the two and exploits vectorized
  hardware.
The **learning rate** is the most important hyperparameter: too high diverges,
too low crawls or gets stuck. Learning-rate schedules (decay, warmup) and
adaptive optimizers help.

## Adaptive optimizers and momentum
- **Momentum** accumulates a moving average of past gradients to dampen
  oscillations and accelerate along consistent directions.
- **RMSProp** scales each parameter's step by a running average of squared
  gradients.
- **Adam** combines momentum and per-parameter scaling and is a strong default,
  though well-tuned SGD with momentum can generalize better on some tasks.

## Backpropagation
Backpropagation computes gradients of the loss with respect to every parameter by
applying the chain rule from the output backward through the network. Each layer
receives the gradient of the loss with respect to its output and propagates the
gradient with respect to its input and weights. It is what makes training deep
networks computationally feasible.

## Neural network building blocks
- **Neurons and layers**: a layer computes a linear transform (weights + bias)
  followed by a nonlinear **activation** (ReLU, sigmoid, tanh). Without
  nonlinearity, stacked linear layers collapse into a single linear map.
- **ReLU** (`max(0, x)`) is the default hidden activation: cheap, mitigates
  vanishing gradients, but can "die" if too many units output zero.
- **Softmax** turns logits into a probability distribution for multi-class output.

## Vanishing and exploding gradients
In deep networks, repeated multiplication of small (or large) derivatives makes
gradients shrink toward zero or blow up, stalling or destabilizing training.
Mitigations: ReLU-family activations, careful weight initialization (He/Xavier),
**batch normalization**, residual/skip connections, and gradient clipping.

## Regularization in deep learning
- **Dropout** randomly zeroes activations during training, preventing co-adaptation
  and acting like an ensemble of subnetworks.
- **Weight decay** is L2 regularization applied during optimization.
- **Early stopping** halts training when validation loss stops improving.
- **Data augmentation** synthesizes new training examples (crops, flips, noise).

## Hyperparameters vs parameters
Parameters (weights) are learned from data. Hyperparameters (learning rate, number
of layers, regularization strength, batch size) are set before training and tuned
on validation data via grid search, random search, or Bayesian optimization.

## Bias-variance in practice for neural nets
Modern deep networks are heavily over-parameterized yet generalize well when
trained with SGD and regularization — an active research area. Practically, you
diagnose with learning curves: high training error → underfitting (grow the model
or train longer); low training but high validation error → overfitting (regularize
or add data).
