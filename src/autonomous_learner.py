import json
import os
import numpy as np
from sklearn.linear_model import SGDRegressor

LEARNING_FILE = "data/learning_state.json"
FEEDBACK_LOG = "data/feedback_log.jsonl"

class AutonomousLearner:
    def __init__(self):
        self.weights = {"skills": 0.5, "experience": 0.25, "education": 0.15, "training": 0.1}
        self.load_state()

    def load_state(self):
        if os.path.exists(LEARNING_FILE):
            try:
                with open(LEARNING_FILE, 'r') as f:
                    self.weights = json.load(f)
            except:
                pass

    def save_state(self):
        os.makedirs("data", exist_ok=True)
        with open(LEARNING_FILE, 'w') as f:
            json.dump(self.weights, f)

    def log_feedback(self, job_desc, candidate_features, score, feedback_type):
        """
        feedback_type: 1 for Hire/Positive, 0 for Reject/Negative
        """
        log_entry = {
            "features": candidate_features, # {"skills": 0.8, "experience": 0.4, ...}
            "label": feedback_type
        }
        os.makedirs("data", exist_ok=True)
        with open(FEEDBACK_LOG, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")

    def train_on_feedback(self):
        """
        Trains a simple linear model to learn the importance of different features
        based on user hiring decisions.
        """
        if not os.path.exists(FEEDBACK_LOG):
            return self.weights

        X = []
        y = []
        
        with open(FEEDBACK_LOG, 'r') as f:
            for line in f:
                data = json.loads(line)
                # Ensure we use the keys in a consistent order
                feat_vec = [
                    data["features"].get("skills", 0),
                    data["features"].get("experience", 0),
                    data["features"].get("education", 0),
                    data["features"].get("training", 0)
                ]
                X.append(feat_vec)
                y.append(data["label"])

        if len(y) < 5: # Need at least some data to learn
            return self.weights

        X = np.array(X)
        y = np.array(y)

        # Use SGD to learn weights (Online learning style)
        model = SGDRegressor(max_iter=1000, tol=1e-3, penalty=None, eta0=0.01)
        model.fit(X, y)

        # Normalize coefficients to be our new weights (sum to 1)
        coeffs = np.abs(model.coef_)
        total = np.sum(coeffs)
        if total > 0:
            norm_coeffs = coeffs / total
            self.weights = {
                "skills": float(norm_coeffs[0]),
                "experience": float(norm_coeffs[1]),
                "education": float(norm_coeffs[2]),
                "training": float(norm_coeffs[3])
            }
            self.save_state()
        
        return self.weights

# Singleton instance
learner = AutonomousLearner()
