import numpy as np
from scipy import linalg

class PCA:
    def __init__(self):
        pass

    def pca(self, data):
        """Performs PCA on the provided data using the SVD.

        Args:
            data (array): NumPy array with the data.
        """
        self.data = data

        # Obtain mean by columns
        means = np.mean(data, axis=0)

        # Center the matrix by removing the data mean
        centered = data - means

        # SVD decomposition of the matrix (values on the diagonal of S in decending order)
        # U: Coordiantes of the principal components of each data point with decreasing order
        # S: Eigenvalues
        # V: Orthonormal matrix (V^T V = I), used to project new centered data points ^X
        #    onto their (properly scaled) principal components ÛS
        self.U, self.S, self.V = linalg.svd(centered)

    def getReconstructedData(self, nComponents = None):
        """It returns the recosntructed data with the given number of components.
        If no number is provided, it returns the reconstructed data with the same number of components as the original data.

        Args:
            nComponents (int, optional): Number of components to be used in the reconstruction. Defaults to None.

        Returns:
            array: NumPy array with the reconstructed data (U · S · V).
            float: Total energy of the components used for the reconstruction.
        """
        U = None
        if nComponents is None:
            U = self.U
        else:
            U = self.U[:, 0:nComponents]

        SMatrix = np.zeros((U.shape[1], self.V.shape[0]), self.S.dtype)
        np.fill_diagonal(SMatrix, self.S)
        
        return U @ (SMatrix @ self.V), self.getTotalEnergy(SMatrix)

    def getTotalEnergy(self, SMatrixNComponents):
        """Returns the total energy of the components used for the reconstruction using the given sigma matrix.

        Args:
            SMatrixNComponents (_type_): Matrix of the S vector returned by linalg.svd().

        Returns:
            float: Total energy of the components used for the reconstruction.
        """
        sum = np.sum(np.square(np.diagonal(SMatrixNComponents)))
        traceSSquare = np.sum(np.square(self.S))
        return sum / traceSSquare
    
    def getEnergyPerComponent(self):
        """Computes and returns the energy of each component.

        Returns:
            array: NumPy array with the eenrgy of each component.
        """
        SSquared = np.square(self.S)
        return SSquared / SSquared.sum()

    def getComponents(self, n = None):
        """Returns n components of the data, i.e., the n first values of the V matrix.
        """
        if n is None:
            return self.V
        else:
            return self.V[:, 0:n]