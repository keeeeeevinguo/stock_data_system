import numpy as np
from sklearn.linear_model import LinearRegression
import pickle

# Create dummy data
X = np.array([[i] for i in range(100)])  # Feature (e.g., days)
y = np.array([2 * i + 3 for i in range(100)])  # Target (e.g., stock price)

# Train a linear regression model
model = LinearRegression()
model.fit(X, y)

# Save the model
with open('pretrained_model.pkl', 'wb') as f:
    pickle.dump(model, f)
