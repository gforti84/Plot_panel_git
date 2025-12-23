# Classes definitions
# PlotLinesObj - single plot parameters.
# GenPlotParamObj - Overall ploting parameters.

from os import linesep
import numpy as np

class PlotLinesObj:
    
    def __init__(
        self,
        # Plot idx is the index of each curve. 
        idx = [0,0],
        # plot num is the total of subplots and curves for each subplot.
        #   also, for now, only allowed is subplots of same number of curves.
        plot_num = [1,1],
        title = 'Title',
        label = 'Label',
        x_label = 'xlabel',
        y_label = 'ylabel',
        x_lim = np.array([0,1]),
        y_lim = np.array([0,1]),
        styl_name = 'solid',
        styl = '-',
        clr = 'k',
        x_data = np.empty(0),
        y_data = np.empty(0)
    ):
        self.idx = idx
        self.plot_num = plot_num
        self.title = title
        self.label = label
        self.x_label = x_label
        self.y_label = y_label
        self.x_lim = x_lim
        self.y_lim = y_lim
        self.styl_name = styl_name
        self.styl = styl
        self.clr = clr
        self.x_data = x_data
        self.y_data = y_data

    def __str__(self):

        """Convert this object in a readeable string (for print)"""
        PlotLines_str = ''
        PlotLines_str += 'Plot idx = ' + str(self.idx[0]) + '/ Subplot idx = ' + str(self.idx[1]) + linesep
        PlotLines_str += 'Title = ' + self.title + linesep
        PlotLines_str += 'Label = ' + self.label + linesep
        PlotLines_str += 'X label = ' + self.x_label + linesep
        PlotLines_str += 'Y label = ' + self.y_label + linesep
        PlotLines_str += 'X lim max = ' + str(self.x_lim[1]) + linesep
        PlotLines_str += 'X lim min = ' + str(self.x_lim[0]) + linesep
        PlotLines_str += 'Y lim max = ' + str(self.y_lim[1]) + linesep
        PlotLines_str += 'Y lim min = ' + str(self.y_lim[0]) + linesep
        PlotLines_str += 'line stype = ' + self.styl_name + '( ' + self.styl + ' )' + linesep
        PlotLines_str += 'line color = ' + self.clr + linesep

        return PlotLines_str
    

class GenPlotParamObj:

    def __init__(
        self,
        fig_size = (20/2.54, 15/2.54),
        font_size = 16,
        ln_wdth = 1,
        legend_pos = 'upper left',
        legend_col = 1
    ):
        self.fig_size = fig_size
        self.ln_wdth = ln_wdth
        self.font_size = font_size
        self.legend_pos = legend_pos
        self.legend_col = legend_col


    def __str__(self):

        """Convert this object in a readeable string (for print)"""
        PlotLines_str = ''
        PlotLines_str += 'Fig size = ' + str(self.fig_size) + linesep
        PlotLines_str += 'Line width = ' + str(self.ln_wdth) + linesep
        PlotLines_str += 'Font size = ' + str(self.font_size) + linesep
        PlotLines_str += 'Legend position = ' + self.legend_pos + linesep
        PlotLines_str += 'Legend col number = ' + str(self.legend_col) + linesep

        return PlotLines_str