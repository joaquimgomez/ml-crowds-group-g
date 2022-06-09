import numpy as np
from scipy import linalg

class PCA:
    def __init__(self):
        pass

    def pca(self, data):
        self.data = data

        # Obtain mean by columns
        means = np.mean(data, axis=0)

        # Center the matrix by removing the data mean
        centered = data - means

        # SVD decomposition fo the matrix (values on the diagonal of S in decending order)
        # U: Coordiantes of the principal components of each data point with decreasing order
        # S: 
        # V: Orthonormal matrix (V^T V = I), used to project new centered data points X^
        #    onto their (properly scaled) principal components ÛS
        self.U, self.S, V = linalg.svd(centered) # full_matrices=False ?

    def getReconstructedData(self, nComponents = None):
        U = None
        if nComponents is None:
            U = self.U
        else:
            U = self.U[:, 0:nComponents]

        SMatrix = np.zeros((U.shape[1], self.V.shape[0]), self.S.dtype)
        np.fill_diagonal(SMatrix, self.S)
        
        return U @ (SMatrix @ self.V), self.getTotalEnergy(SMatrix)

    def getTotalEnergy(self, SMatrixNComponents): # TODO: Is this correct? Yes, it is
        sum = np.sum(np.square(np.diagonal(SMatrixNComponents)))
        traceSSquare = np.sum(np.square(self.S))
        return sum / traceSSquare
    
    def getEnergyPerComponent(self): # TODO: Is this correct? Yes, it is
        # Compute variance explained by principal components
        SSquared = np.square(self.S)
        return SSquared / SSquared.sum()

    def getComponents(self, n = None):
        if n is None:
            return self.V
        else:
            return self.V[:, 0:n]