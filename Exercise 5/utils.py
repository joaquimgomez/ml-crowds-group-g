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
    return np.exp(-(xl-x)**2 / (epsilon**2))

def approximateNonLinearFunction(data, L, epsilon):
    x, y = data[:, 0], data[:, 1]
    
    # 
    #randomPoints = np.random.permutation(data.shape[0])[:L]
    #centers = [x[i] for i in randomPoints]

    def getCenters():
        centers = []
        points =[]
        for i in range(L):
            points.append(np.min(x) + (i*(np.max(x)-np.min(x))/L)) #?
        
        for i in range(L):
            centers.append(np.ones(len(x))*points[i])
        
        return centers
    centers = getCenters()
    
    #
    rbfResults = []
    for l in range(L):
        rbfResults.append(radialBasisFunction(centers[l], x, epsilon))   
    rbfResults = np.array(rbfResults)
    
    #
    A = np.vstack([rbfResults, np.ones(rbfResults.shape)]).T
    C, residuals, rank, singularValues = np.linalg.lstsq(A, y, rcond=None)
    
    #
    f = np.zeros(len(x))
    for l in range(L):
        f += C[l] * radialBasisFunction(centers[l], x, epsilon)
    
    return f
