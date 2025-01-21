import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 


# use pandas to load real_estate_dataset.csv
df = pd.read_csv('real_estate_dataset.csv')

# get the number of samples and features
n_samples, n_features = df.shape
print(f"Number of samples, features: {n_samples, n_features}")

# get the names of the columns
columns = df.columns
print(f"Columns: {columns}")

# save the column names to a file for accessing later as text file
np.savetxt('columns.txt', columns, fmt='%s')

# use all features available in the dataset
x = df.drop(columns=['Price']).values

# use price as the target
y = df['Price'].values

print(f"shape of x: {x.shape}")
print(f"shape of y: {y.shape}")

# get the number of the samples and features in X
n_samples, n_features = x.shape

# Build a linear model to predict the price from the four features in X
# make an array of coefs of the size of n_features+1, initialized to 1
coefs = np.ones(n_features + 1)

# predict the price for each sample in X
predictions_bydefn = x @ coefs[1:] + coefs[0]

# append a column of ones to X
x = np.hstack((np.ones((n_samples, 1)), x))

# predict the price for each sample in X
predictions = x @ coefs

# see if all entries in predictions_bydefn and predictions are the same
is_same = np.allclose(predictions_bydefn, predictions)

print(f"are the predictions the same with x*coefs[1:] + coefs[0] and x@coefs: {is_same}\n")

# calculate the error using predictions and y
errors = y - predictions

# Calculate the relative errors
rel_errors = errors / (y + 1e-10)  # Avoid division by zero

# calculate the mean of the square of the errors using the loop
loss_loop = 0
for i in range(n_samples):
    loss_loop += errors[i]**2
loss_loop /= n_samples

# calculate the mean of the square of the errors using matrix operations
loss_matrix = (errors.T @ errors) / n_samples

# compare the two methods of calculating the mean of the square of the errors
is_diff = np.allclose(loss_loop, loss_matrix)
print(f"Are the loss by direct and matrix same? {is_diff}\n")

# print the size of errors and its L2 norm
print(f"Size of the errors: {errors.shape}")
print(f"L2 norm of the errors: {np.linalg.norm(errors)}")
print(f"L2 norm of the relative error: {np.linalg.norm(rel_errors)}")

# objective function: f(coefs) = 1/n_samples * \sum_{i=1}^{n_samples} (y_i - x_i^T coefs)^2

# What is the solution?
# A solution is a set of coefficients that minimize the objective function

# How to find the solution?
# By searching for the coefficients at which the gradient of the objective function is zero
# Or I can set the gradient of the objective function to zero and solve for the coefficients

# Write the loss matrix in terms of the data and coefs
loss = 1/n_samples * (y - (x @ coefs)).T @ (y - x @ coefs)

# We set the gradient of the loss with respect to the coefficients
grad_matrix = -2/n_samples * x.T @ (y - x @ coefs)
# We set the gradient = zero and solve for the coefficients
# x.T @ y = x.T @ x @ coefs
# x.T @ x @ coefs = x.T @ y. This equation is called the normal equation

coefs = np.linalg.inv(x.T @ x) @ x.T @ y
np.savetxt('Coeffs_INV.csv', coefs, delimiter=',')

# predict the price for each sample in X
predictions = x @ coefs

# calculate the error using the optimal coefficients
error_model = y - predictions

print(f"L2 norm of the errors_model: {np.linalg.norm(error_model)}")

# calculate the rank of the X.T @ X
rank_xTx = np.linalg.matrix_rank(x.T @ x)
print(f"Rank of X.T @ X: {rank_xTx}")

# solve the normal equation using matrix decomposition
# QR decomposition
Q, R = np.linalg.qr(x)

print(f"shape of Q: {Q.shape}")
print(f"shape of R: {R.shape}")

# write R to the file named R.csv
np.savetxt('R.csv', R, delimiter=',')

# R * coeffs = b
sol = Q.T @ Q
np.savetxt('sol.csv', sol, delimiter=',')

# x = QR
# x.T @ x = R.T @ Q.T @ Q @ R = R.T @ R
# R * coeffs = Q.T @ y

b = Q.T @ y
print(f"shape of b: {b.shape}")
print(f"shape of R: {R.shape}")

# loop to solve R * coeffs = b using back substitution
coeffs_qr_loop = np.zeros(n_features + 1)
for i in range(n_features, -1, -1):
    coeffs_qr_loop[i] = b[i]
    for j in range(i + 1, n_features + 1):
        coeffs_qr_loop[i] -= R[i, j] * coeffs_qr_loop[j]
    coeffs_qr_loop[i] /= R[i, i]

# save coeffs_qr_loop to a file named coeffs_qr_loop.csv
np.savetxt('Coeffs_QR_loop.csv', coeffs_qr_loop, delimiter=',')

# solve the normal equation using SVD
# x = U S Vt

# Eigen decomposition of a square matrix
# A = V D V^T
# A^-1 = V D^-1 V^T
# X * coeffs = y
# A = X^T @ X

# Normal equation: X^T @ X @ coeffs = X^T @ y
# X_dagger = (X^T @ X)^-1 @ X^T 
# fit only for the feature square feet
X_for_feet = x[:, 2].reshape(-1, 1)
X_for_feet = np.hstack((np.ones((n_samples, 1)), X_for_feet))
#print(f"shape of X_for_feet: {X_for_feet.shape}")


# Perform SVD
U, S, Vt = np.linalg.svd(X_for_feet, full_matrices=False)

# Find the pseudo-inverse of X using SVD
S_inv = np.diag(1/S)
X_dagger = Vt.T @ S_inv @ U.T
coeffs_svd = X_dagger @ y

# Alternatively, use numpy's pinv function
coeffs_pinv = np.linalg.pinv(X_for_feet) @ y

# Save coefficients to a file named coeffs.csv
np.savetxt('Coeffs_SVD.csv', coeffs_svd, delimiter=',')

# Plot the data on square feet and price using matplotlib
X_for_plot = np.arange(min(X_for_feet[:, 1]), max(X_for_feet[:, 1]), 0.01)
plt.scatter(X_for_feet[:, 1], y / 1e6)
plt.plot(X_for_plot, (X_for_plot * coeffs_pinv[1] + coeffs_pinv[0]) / 1e6, color='red')
plt.xlabel('Square Feet')
plt.ylabel('Price (in millions)')
plt.title('Price vs Square Feet')
plt.show()
