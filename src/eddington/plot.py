"""Utility functions for plotting."""
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np

from eddington import FitData


def plot_fitting(  # pylint: disable=C0103,R0913
    func,
    data: FitData,
    a: np.ndarray,
    title_name,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    grid: bool = False,
    step: Optional[float] = None,
    xmin: Optional[float] = None,
    xmax: Optional[float] = None,
):
    """
    Plot fitting plot.

    :param func: Fitting function.
    :param data: Fitting data
    :param a: The parameters result
    :param title_name: str or None. Title for the figure.
    :param xlabel: str or None. Label of the x axis
    :param ylabel: str or None. Label of the x axis
    :param grid: bool. Add grid lines or not
    :param xmin: Optional. minimum value for x in plot
    :param xmax: Optional. maximum value for x in plot
    :param step: float or None. step between values of the continuous plot
    """
    fig = plot_data(
        data=data, title_name=title_name, xlabel=xlabel, ylabel=ylabel, grid=grid
    )
    xmin, xmax = get_plot_borders(x=data.x, xmin=xmin, xmax=xmax)
    if step is None:
        step = (xmax - xmin) / 1000.0
    x = np.arange(xmin, xmax, step=step)  # pylint: disable=invalid-name
    y = func(a, x)  # pylint: disable=invalid-name
    plot(fig=fig, x=x, y=y)
    return fig


def plot_data(
    data: FitData,
    title_name,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    grid: bool = False,
):
    """
    Plot fitting data.

    :param data: Fitting data
    :param title_name: str or None. Title for the figure.
    :param xlabel: str or None. Label of the x axis
    :param ylabel: str or None. Label of the x axis
    :param grid: bool. Add grid lines or not
    :returns: Data figure
    """
    fig = get_figure(title_name=title_name, xlabel=xlabel, ylabel=ylabel, grid=grid)
    errorbar(fig=fig, x=data.x, y=data.y, xerr=data.xerr, yerr=data.yerr)
    return fig


def get_figure(
    title_name,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    grid: bool = False,
):
    """
    Gets a figure from matplotlib.

    :param title_name: str or None. Title for the figure.
    :param xlabel: str or None. Label of the x axis
    :param ylabel: str or None. Label of the x axis
    :param grid: bool. Add grid lines or not
    :return: Figure instance
    """
    fig = plt.figure()
    title(fig=fig, title_name=title_name)
    label_axes(fig=fig, xlabel=xlabel, ylabel=ylabel)
    add_grid(fig=fig, is_grid=grid)
    return fig


def title(fig, title_name):
    """
    Add/remove title to figure.

    :param title_name: str or None. If None, don't add title. otherwise, add given title
    :param fig: Plot figure.
    """
    if title_name is not None:
        plt.title(title_name, figure=fig)


def label_axes(fig, xlabel, ylabel):
    """
    Add/remove labels to figure.

    :param fig: Plot figure.
    :param xlabel: str or None. If None, don't add label. otherwise, add given label
    :param ylabel: str or None. If None, don't add label. otherwise, add given label
    """
    if xlabel is not None:
        plt.xlabel(xlabel, figure=fig)
    if ylabel is not None:
        plt.ylabel(ylabel, figure=fig)


def add_grid(fig, is_grid):
    """
    Add/remove grid to figure.

    :param fig: Plot figure
    :param is_grid: Boolean. add or remote grid to plot
    """
    if is_grid:
        plt.grid(True, figure=fig)


def plot(x, y, fig):  # pylint: disable=C0103
    """
    Plot y as a function of x.

    :param x: X values
    :param y: Y values
    :param fig: Plot figure
    """
    plt.plot(x, y, figure=fig)


def horizontal_line(  # pylint: disable=C0103
    fig: plt.Figure, xmin: float, xmax: float, y=0
):
    """
    Add horizontal line to figure.

    :param xmin: Minimum x value of line
    :param xmax: Maximum x value of line
    :param y: The y value of the line
    """
    plt.hlines(y, xmin=xmin, xmax=xmax, linestyles="dashed", figure=fig)


def errorbar(fig, x, y, xerr, yerr):  # pylint: disable=C0103
    """
    Plot error bar to figure.

    :param x: X values
    :param y: Y values
    :param xerr: Errors of x
    :param yerr: Errors of y
    :param fig: Plot figure
    """
    plt.errorbar(
        x=x,
        y=y,
        xerr=xerr,
        yerr=yerr,
        markersize=1,
        marker="o",
        linestyle="None",
        figure=fig,
    )


def get_plot_borders(
    x: np.ndarray, xmin: Optional[float] = None, xmax: Optional[float] = None
):  # pylint: disable=C0103
    """
    Get borders for a plot based on its x values.

    :param x: Array. x values of the fitting
    :return: tuple. minimum and maximum values for the plot.
    """
    data_xmin = np.min(x)
    data_xmax = np.max(x)
    gap = (data_xmax - data_xmin) * 0.1
    if xmin is None:
        xmin = data_xmin - gap
    if xmax is None:
        xmax = data_xmax + gap
    return xmin, xmax


def show_or_export(fig: plt.Figure, output_path=None):
    """
    Show plot or export it to a file.

    :param fig: a plot figure
    :param output_path: Path or None. if None, show plot. otherwise, save to path.
    """
    if output_path is None:
        plt.show()
        return
    fig.savefig(output_path)
