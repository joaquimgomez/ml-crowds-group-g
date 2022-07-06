import numpy as np

def leastSquaresMinimization(data):
    """Given a dataset, it computes the Least Squares Minimization (LSM) of the data.

    Args:
        data (NumPy Array): Dataset to be approximated using LSM.

    Returns:
        a (int): Slope of the approximated function.
        b (int): Intercept of the approximated function.
    """
    x, y = data[:, 0], data[:, 1]
    
    # Obtain coefficient matrix
    A = np.vstack([x, np.ones(len(x))]).T
     
    # Compute Least Squares Minimization
    (a, b), residuals, rank, singularValues = np.linalg.lstsq(A, y, rcond=None)
    
    return a, b

def radialBasisFunction(xl, x, epsilon):
    """Computes the results of the radial basis function phi_l = exp(-||x_l - x||^2 / epsilon^2).

    Args:
        xl (array): Center of the function
        x (array): Input of the functon
        epsilon (float): bandwidth.

    Returns:
        array: Result of the RBF.
    """
    return np.exp(-(xl - x)**2 / (epsilon**2))

def approximateNonLinearFunction(data, L, epsilon):
    """Approximates the given data using L radial basis functions with a epsilon bandwidth.

    Args:
        data (array): Data to be approximated.
        L (int): Number of radial basis functions to accumulate.
        epsilon (float): Bandwidth of the RBF.

    Returns:
        array: Array with the resulting approximation.
    """
    # Unpack the data in x and y
    x, y = data[:, 0], data[:, 1]
    
    # Computation of L data centers for the radial basasis function
    #randomPoints = np.random.permutation(data.shape[0])[:L]
    #centers = [x[i] for i in randomPoints]
    def getCenters():
        centers = []
        for i in range(L):
            center = np.min(x) + i * ((np.max(x) - np.min(x)) / L)
            centers.append(np.ones(len(x)) * center)
        return centers
        
    centers = getCenters()
    
    # Computation of L radial basis functions
    rbfResults = []
    for l in range(L):
        rbfResults.append(radialBasisFunction(centers[l], x, epsilon))   
    rbfResults = np.array(rbfResults)
    
    # Computationf of L coefficients for the L radial basis functions
    A = np.vstack([rbfResults, np.ones(rbfResults.shape)]).T
    C, residuals, rank, singularValues = np.linalg.lstsq(A, y, rcond=None)
    
    # Accumulation of the radial basis functions times the coefficients
    f = np.zeros(len(x))
    for l in range(L):
        f += C[l] * radialBasisFunction(centers[l], x, epsilon)
    
    return f
