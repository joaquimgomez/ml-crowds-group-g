import matplotlib.pyplot as plt
import numpy as np
import random
import pandas as pd
from sklearn.metrics.pairwise import euclidean_distances
from scipy.spatial import KDTree
from scipy.sparse.linalg import eigsh

class DiffusionMaps:
	def __init__(self):
		pass

	def distance_matrix(self, data):
		# TODO: Will change this guy to KDTree
		distances = euclidean_distances(data)
		return distances

	def diffusion_algorithm(self, data, L):
		# Implementation of the basic Diffusion Map algorithm

		# Pairwise distance matrix(Step 1)
		self.distances = self.distance_matrix(data)


		# 5% of the diameter of the dataset is set to epsilon(Step 2)
		self.epsilon = 0.05 * np.max(self.distances)

		# Kernel Matrix W (Step 3)
		self.W = np.exp(-1 * (self.distances ** 2) / self.epsilon)


		# Diagonal Normalization Matrix P. (Step 4)
		self.P = np.diag(np.sum(self.W, axis=1))

		# Normalize the kernel matrix W (Step 5)
		self.inv_P = np.linalg.inv(self.P)
		self.K = np.dot(self.inv_P, np.dot(self.W, self.inv_P))

		# Diagonal Normalization Matrix Q (Step 6)
		self.Q = np.diag(np.sum(self.K, axis=1))

		# Symmetric matrix T_hat (Step 7)
		self.inv_Qsqrt = np.sqrt(np.linalg.inv(self.Q))
		self.T_hat = np.dot(self.inv_Qsqrt, np.dot(self.K, self.inv_Qsqrt))

		# L + 1 largest eigenvalues and eigenvectors of T_hat (Step 8)
		eigvals, eigvecs = eigsh(self.T_hat, k=L+1)

		# Compute the eigenvals of T_hat^1/epsilon (Step 9)
		eigvals_T_hat_squared = eigvals ** (1 / self.epsilon)
		eigvals_T_hat = np.sqrt(eigvals_T_hat_squared)

		# Compute the eigenvectors of matrix T (Step 10)
		eigvecs_t = np.dot(self.inv_Qsqrt, eigvecs)

		return eigvals_T_hat, eigvecs_t

