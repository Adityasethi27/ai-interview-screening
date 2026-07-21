# Statistics and Experimentation

## Populations, samples, and sampling
We estimate properties of a population from a sample. A biased sampling process
(selection bias, survivorship bias) invalidates conclusions no matter how much data
you collect. Random, representative sampling is the foundation of valid inference.

## Descriptive vs inferential statistics
Descriptive statistics summarize data (mean, median, variance, quantiles).
Inferential statistics quantify uncertainty when generalizing from a sample to a
population — confidence intervals and hypothesis tests.

## The Central Limit Theorem
The sampling distribution of the mean approaches a normal distribution as sample
size grows, regardless of the population's shape. This underpins confidence
intervals and many tests, and explains why larger samples give tighter estimates
(standard error shrinks with 1/√n).

## Hypothesis testing
A hypothesis test asks whether observed data is surprising under a **null
hypothesis** (H0, "no effect").
- The **p-value** is the probability of observing data at least as extreme as
  yours *if H0 were true*. A small p-value means the data is unlikely under H0.
- The **significance level α** (often 0.05) is the false-positive rate you accept.
- A **Type I error** rejects a true null (false positive); a **Type II error**
  fails to reject a false null (false negative).
- **Statistical power** (1 − β) is the probability of detecting a real effect;
  it rises with effect size, sample size, and lower variance.
A p-value is **not** the probability the hypothesis is true, and statistical
significance is not practical significance — always report **effect size** and
confidence intervals.

## Common tests
- **t-test**: compare two group means.
- **ANOVA**: compare means across 3+ groups.
- **chi-square**: association between categorical variables.
- **Mann–Whitney / non-parametric**: when normality assumptions fail.
Multiple comparisons inflate false positives; correct with Bonferroni or
Benjamini–Hochberg (FDR).

## A/B testing
An A/B test randomly assigns users to control and treatment to causally measure an
intervention. Key discipline:
- **Randomization** removes confounding.
- Compute the required **sample size** in advance from the minimum detectable
  effect, baseline rate, α, and power — underpowered tests waste traffic.
- Avoid **peeking**: repeatedly checking and stopping when significant inflates
  Type I error; use fixed horizons or sequential testing methods.
- Guard against the **novelty effect**, sample-ratio mismatch, and network effects.
- Track a primary metric plus guardrail metrics so a win on one dimension doesn't
  hide harm on another.

## Correlation vs causation
Correlation measures association; causation requires ruling out confounders,
typically via randomized experiments or careful causal inference (instrumental
variables, difference-in-differences, propensity matching). Observational
correlations are hypotheses, not conclusions.

## Bayesian thinking
The Bayesian view updates a **prior** belief with data (the **likelihood**) to get
a **posterior**. It naturally expresses uncertainty as distributions and is useful
for small-sample problems and sequential decision-making, at the cost of choosing
priors and heavier computation.

## Confidence intervals
A 95% confidence interval means that, under repeated sampling, 95% of such intervals
would contain the true parameter. It communicates precision far better than a point
estimate or a bare p-value.
