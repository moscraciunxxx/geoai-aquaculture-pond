# Trustworthiness Evaluation

## 1. Data and model bias

Train and test represent different time periods, and the test rows expose only
consecutive 4-, 5-, or 6-month observation windows. Optical observations also
drop out unevenly by month. Training only on complete annual rows would therefore
overstate performance. The candidate mitigates this by training on deterministic
test-shaped masked views and by retaining missingness indicators and window
length. The training positive rate is 0.4036, while the test prior is unknown;
the submitted probability is not post-hoc threshold-tuned. Regional bias cannot
be measured because coordinates and region labels are not supplied.

## 2. Model transparency

Clean candidates use supplied monthly bands: robust indices, temporal changes,
wet/dry fractions, and cross-band correlations. LightGBM uses fixed seeds,
deterministic settings, declared weights, and no external data. We did not run
SHAP or LIME; instead, [this diagnostic figure](eda/trustworthiness_shift.png)
shows the observable shift and missingness addressed by the feature blocks.
Train-side ablations identify water indices, SAR contrast, and temporal
stability as key groups. Unexpectedly, absolute radiometric levels were highly
predictive in Train but failed after the shift. v4 is separately labelled a
public-feedback splice, not a clean model.

## 3. Approach reusability

The notebook and flagship builder run from the supplied Train, Test, and sample
files. The flagship’s `--fresh` mode refuses caches whose raw-data, source,
configuration, dependency, or platform provenance differs. Window-relative
summaries and deterministic masking make the workflow adaptable to monthly
satellite tasks with partial observation. Exact-mask experiments use only
unlabelled Test availability patterns, never Test labels. Reuse still requires
changing band definitions and retraining for a new target. A different sensor,
region, seasonal cycle, or cloud process can invalidate both the feature
invariances and mask simulator, so transfer must be revalidated rather than
assumed.

## 4. Sustainability and efficiency

The candidate is CPU-only, uses a compact engineered feature table, deterministic
LightGBM, and no external service or GPU. The final fit expands the 1,821 labelled
rows into 24 deterministic observation-window views and trains fixed boosting
ensembles. Runtime and energy were not measured with CodeCarbon or
hardware counters, so no numerical emissions claim is made. The deliberate
trade-off is a small amount of extra CPU work for reproducibility and robustness
to the test masking process.
