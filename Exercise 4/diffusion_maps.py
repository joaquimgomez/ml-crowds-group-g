import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances
from scipy.sparse.linalg import eigsh

class DiffusionMaps:
	def __init__(self):
		pass

	def diffusion_algorithm(self, data, L):
		"""Performs the Diffusion Map algorithm for the given data.

		Args:
			data (array): NumPy array.
			L (integer): Mumber of eigenvalues.
			
		Returns:
			eigvals_T_hat (array): Array with the eigenvalues
			eigvecs_T (array): Array with the eigenvectors
		"""

		# Pairwise distance matrix
		self.distances = euclidean_distances(data)

		# 5% of the diameter of the dataset is set to epsilon
		self.epsilon = 0.05 * np.max(self.distances)

		# Kernel Matrix W
		self.W = np.exp(-1 * (self.distances ** 2) / self.epsilon)

		# Diagonal Normalization Matrix P.
		self.P = np.diag(np.sum(self.W, axis=1))

		# Normalize the kernel matrix W
		self.inv_P = np.linalg.inv(self.P)
		self.K = np.dot(self.inv_P, np.dot(self.W, self.inv_P))

		# Diagonal Normalization Matrix Q
		self.Q = np.diag(np.sum(self.K, axis=1))

		# Symmetric matrix T_hat
		self.inv_Qsqrt = np.sqrt(np.linalg.inv(self.Q))
		self.T_hat = np.dot(self.inv_Qsqrt, np.dot(self.K, self.inv_Qsqrt))

		# L + 1 largest eigenvalues and eigenvectors of T_hat
		eigvals, eigvecs = eigsh(self.T_hat, k=L+1)

		# Compute the eigenvals of T_hat^1/epsilon
		eigvals_T_hat_squared = eigvals ** (1 / self.epsilon)
		eigvals_T_hat = np.sqrt(eigvals_T_hat_squared)

		# Compute the eigenvectors of matrix T
		eigvecs_t = np.dot(self.inv_Qsqrt, eigvecs)

		return eigvals_T_hat, eigvecs_t

