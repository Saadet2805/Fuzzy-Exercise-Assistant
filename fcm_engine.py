"""FCM inference — uses fcmpy when installed, else native mKosko + sigmoid."""

import numpy as np
import pandas as pd

NODES = [
    "BMI",
    "Fitness_Lvl",
    "Goal_MuscleGain",
    "Goal_WeightLoss",
    "Rec_Light_Cardio",
    "Rec_Strength",
    "Rec_HIIT",
    "Rec_Beginner",
]

OUTPUT_NODES = [
    "Rec_Light_Cardio",
    "Rec_Strength",
    "Rec_HIIT",
    "Rec_Beginner",
]

WEIGHTS = np.array(
    [
        [0, 0, 0, 0, 0.7, 0.2, -0.3, 0.8],
        [0, 0, 0, 0, -0.2, 0.7, 0.9, -0.8],
        [0, 0, 0, 0, -0.2, 1.0, 0.2, 0.0],
        [0, 0, 0, 0, 0.6, 0.3, 0.8, 0.0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]
)

WEIGHT_MATRIX = pd.DataFrame(WEIGHTS, columns=NODES, index=NODES)

_USE_FCMPY = False
_SIMULATOR = None

try:
    from fcmpy import FcmSimulator

    _SIMULATOR = FcmSimulator()
    _USE_FCMPY = True
except ImportError:
    pass


def slider_to_fuzzy(value: int | float) -> float:
    """Map frontend slider 1–10 to fuzzy activation 0–1."""
    v = int(round(float(value)))
    v = max(1, min(10, v))
    return (v - 1) / 9.0


def bmi_to_fuzzy(bmi: float) -> float:
    """
    Map real BMI (kg/m²) to fuzzy 0–1 for the FCM.
    ~18.5 = lower end, ~35 = higher end (expert-style scale for the model).
    """
    bmi = float(bmi)
    low, high = 18.5, 35.0
    return float(max(0.0, min(1.0, (bmi - low) / (high - low))))


def _sigmoid(x: np.ndarray, steepness: float = 1.0) -> np.ndarray:
    z = np.clip(steepness * x, -500, 500)
    return 1.0 / (1.0 + np.exp(-z))


def _stable_concept_mask(weight_matrix: pd.DataFrame) -> np.ndarray:
    """Concepts with no incoming edges stay fixed (same as fcmpy in-degree == 0)."""
    w = weight_matrix.values.astype(float)
    return np.all(w == 0, axis=0)


def _simulate_native(
    initial_state: dict,
    weight_matrix: pd.DataFrame,
    thresh: float = 0.001,
    iterations: int = 50,
    steepness: float = 1.0,
) -> pd.DataFrame:
    """
    mKosko + sigmoid, matching fcmpy:
    infer: W.T @ A + A, then sigmoid; clamp stable (input) concepts each step.
    """
    nodes = list(weight_matrix.columns)
    w = weight_matrix.values.astype(float)
    state = np.array([float(initial_state[n]) for n in nodes], dtype=float)
    clamped = _stable_concept_mask(weight_matrix)
    fixed_values = state[clamped].copy()

    rows = [state.copy()]

    for _ in range(iterations):
        inferred = w.T @ state + state
        next_state = _sigmoid(inferred, steepness)
        next_state[clamped] = fixed_values
        rows.append(next_state.copy())

        if np.max(np.abs(next_state - state)) <= thresh:
            break
        state = next_state

    return pd.DataFrame(rows, columns=nodes)


def simulate(
    initial_state: dict,
    thresh: float = 0.001,
    iterations: int = 50,
) -> pd.DataFrame:
    if _USE_FCMPY and _SIMULATOR is not None:
        return _SIMULATOR.simulate(
            initial_state=initial_state,
            weight_matrix=WEIGHT_MATRIX,
            transfer="sigmoid",
            inference="mKosko",
            thresh=thresh,
            iterations=iterations,
            l=1,
        )
    return _simulate_native(
        initial_state,
        WEIGHT_MATRIX,
        thresh=thresh,
        iterations=iterations,
    )


def run_fcm(
    bmi: float,
    fitness: int,
    muscle_gain: int,
    weight_loss: int,
) -> dict:
    bmi_fuzzy = bmi_to_fuzzy(bmi)
    user_input = {
        "BMI": bmi_fuzzy,
        "Fitness_Lvl": slider_to_fuzzy(fitness),
        "Goal_MuscleGain": slider_to_fuzzy(muscle_gain),
        "Goal_WeightLoss": slider_to_fuzzy(weight_loss),
        "Rec_Light_Cardio": 0.0,
        "Rec_Strength": 0.0,
        "Rec_HIIT": 0.0,
        "Rec_Beginner": 0.0,
    }

    result = simulate(user_input)
    final_values = result.iloc[-1]
    recommendations = final_values[OUTPUT_NODES].sort_values(ascending=False)

    return {
        "engine": "fcmpy" if _USE_FCMPY else "native",
        "bmi_value": round(float(bmi), 1),
        "inputs_fuzzy": {
            "BMI": bmi_fuzzy,
            "Fitness_Lvl": user_input["Fitness_Lvl"],
            "Goal_MuscleGain": user_input["Goal_MuscleGain"],
            "Goal_WeightLoss": user_input["Goal_WeightLoss"],
        },
        "iterations": len(result) - 1,
        "recommendations": [
            {"key": key, "score": float(recommendations[key])}
            for key in recommendations.index
        ],
    }
