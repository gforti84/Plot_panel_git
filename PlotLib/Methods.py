import unittest as ut
import re
import os

import numpy as np
import matplotlib.pyplot as plt


#  -- Defined classes
from .Classes import PlotLinesObj, GenPlotParamObj

#  -- for certifyGspread
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# -- for Panel 
import panel as pn
# import matplotlib
# matplotlib.use('Agg')


# ==============================================
# ========= Miscellaneous functions ============
# ==============================================

def round_two(num):
    # ===================================
    # retrieve the round number in the second most significant place
    # ex.: 
    #     1576 -> 1600
    #     13.5 -> 14
    #     0.014789 -> 0.015
        
    if num >= 1:
        # Returns the first portion splited string using the '.' as cutting tool
        str_num = str(num).split('.')[0] 

        # Size of the number
        str_len  = int(len(str_num))
        
        # multiply by 10^(2 - length) so the third most significan place is decimal.
        #  ceil will decimate it to the next "integer". Devide by the same 10^(2 - len)
        #  to retrieve the desired number.
        return np.ceil(num*10**(2 - str_len))/10**(2 - str_len), 10**(str_len - 3)

    else:
        # Returns the second portion splited string using the '.' as cutting tool
        str_num = str(num).split('.')[1]

        # [] - used to indicate a set of characters
        # If first character is ^, all char that are NOT in the set will be matched.
        # Returns the FIRST occurency of NOT '0'. the .span()[0] is to get the index of it
        idx_first = re.search('[^0]', str_num).span()[0]

        return np.ceil(num*10**(idx_first + 2))/10**(idx_first + 2), 10**(-idx_first - 3)
    
def next_hex(hex_string):
    # Convert the hex string to the closest next color in order to prevent
    # my current search algorithm no to confuse with to equal colors.

    hex_string = hex_string.replace('#', '')

    rgb_1 = int(hex_string[0:2], 16)
    rgb_2 = int(hex_string[2:4], 16)
    rgb_3 = int(hex_string[4:6], 16)

    rgb_list = [rgb_1, rgb_2, rgb_3]

    strong_clr = max(rgb_list)

    # >> the .index() method only returns the first index, if
    # >>     all occorrencies are needed, use array.where()
    # ii = np.where(np.array([rgb_1, rgb_2, rgb_3]) == m_rgb)[0]
    strong_idx = rgb_list.index(strong_clr)

    rgb_list[strong_idx] = rgb_list[strong_idx] - 1 if rgb_list[strong_idx] > 0 else rgb_list[strong_idx] + 1

    out_hex = '#'

    for i_rgb in rgb_list:
        # if hex() does not return a two character str, add '0' to the str
        out_hex += hex(i_rgb)[2:] if len(hex(i_rgb)[2:]) == 2 else '0' + hex(i_rgb)[2:]

    return out_hex
            
  

def get_line_style(idx_ls, idx_c):

    # styl_list=['-','--','-.',':'] # list of basic linestyles: solid, dashed, dashdot and dotted
    styl_list = [
        ('solid', '-'),

        ('loosely dotted',        (0, (1, 10))),
        ('dotted',                (0, (1, 1))),
        ('long dash with offset', (5, (10, 3))),
        ('loosely dashed',        (0, (5, 10))),
        ('dashed',                (0, (5, 5))),
        ('densely dashed',        (0, (5, 1))),

        ('loosely dashdotted',    (0, (3, 10, 1, 10))),
        ('dashdotted',            (0, (3, 5, 1, 5))),
        ('densely dashdotted',    (0, (3, 1, 1, 1))),

        ('dashdotdotted',         (0, (3, 5, 1, 5, 1, 5))),
        ('loosely dashdotdotted', (0, (3, 10, 1, 10, 1, 10))),
        ('densely dashdotdotted', (0, (3, 1, 1, 1, 1, 1)))]
    
    clrs_list=['#000000','#0000ff','#ff0000','#33cc33', '#cccc00', '#cc9900', '#009999'] # list of basic colors: black, blue, red, green, cyan and magenta

    return styl_list[idx_ls][1], clrs_list[idx_c]

def get_line_style_list():

    # styl_list=['-','--','-.',':'] # list of basic linestyles: solid, dashed, dashdot and dotted
    styl_list = ['solid',
        
        'loosely dotted',
        'dotted',
        'long dash with offset',
        'loosely dashed',
        'dashed',
        'densely dashed',

        'loosely dashdotted',
        'dashdotted',
        'densely dashdotted',

        'dashdotdotted',
        'loosely dashdotdotted',
        'densely dashdotdotted']
    
    clrs_list=['#000000','#0000ff','#ff0000','#33cc33', '#cccc00', '#cc9900', '#009999'] # list of basic colors: black, blue, red, green, cyan and magenta

    return styl_list, clrs_list

