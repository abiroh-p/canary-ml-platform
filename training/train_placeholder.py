"""
Trains a minimal placeholder classifier and saves it for the model server
to load locally. Not the real training pipeline (see ADR-0003) — just
enough to exercise the serving path end-to-end.
"""

import logging

import joblib
from pathlib import Path
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OUTPUT_PATH = Path(__file__).parent.parent / "model-server" / "artifacts" / "model.joblib"

def main() -> None:
    X, y = make_classification(n_samples=500, n_features=5, random_state=42)
    model = LogisticRegression().fit(X, y)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, OUTPUT_PATH)
    logger.info("saved model to %s", OUTPUT_PATH)

if __name__ == "__main__":
    main()