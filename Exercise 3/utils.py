import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


def solve_euler(f_ode, y0, time):
    """
    Solves the given ODE system in f_ode using forward Euler.
    :param f_ode: the right hand side of the ordinary differential equation d/dt x = f_ode(x(t)).
    :param y0: the initial condition to start the solution at.
    :param time: np.array of time values (equally spaced), where the solution must be obtained.
    :returns: (solution[time,values], time) tuple.
    """
    yt = np.zeros((len(time), len(y0)))
    yt[0, :] = y0
    step_size = time[1]-time[0]
    for k in range(1, len(time)):
        yt[k, :] = yt[k-1, :] + step_size * f_ode(yt[k-1, :])
    return yt, time


def plot_phase_portrait(A, X, Y):
    """
    Plots a linear vector field in a streamplot, defined with X and Y coordinates and the matrix A.
    """
    UV = A@np.row_stack([X.ravel(), Y.ravel()])
    U = UV[0,:].reshape(X.shape)
    V = UV[1,:].reshape(X.shape)

    fig = plt.figure(figsize=(15, 15))
    gs = gridspec.GridSpec(nrows=3, ncols=2, height_ratios=[1, 1, 2])

    #  Varying density along a streamline
    ax0 = fig.add_subplot(gs[0, 0])
    ax0.streamplot(X, Y, U, V, density=[0.5, 1])
    ax0.set_title('Streamplot for linear vector field A*x');
    ax0.set_aspect(1)
    return ax0

def plot_phase_portrait(X, Y, U, V, figsize=(15, 15)):
    """
    Plots a linear vector field in a streamplot, defined with X and Y coordinates and velocities U and V.
    """
    fig = plt.figure(figsize=figsize)
    gs = gridspec.GridSpec(nrows=3, ncols=2, height_ratios=[1, 1, 2])

    #  Varying density along a streamline
    ax0 = fig.add_subplot(gs[0, 0])
    ax0.streamplot(X, Y, U, V, density=[0.5, 1])
    ax0.set_title('Streamplot for linear vector field A*x');
    ax0.set_aspect(1)
    return ax0

def plot_bifurcation_diagram(interval, alphas, labels, axis):
    """
    Plots the bifurcation diagram for the interval, using the provided alphas, labels for the alphas
    and the definition of the axis.
    """
    fig = plt.figure(figsize=(10, 6))
    gs = gridspec.GridSpec(nrows=1, ncols=1)
    
    ax0 = fig.add_subplot(gs[0])
    colors = ['r', 'b', 'g', 'y', 'c', 'm', 'k']
    for index, alpha in enumerate(alphas):
        ax0.plot(interval, alpha, colors[index], label = labels[index], linewidth = 3)
        
    ax0.axis(axis)
    ax0.legend(loc='upper left')
    ax0.set_xlabel('α')
    ax0.set_ylabel('ẋ')
    ax0.set_title('Bifurcation Diagram')