# ==============================================
# ===== Google sheet manipulation funcions =====
# ==============================================

def certifyGspread(keyfile_dict, sh_name):

    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    home_path = os.path.expanduser('~')
        
    load_path = os.path.join(os.path.sep, home_path, 'Documents', 'gsheet_cred.json')


    # creds = ServiceAccountCredentials.from_json_keyfile_name('/home/forti/HD-DATA/OneDrive/Aperam/Simulacao/PlotSolution/PlotLib/gsheet_creds.json', scopes=scopes)
    # creds = ServiceAccountCredentials.from_json_keyfile_name('./PlotLib/gsheet_cred_gam.json', scopes=scopes)
    # creds = ServiceAccountCredentials.from_json_keyfile_name(load_path, scopes=scopes)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(keyfile_dict, scopes=scopes)

    file = gspread.authorize(creds)
    workbook = file.open(sh_name)

    return workbook


def get_ws_tags(current_ws):
    # ===================================
    # retrieve the current worksheet tags:
    #   - title_list: subplot titles
    #   - curves_list_rs: subplot curves names (for legend)
    #   - axis_list_rs: axis names.

    # The first ROW is for definition of different titles. For example, same measurement ranges with different experiment conditions.
    #   For later definition: plot in the same windows or using diferrent subplots?
    title_list = current_ws.row_values(1)
    title_list = list(filter(None, title_list))

    #   # Find the rows of different titles for comparison of the desired ploting ranges
    #   Cell_title = [current_ws.find(title_list[idx_title]) for idx_title in range(len(title_list))]

    # The second ROW is for defining the curves names for the same plot.
    # For definition in the same sheet, it is expected that these a equal.
    curves_list = current_ws.row_values(2)
    curves_list = list(filter(None, curves_list))

    # =============
    # Loop for reshaping the curves_list for different experiments. Each row is a different experiment
    # Each column is the corresponding curve in the given order.

    if len(title_list) > 1:

        curves_list_rs = [] # Starting a new list for reshaping

        for idx_l in range(len(title_list)):
            temp = []
            for idx_c in range(int((len(curves_list))/2)):
                run_idx = idx_c + idx_l*int((len(curves_list))/2)
                # print(run_idx)
                # curves_list_rs[idx_l, idx_c] = curves_list[(idx_l+1)*idx_c]
                temp.append(curves_list[run_idx])

            curves_list_rs.append(temp)

        # Test if the curves are equally defined. Same elements, order is not important
        try:
            ut.TestCase().assertCountEqual(curves_list_rs[0][:], curves_list_rs[1][:])
        except AssertionError as msg:
            print(msg)

    else:

        curves_list_rs = [curves_list]

    # =============

    # The third ROW is for definition of curves names for the same plot

    # If you sure of what you are doing, define the axis only for the first set of values

    axis_list = current_ws.row_values(3)
    axis_list = list(filter(None, axis_list))

    if len(axis_list) >= 2:

        axis_list_rs = []

        for idx_l in range(int(len(axis_list)/2)):
            temp = []
            for idx_c in range(2):
                # print(idx_l, idx_c)
                run_idx = idx_c + idx_l*2
                # print(run_idx)
                temp.append(axis_list[run_idx])

            axis_list_rs.append(temp)

        # print(axis_list_rs)

        # Test if the axis are equally defined. Equal elements for all defined curves
        try:
            for idx_test in range(1, int(len(axis_list)/2)):
                ut.TestCase().assertListEqual(axis_list_rs[idx_test - 1][:], axis_list_rs[idx_test][:], msg='Failed at test idx = ' + str(idx_test))
        except AssertionError as msg:
            print(msg)

    return title_list, curves_list_rs, axis_list_rs


