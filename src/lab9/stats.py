"""Statistics students implement (M2 judge calibration, M4 paired bootstrap).

Rules: a judge is a classifier -- measure it like one. A higher mean is not
"better" until the paired CI of the difference excludes 0.
Reference values to self-check are in tests/test_lab9_stats.py.
"""

from __future__ import annotations

from collections.abc import Sequence

POS = "FAIL"   # the judge's job is to FIND failures, so FAIL is the positive class


def confusion(human: Sequence[str], judge: Sequence[str]) -> dict[str, int]:
    """tp/fp/fn/tn with FAIL as positive."""
    tp = fp = fn = tn = 0
    for h, j in zip(human, judge, strict=True):
        if h == POS and j == POS:
            tp += 1
        elif h != POS and j == POS:
            fp += 1
        elif h == POS and j != POS:
            fn += 1
        else:
            tn += 1
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn}


def precision_recall(human: Sequence[str], judge: Sequence[str]) -> tuple[float, float]:
    cm = confusion(human, judge)
    p_den = cm["tp"] + cm["fp"]
    r_den = cm["tp"] + cm["fn"]
    precision = cm["tp"] / p_den if p_den else 0.0
    recall = cm["tp"] / r_den if r_den else 0.0
    return (precision, recall)


def cohen_kappa(human: Sequence[str], judge: Sequence[str]) -> float:
    """kappa = (p_o - p_e) / (1 - p_e). Raise ValueError when undefined (p_e == 1):
    a constant judge has no signal and must FAIL calibration, not pass on a technicality."""
    n = len(human)
    if n == 0:
        raise ValueError("empty sequences")
    cm = confusion(human, judge)
    p_o = (cm["tp"] + cm["tn"]) / n
    p_e = ((cm["tp"] + cm["fp"]) * (cm["tp"] + cm["fn"]) + (cm["fn"] + cm["tn"]) * (cm["fp"] + cm["tn"])) / (n * n)
    if p_e >= 1.0 - 1e-12:
        raise ValueError("kappa is undefined when p_e == 1")
    return (p_o - p_e) / (1.0 - p_e)


def rogan_gladen(observed_rate: float, sensitivity: float, specificity: float) -> float:
    """Correct an observed failure rate for judge error; clip to [0, 1]."""
    denom = sensitivity + specificity - 1.0
    if denom == 0:
        return max(0.0, min(1.0, float(observed_rate)))
    val = (observed_rate + specificity - 1.0) / denom
    return max(0.0, min(1.0, float(val)))


def paired_bootstrap(a: Sequence[float], b: Sequence[float], *, n_resamples: int = 1000,
                     rng: int = 2027, confidence: float = 0.95) -> tuple[float, float, float]:
    """a[i], b[i] = per-item mean over seeds, SAME items, SAME order.
    Return (mean(a)-mean(b), lo, hi) with scipy.stats.bootstrap(paired=True, method="percentile",
    rng=numpy.random.default_rng(rng)). If a == b everywhere return (0.0, 0.0, 0.0)."""
    import numpy as np
    from scipy.stats import bootstrap

    a_arr = np.asarray(a, dtype=float)
    b_arr = np.asarray(b, dtype=float)
    if len(a_arr) == 0 or np.array_equal(a_arr, b_arr):
        return (0.0, 0.0, 0.0)
    diff = float(np.mean(a_arr) - np.mean(b_arr))
    res = bootstrap(
        (a_arr, b_arr),
        lambda x, y: np.mean(x - y),
        paired=True,
        n_resamples=n_resamples,
        confidence_level=confidence,
        method="percentile",
        rng=np.random.default_rng(rng),
    )
    return (diff, float(res.confidence_interval.low), float(res.confidence_interval.high))


def pass_at_k(n: int, c: int, k: int) -> float:
    """Probability that AT LEAST ONE of k trials drawn from n (c of them passing) passes.
    Unbiased estimator (Chen et al. 2021): 1 - C(n-c, k) / C(n, k). Raise ValueError if k > n."""
    import math

    if n <= 0 or k <= 0 or k > n or c < 0 or c > n:
        raise ValueError(f"invalid args for pass_at_k: n={n}, c={c}, k={k}")
    if n - c < k:
        return 1.0
    return 1.0 - math.comb(n - c, k) / math.comb(n, k)


def pass_hat_k(n: int, c: int, k: int) -> float:
    """pass^k (tau-bench, Yao et al. 2024): probability that ALL k trials drawn from n pass.
    Unbiased estimator: C(c, k) / C(n, k). Raise ValueError if k > n.
    pass^k <= pass@1 <= pass@k; a reliable agent keeps pass^k close to pass@1."""
    import math

    if n <= 0 or k <= 0 or k > n or c < 0 or c > n:
        raise ValueError(f"invalid args for pass_hat_k: n={n}, c={c}, k={k}")
    if c < k:
        return 0.0
    return math.comb(c, k) / math.comb(n, k)