def get_plot_params(current_ws, idx_ws):

    # global Plotlist

    Plotlist = []

    # For now, the curve_list for the same spreadsheet should be equal.
    # So, in the same spreadsheet, different subplots should compare
    # same curves, different conditions.
    title_list, curves_list_rs, axis_list_rs = get_ws_tags(current_ws)

    ws_plot_num = len(title_list)

    # Definition of number of curves per subplot considering the different defined titles
    ws_curve_num = len(curves_list_rs[0])
    # -- len(curves_list_rs) -> # of rows
    # -- len(curves_list_rs[0]) -> # of columns

    max_Xval = 0
    max_Yval = 0

    for idx_subplot in range(ws_plot_num):
        
        for idx_curve in range(ws_curve_num):

            plotVar = PlotLinesObj()
           
            # plot num is the total of subplots and curves for each subplot.
            #   also, for now, only allowed is subplots of same number of curves.
            plotVar.plot_num = [ws_plot_num, ws_curve_num]

            plotVar.styl, plotVar.clr = get_line_style(idx_subplot, idx_curve)

            x_list = current_ws.col_values(int(2*idx_curve + 1 + idx_subplot*2*ws_curve_num))
            y_list = current_ws.col_values(int(2*idx_curve + 2 + idx_subplot*2*ws_curve_num))

            x_real = np.float64(x_list[3:])
            y_real = np.float64(y_list[3:])

            # Plot idx is the index of each curve. 
            plotVar.idx = [idx_ws, idx_subplot]

            plotVar.label = curves_list_rs[idx_subplot][idx_curve]
            plotVar.title = title_list[idx_subplot]
            plotVar.x_label = axis_list_rs[0][0]
            plotVar.y_label = axis_list_rs[0][1]

            max_Xval = max(x_real) if max(x_real) > max_Xval else max_Xval
            max_Yval = max(y_real) if max(y_real) > max_Yval else max_Yval

            x_lim_max, _ = round_two(max_Xval)
            y_lim_max, _ = round_two(1.1*max_Yval)
            
            # plotVar.x_lim = np.array([0, x_lim_max])
            # plotVar.y_lim = np.array([0, y_lim_max])

            plotVar.x_data = x_real
            plotVar.y_data = y_real

            Plotlist.append(plotVar)

            del plotVar
        
        for plot_run in Plotlist:
            plot_run.x_lim = np.array([0, x_lim_max])
            plot_run.y_lim = np.array([0, y_lim_max])

    return Plotlist

def get_fig_data(fig_list):

    plotParam = GenPlotParamObj()

    # The figure and axis dict are created empty 
    fig = {}
    axs = {}

    # The function is defined for each worksheet. For 
    #   now, only option is to create subplots for a worksheet
    #   with more plot titles.
    fig = plt.figure(figsize = plotParam.fig_size)

    # plot num is the total of subplots and curves for each subplot.
    #   also, for now, only allowed is subplots of same number of curves.
    [ws_plot_num, ws_curve_num] = fig_list[0].plot_num

    
    # Go through the figure list. The parameters are defined for each 
    #   worksheet.
    for idx_fig, curr_fig in enumerate(fig_list):

        fig_idx = curr_fig.idx[0]
        ax_idx = curr_fig.idx[1]

        # Evaluating the modulo operation of curve index over total of curves
        #   we can set some figure properties at the first iteration of each
        #   subplot
        if idx_fig % ws_curve_num == 0:

            x_lim_max = 0
            x_lim_min = 0

            y_lim_max = 0
            y_lim_min = 0

            axs[ax_idx] = fig.add_subplot(1, ws_plot_num, ax_idx + 1)
            axs[ax_idx].set_title(curr_fig.title, fontsize = plotParam.font_size)
            axs[ax_idx].set_xlabel(curr_fig.x_label, fontsize = plotParam.font_size)
            axs[ax_idx].set_ylabel(curr_fig.y_label, fontsize = plotParam.font_size)
            axs[ax_idx].grid(color=(0.8, 0.8, 0.8), linestyle='--', linewidth=.8)
            axs[ax_idx].tick_params(axis='both', which='major', labelsize=plotParam.font_size)

        # Setting x range
        x_lim_max = x_lim_max if x_lim_max >= curr_fig.x_lim[1] else curr_fig.x_lim[1]
        x_lim_min = x_lim_min if x_lim_min <= curr_fig.x_lim[0] else curr_fig.x_lim[0]

        y_lim_max = y_lim_max if y_lim_max >= curr_fig.y_lim[1] else curr_fig.y_lim[1]
        y_lim_min = y_lim_min if y_lim_min <= curr_fig.y_lim[0] else curr_fig.y_lim[0]

        axs[ax_idx].plot(
            curr_fig.x_data,
            curr_fig.y_data,
            label = curr_fig.label, 
            c = curr_fig.clr, 
            ls = curr_fig.styl, 
            lw = plotParam.ln_wdth
                         )
        # Evaluating the modulo operation of curve index + 1 over total of curves
        #   we can set some figure properties at the last iteration of each
        #   subplot
        if (idx_fig + 1) % ws_curve_num == 0:
            axs[ax_idx].legend(
                fontsize=plotParam.font_size,
                ncol = plotParam.legend_col,
                loc = plotParam.legend_pos,
                fancybox=True,
                shadow=True
                )
            
            axs[ax_idx].set_xlim(x_lim_min, x_lim_max)
            axs[ax_idx].set_ylim(y_lim_min, y_lim_max)
    
    plt.close()

    return fig, plotParam 
  