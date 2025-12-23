import numpy as np
import matplotlib.colors

# -- for Panel 
import panel as pn
import matplotlib
matplotlib.use('Agg')

#  -- Defined classes
from .Classes import PlotLinesObj, GenPlotParamObj

#  -- For saving
import getpass
import os

from .Methods import (
    get_plot_params, get_fig_data,
    round_two, get_line_style_list,
    get_line_style, certifyGspread, 
    next_hex
)


# ==============================================
# =========== Panel display funcions ===========
# ==============================================


def run_panel(workbook, keyfile_dict):

    cm_p_inch = 1/2.54

    list_ws = workbook.worksheets()
    sheet_list = [list_ws[idx].title for idx in range(len(list_ws))]
    
    select = pn.widgets.Select(name = 'Select plot tab', options=sheet_list, width = 170)

    select_fileformat = pn.widgets.Select(name = 'Select output file format', options = ['pdf', 'png'], width = 170)

    idx_ws = sheet_list.index(select.value)
    current_ws = workbook.worksheet(sheet_list[idx_ws])
    plot_list = get_plot_params(current_ws, idx_ws)

    fig, plotParam = get_fig_data(plot_list)

    # Overall legend control

    lgd_opt = ['upper left', 'upper center', 'upper right', 'lower left', 'lower center', 'lower right']

    lgd_col = pn.widgets.IntInput(name = 'Col#', start = 1, end = len(plot_list), value = 1, width = 50)
    lgd_loc = pn.widgets.Select(name = 'Legend location', options = lgd_opt, width = 140)
    
    exp_txt = pn.pane.Str('Exp X')
    enbl_exp = pn.widgets.Switch(name = 'Expand X')

    lgd_ctrl = pn.Row(lgd_col, pn.Column(exp_txt, enbl_exp), lgd_loc)

    # Fine legend control

    swt_txt = pn.pane.Str('Lgd xy')
    enbl_bbox = pn.widgets.Switch(name = 'Fine Lgd Ctrl')
    lgd_bbx_x = pn.widgets.FloatInput(name = 'bbox X', value = 0, step = 0.05, start = -2, end = 2, width = 70, disabled = True)
    lgd_bbx_y = pn.widgets.FloatInput(name = 'bbox Y', value = 0, step = 0.05, start = -2, end = 2, width = 70, disabled = True)
    lgd_fn_txt = pn.widgets.FloatInput(name = 'Lgd Font', value = 12, step = 0.5, start = 0, end = 26, width = 70, disabled = True)
    # lgd_bbx_dely = pn.widgets.FloatInput(name = 'del Y', value = 1, step = 0.05, start = 0, end = 2, width = 70, disabled = True)
    # lgd_fn_col = pn.widgets.IntInput(name = 'Col#', value = 1, step = 1, start = 1, end = len(plot_list), width = 50, disabled = True)

    lgd_fine = pn.GridSpec()
    lgd_fine[:, 0] = pn.Column(swt_txt, enbl_bbox, align = 'center')
    lgd_fine[0, 1] = lgd_bbx_x
    lgd_fine[0, 2] = lgd_bbx_y
    lgd_fine[1, 1] = lgd_fn_txt
    # lgd_fine[1, 2] = lgd_bbx_dely


    # ldg_fine = pn.Row(pn.Column(swt_txt, enbl_bbox), lgd_bbx_x, lgd_bbx_y)

    wdth_slide = pn.widgets.EditableIntSlider(name = 'Width', start = 0, end = 30, step = 1, value = 20, width = 200)
    hght_slide = pn.widgets.EditableIntSlider(name = 'Height', start = 0, end = 20, step = 1, value = 15, width = 200)

    font_size_slide = pn.widgets.EditableIntSlider(name = 'Font size', start = 0, end = 24, step = 1, value = 16, width = 200)
    ln_thck_slide = pn.widgets.EditableFloatSlider(name = 'Curve line width', start = 0, end = 4, step = 0.2, value = 1, width = 200)

    txt_lw = pn.Row(font_size_slide, ln_thck_slide)
    fig_size = pn.Row(wdth_slide, hght_slide)

    title_switch = pn.widgets.Checkbox(name = 'No title', align = 'center')

    button_update = pn.widgets.Button(name='Update data', button_type='primary')

    text_title = pn.widgets.TextInput(name='Title input', placeholder=plot_list[idx_ws].title, width = 200)

    title_grid = pn.GridBox(*[text_title, title_switch], ncols = 2, width=320)

    text_xlabel = pn.widgets.TextInput(name='X label input', placeholder=plot_list[idx_ws].x_label)  
    text_ylabel = pn.widgets.TextInput(name='Y label input', placeholder=plot_list[idx_ws].y_label)

    end_x, step_x = round_two(plot_list[idx_ws].x_lim[1])
    start_x = 0 #round_two(plot_list[idx_ws].x_lim[0])
    
    end_y, step_y = round_two(plot_list[idx_ws].y_lim[1])
    start_y = 0 #round_two(plot_list[idx_ws].x_lim[0])


    color_dic = {}
    style_dic = {}
    plot_clrs = []
    plot_stls = []

    for idx_clr in range(len(plot_list)):
        color_dic["colorpick_{0}".format(idx_clr)] = pn.widgets.ColorPicker(name=plot_list[idx_clr].label, 
                                                        value=plot_list[idx_clr].clr)

        stl_name = 'Line style' if idx_clr == 0 else ' '

        style_dic["linestlpick_{0}".format(idx_clr)] = pn.widgets.Select(name=' ',
                                                        value = idx_clr, #plot_list[idx_clr].styl_name, 
                                                        # options = get_line_style_list()[0],
                                                        options = dict(zip(get_line_style_list()[0], range(idx_clr, len(get_line_style_list()[0]) + idx_clr))),
                                                        width = 170, align=('end', 'center'))

        plot_clrs.append(plot_list[idx_clr].clr)
        plot_stls.append(plot_list[idx_clr].styl_name)

    grid_list = [None]*(len(list(color_dic.values())) + len(list(style_dic.values())))
    grid_list[::2] = list(color_dic.values())
    grid_list[1::2] = list(style_dic.values())

    color_curves = pn.Column(*list(color_dic.values()))
    style_curves = pn.Column(*list(style_dic.values()))
        
    clr_ls_grid = pn.GridBox(*grid_list, ncols = 2, width=280)

    xlim_sci = pn.widgets.Checkbox(name = '×10³', align = 'center')

    xlim_range = pn.widgets.EditableRangeSlider(
        name = 'X lim',
        start = start_x - 30*step_x,
        end = end_x + 30*step_x,
        value = (plot_list[idx_ws].x_lim[0], plot_list[idx_ws].x_lim[1]),
        step = step_x, 
        width = 230
    )

    xlim_grid = pn.GridBox(*[xlim_range, xlim_sci], ncols = 2, width=320)

    
    ylim_sci = pn.widgets.Checkbox(name = '×10³', align = 'center')

    ylim_range = pn.widgets.EditableRangeSlider(
        name = 'Y lim',
        start = start_y - 30*step_y,
        end = end_y + 30*step_y,
        value = (plot_list[idx_ws].y_lim[0], plot_list[idx_ws].y_lim[1]),
        step = step_y, 
        width = 230
    ) 

    ylim_grid = pn.GridBox(*[ylim_range, ylim_sci], ncols = 2, width=320)

    def update_select(event):

        fig = mpl_pane.object

        idx_ws = sheet_list.index(event.new)
        current_ws = workbook.worksheet(sheet_list[idx_ws])
        plot_list = get_plot_params(current_ws, idx_ws)

        fig, plotParam = get_fig_data(plot_list)
        end_x, step_x = round_two(plot_list[-1].x_lim[1])
        start_x = 0 #round_two(plot_list[idx_ws].x_lim[0])
        
        end_y, step_y = round_two(plot_list[-1].y_lim[1])
        start_y = 0 #round_two(plot_list[idx_ws].x_lim[0])

        ax = fig.axes

        text_title.value = ''
        text_xlabel.value = ''
        text_ylabel.value = ''

        text_title.placeholder = plot_list[-1].title
        text_xlabel.placeholder = plot_list[-1].x_label
        text_ylabel.placeholder = plot_list[-1].y_label

        xlim_range.start = start_x - 50*step_x
        xlim_range.end = end_x + 50*step_x
        xlim_range.value = (plot_list[-1].x_lim[0], plot_list[-1].x_lim[1])
        xlim_range.step = step_x
        
        ylim_range.start = start_y - 50*step_y
        ylim_range.end = end_y + 50*step_y
        ylim_range.value = (plot_list[-1].y_lim[0], plot_list[-1].y_lim[1])
        ylim_range.step = step_y
        
        wdth_slide.value = 20
        hght_slide.value = 15
        font_size_slide.value = 16
        ln_thck_slide.value = 1

        lgd_col.disabled = False
        lgd_loc.disabled = False
        lgd_col.value = 1
        lgd_col.end = len(plot_list)
        lgd_loc.value = 'upper left'
        title_switch.value = False
        enbl_exp.value = False
        xlim_sci.value = False
        ylim_sci.value = False

        enbl_bbox.value = False        
        lgd_bbx_x.disabled = True
        lgd_bbx_y.disabled = True
        # lgd_fn_col.end = len(plot_list)
        lgd_bbx_x.value = 0
        lgd_bbx_y.value = 0
        # lgd_fn_col.value = 1
        

        ax[0].set_xlim(0, end_x)
        ax[0].set_ylim(0, end_y)

        mpl_pane.object = fig    
        
        # Remove current watchers for recreation later
        # Without this, watchers are duplicated every new tab.
        for idx, colors in enumerate(color_curves.objects):
            colors.param.unwatch(cl_wtchrs[idx])

        for idx, style in enumerate(style_curves.objects):
            style.param.unwatch(ln_wtchrs[idx])        
        
        # Remove objects from list in case of figure with fewer curves
        if len(plot_list) < len(plot_clrs):

            for idx_add in range(len(plot_list), len(plot_clrs)):

                color_dic.pop("colorpick_{0}".format(idx_add))
                style_dic.pop("linestlpick_{0}".format(idx_add)) 

                plot_clrs.pop()
                plot_stls.pop()

                cl_wtchrs.pop()
                ln_wtchrs.pop()
        
        
        for idx, clr_key in enumerate(color_dic):
            color_dic[clr_key].value = plot_list[idx].clr
            plot_clrs[idx] = plot_list[idx].clr


        for idx, stl_key in enumerate(style_dic):
            style_dic[stl_key].value = idx # plot_list[idx].styl_name
            plot_stls.append(plot_list[idx].styl_name)

        if len(plot_list) > len(plot_clrs):

            for idx_add in range(len(plot_clrs), len(plot_list)):


                color_dic["colorpick_{0}".format(idx_add)] = pn.widgets.ColorPicker(name=plot_list[idx_add].label, 
                                                value=plot_list[idx_add].clr)

                style_dic["linestlpick_{0}".format(idx_add)] = pn.widgets.Select(name='ln_{0}'.format(idx_clr),
                                                value = idx_add, 
                                                options = dict(zip(get_line_style_list()[0], range(idx_add, len(get_line_style_list()[0]) + idx_add))),
                                                width = 170, align=('end', 'center'))

                plot_clrs.append(plot_list[idx_add].clr)
                plot_stls.append(plot_list[idx_add].styl_name)

                cl_wtchrs.append(0)
                ln_wtchrs.append(0)

        

        grid_list = [None]*(len(list(color_dic.values())) + len(list(style_dic.values())))
        grid_list[::2] = list(color_dic.values())
        grid_list[1::2] = list(style_dic.values())

        clr_ls_grid.objects = grid_list
                
        color_curves.objects = list(color_dic.values())
        style_curves.objects = list(style_dic.values())        
        
        # cl_wtchrs = []
        for idx, colors in enumerate(color_curves.objects):
            temp = colors.param.watch(update_color, 'value')
            cl_wtchrs[idx] = temp

        for idx, style in enumerate(style_curves.objects):
            temp = style.param.watch(update_style, 'value')
            ln_wtchrs[idx] = temp


    select.param.watch(update_select, 'value')
        
    mpl_pane = pn.pane.Matplotlib(fig, dpi=50, tight = True)


    def update_title(event):

        fig = mpl_pane.object

        ax = fig.axes

        ax[0].set_title(str(event.new), fontsize = font_size_slide.value)
        mpl_pane.object = fig

    def update_xLabel(event):

        fig = mpl_pane.object
        
        ax = fig.axes
        ax[0].set_xlabel(str(event.new), fontsize = font_size_slide.value)
        mpl_pane.object = fig

    def update_yLabel(event):

        fig = mpl_pane.object
        
        ax = fig.axes
        ax[0].set_ylabel(str(event.new), fontsize = font_size_slide.value)
        mpl_pane.object = fig

    def update_xlim(event):

        fig = mpl_pane.object
        
        ax = fig.axes
        ax[0].set_xlim(event.new[0], event.new[1])
        mpl_pane.object = fig

    def update_xSci(event):

        fig = mpl_pane.object
        
        ax = fig.axes

        if event.new == True:
            ax[0].ticklabel_format(style='scientific', axis='x', scilimits=(0, 0), useMathText= True)
            ax[0].xaxis.offsetText.set_fontsize(font_size_slide.value - 5)

        if event.new == False:
            ax[0].ticklabel_format(style='plain', axis='x')

        mpl_pane.object = fig


    def update_ylim(event):

        fig = mpl_pane.object
        
        ax = fig.axes
        ax[0].set_ylim(event.new[0], event.new[1])
        mpl_pane.object = fig

    def update_ySci(event):

        fig = mpl_pane.object
        
        ax = fig.axes

        if event.new == True:
            ax[0].ticklabel_format(style='scientific', axis='y', scilimits=(0, 0), useMathText= True)
            ax[0].yaxis.offsetText.set_fontsize(font_size_slide.value - 5)

        if event.new == False:
            ax[0].ticklabel_format(style='plain', axis='y')

        mpl_pane.object = fig

    def update_swTitle(event):
        
        fig = mpl_pane.object
        ax = fig.axes
        
        if event.new == True:
            ax[0].set_title('', fontsize = 1)
            # fig.set_size_inches(plotParam.fig_size, forward=True)

        if event.new == False:
            if text_title.value == '':
                text_title.placeholder = plot_list[idx_ws].title
                ax[0].set_title(plot_list[idx_ws].title, fontsize = font_size_slide.value)
            else:
                ax[0].set_title(text_title.value, fontsize = font_size_slide.value)
        
        
        mpl_pane.object = fig



    def click_button(event):
        
        fig = mpl_pane.object
        
        sh_name = 'Pattern_Data'
        workbook = certifyGspread(keyfile_dict, sh_name)

        list_ws = workbook.worksheets()
        new_sheet_list = [list_ws[idx].title for idx in range(len(list_ws))]

        idx_ws = 0
        
        select.options = new_sheet_list
        select.value = new_sheet_list[idx_ws]

        for idx in range(len(sheet_list)):
            sheet_list.pop()

        for new_vl in new_sheet_list:
            sheet_list.append(new_vl)

        current_ws = workbook.worksheet(sheet_list[0])
        plot_list = get_plot_params(current_ws, 0)

        fig, plotParam = get_fig_data(plot_list)
        end_x, step_x = round_two(plot_list[0].x_lim[1])
        start_x = 0 #round_two(plot_list[idx_ws].x_lim[0])
        
        end_y, step_y = round_two(plot_list[0].y_lim[1])
        start_y = 0 #round_two(plot_list[idx_ws].x_lim[0])

        ax = fig.axes

        text_title.value = ''
        text_xlabel.value = ''
        text_ylabel.value = ''

        text_title.placeholder = plot_list[0].title
        text_xlabel.placeholder = plot_list[0].x_label
        text_ylabel.placeholder = plot_list[0].y_label

        xlim_range.start = start_x - 50*step_x
        xlim_range.end = end_x + 50*step_x
        xlim_range.value = (plot_list[0].x_lim[0], plot_list[0].x_lim[1])
        xlim_range.step = step_x
        
        ylim_range.start = start_y - 50*step_y
        ylim_range.end = end_y + 50*step_y
        ylim_range.value = (plot_list[0].y_lim[0], plot_list[0].y_lim[1])
        ylim_range.step = step_y
        
        wdth_slide.value = 20
        hght_slide.value = 15
        font_size_slide.value = 16
        ln_thck_slide.value = 1

        lgd_col.disabled = False
        lgd_loc.disabled = False
        lgd_col.value = 1
        lgd_col.end = len(plot_list)
        lgd_loc.value = 'upper left'
        title_switch.value = False
        enbl_exp.value = False
        xlim_sci.value = False
        ylim_sci.value = False

        enbl_bbox.value = False
        lgd_bbx_x.disabled = True
        lgd_bbx_y.disabled = True
        # lgd_fn_col.disabled = True
        # lgd_fn_col.end = len(plot_list)
        lgd_bbx_x.value = 0
        lgd_bbx_y.value = 0
        # lgd_fn_col.value = 1

        ax[0].set_xlim(0, end_x)
        ax[0].set_ylim(0, end_y)

        mpl_pane.object = fig
        
        # Remove current watchers for recreation later
        # Without this, watchers are duplicated every new tab.
        for idx, colors in enumerate(color_curves.objects):
            colors.param.unwatch(cl_wtchrs[idx])

        for idx, style in enumerate(style_curves.objects):
            style.param.unwatch(ln_wtchrs[idx])


        if len(plot_list) < len(plot_clrs):

            for idx_add in range(len(plot_list), len(plot_clrs)):

                color_dic.pop("colorpick_{0}".format(idx_add))
                style_dic.pop("linestlpick_{0}".format(idx_add)) 

                plot_clrs.pop()
                plot_stls.pop()
        
        
        for idx, clr_key in enumerate(color_dic):
            color_dic[clr_key].value = plot_list[idx].clr
            plot_clrs[idx] = plot_list[idx].clr
            
        for idx, stl_key in enumerate(style_dic):
            style_dic[stl_key].value = idx # plot_list[idx].styl_name
            plot_stls.append(plot_list[idx].styl_name)

        if len(plot_list) > len(plot_clrs):

            for idx_add in range(len(plot_clrs), len(plot_list)):


                color_dic["colorpick_{0}".format(idx_add)] = pn.widgets.ColorPicker(name=plot_list[idx_add].label, 
                                                value=plot_list[idx_add].clr)

                style_dic["linestlpick_{0}".format(idx_add)] = pn.widgets.Select(name=' ',
                                                value = idx_add, 
                                                options = dict(zip(get_line_style_list()[0], range(idx_add, len(get_line_style_list()[0]) + idx_add))),
                                                width = 170, align=('end', 'center'))

                plot_clrs.append(plot_list[idx_add].clr)
                plot_stls.append(plot_list[idx_add].styl_name)

                cl_wtchrs.append(0)
                ln_wtchrs.append(0)

        

        grid_list = [None]*(len(list(color_dic.values())) + len(list(style_dic.values())))
        grid_list[::2] = list(color_dic.values())
        grid_list[1::2] = list(style_dic.values())

        clr_ls_grid.objects = grid_list

        color_curves.objects = list(color_dic.values())
        style_curves.objects = list(style_dic.values())
        
        for idx, colors in enumerate(color_curves.objects):
            temp = colors.param.watch(update_color, 'value')
            cl_wtchrs[idx] = temp

        for idx, style in enumerate(style_curves.objects):
            temp = style.param.watch(update_style, 'value')
            ln_wtchrs[idx] = temp

            
    file_format = select_fileformat.value
    
    def update_format(event):

        file_format = event.new
        file_download.filename = 'Vector_image' + '.' + file_format

    select_fileformat.param.watch(update_format, 'value')

    def save_pdf():

        fig = mpl_pane.object

        # fig.set_size_inches(8, 6) #, forward=True)
        
        curr_user = getpass.getuser()
        file_format = select_fileformat.value

        home_path = os.path.expanduser('~')
        
        save_path = os.path.join(os.path.sep, home_path, 'Pictures', curr_user + '_teste.' + file_format)

        file_download.filename = 'Vector_image' + '.' + file_format

        fig.savefig(save_path, format=file_format, dpi = 150, bbox_inches='tight')
        return save_path
    
    def update_color(event):

        fig = mpl_pane.object

        idx_l = plot_clrs.index(event.old)

        # Since I am using the colors to track the changes, the new color can not
        #   be equal to an current value of a different curve. So, in this case
        #   the next_hex() funcion slightly alters the coloer value.
        try:
            plot_clrs.index(event.new)
            new_color = next_hex(event.new)
            color_curves.objects[idx_l].value = new_color
        except ValueError:
            new_color = event.new

        ax = fig.axes
        lines = ax[0].get_lines()
        lines[idx_l].set_color(new_color)
        plot_clrs[idx_l] = new_color

        if enbl_bbox.value == False:

            ax[0].legend(
                    fontsize = font_size_slide.value,
                    ncol = lgd_col.value,
                    loc = lgd_loc.value,
                    fancybox=True,
                    shadow=True
                    )
            
        if enbl_bbox.value == True:

            ax[0].legend(
                    fontsize = lgd_fn_txt.value,
                    ncol = lgd_col.value,
                    loc = 'lower left',
                    bbox_to_anchor = (lgd_bbx_x.value, lgd_bbx_y.value),
                    fancybox=True,
                    shadow=True
                    )

        mpl_pane.object = fig

    # cl_wt_dict = {}

    # for idx, colors in enumerate(color_curves.objects):
        # cl_wt_dict['name_{0}'.format(idx)] = colors.param.watch(update_color, 'value')

    def update_style(event):

        fig = mpl_pane.object

        key_idx_shift = list(event.obj.options.values())[0]

        # ls_old = list(event.obj.options.values())[event.old - key_idx_shift]
        ls_new = list(event.obj.options.keys())[event.new - key_idx_shift]

        idx_cv = key_idx_shift # plot_stls.index(event.old)
        idx_ls = event.new - key_idx_shift

        new_ls, _ = get_line_style(idx_ls, 0)

        ax = fig.axes
        lines = ax[0].get_lines()
        lines[idx_cv].set_linestyle(new_ls)
        plot_stls[idx_cv] =  ls_new

        if enbl_bbox.value == False:

            ax[0].legend(
                    fontsize = font_size_slide.value,
                    ncol = lgd_col.value,
                    loc = lgd_loc.value,
                    fancybox=True,
                    shadow=True
                    )
            
        if enbl_bbox.value == True:

            ax[0].legend(
                    fontsize = lgd_fn_txt.value,
                    ncol = lgd_col.value,
                    loc = 'lower left',
                    bbox_to_anchor = (lgd_bbx_x.value, lgd_bbx_y.value),
                    fancybox=True,
                    shadow=True
                    )

        mpl_pane.object = fig
        
        
    # list_style = list(style_dic.values())

    def update_fig_wdth(event):

        fig = mpl_pane.object
        fig_size = fig.get_size_inches()
                
        new_zie = [event.new*cm_p_inch, fig_size[1]]

        fig.set_size_inches(new_zie)
        
        
        mpl_pane.object = fig
        

    def update_fig_hght(event):

        fig = mpl_pane.object
        fig_size = fig.get_size_inches()

        new_zie = [fig_size[0], event.new*cm_p_inch]

        fig.set_size_inches(new_zie)

        mpl_pane.object = fig

    def update_txt_size(event):

        fig = mpl_pane.object
        
        ax = fig.axes

        if ylim_sci.value == True:
            ax[0].yaxis.offsetText.set_fontsize(event.new - 5)

        
        if xlim_sci.value == True:
            ax[0].xaxis.offsetText.set_fontsize(event.new - 5)

        
        if text_ylabel.value == '':
            ax[0].set_ylabel(plot_list[-1].y_label, fontsize = event.new)
        else:
            ax[0].set_ylabel(text_ylabel.value, fontsize = event.new)


        if title_switch.value == True:
            ax[0].set_title('', fontsize = 1)
        else:
            if text_title.value == '':
                ax[0].set_title(plot_list[-1].title, fontsize = event.new)
            else:
                ax[0].set_title(text_title.value, fontsize = event.new)
        
        ax[0].tick_params(axis='both', which='major', labelsize=event.new)

        if enbl_bbox.value == False:

            ax[0].legend(
                    fontsize = event.new,
                    ncol = lgd_col.value,
                    loc = lgd_loc.value,
                    fancybox=True,
                    shadow=True
                    )
            
        if enbl_bbox.value == True:

            ax[0].legend(
                    fontsize = lgd_fn_txt.value,
                    ncol = lgd_col.value,
                    loc = 'lower left',
                    bbox_to_anchor = (lgd_bbx_x.value, lgd_bbx_y.value),
                    fancybox=True,
                    shadow=True
                    )
            


        mpl_pane.object = fig

    def update_plot_lw(event):

        ln_thck_slide.value = np.round(event.new, 1)

        fig = mpl_pane.object
        
        ax = fig.axes

        lines = ax[0].get_lines()

        for line in lines:
            line.set_linewidth(event.new)

        if enbl_bbox.value == False:

            ax[0].legend(
                    fontsize = font_size_slide.value,
                    ncol = lgd_col.value,
                    loc = lgd_loc.value,
                    fancybox=True,
                    shadow=True
                    )
            
        if enbl_bbox.value == True:

            ax[0].legend(
                    fontsize = lgd_fn_txt.value,
                    ncol = lgd_col.value,
                    loc = 'lower left',
                    bbox_to_anchor = (lgd_bbx_x.value, lgd_bbx_y.value),
                    fancybox=True,
                    shadow=True
                    )

        
        mpl_pane.object = fig

    def update_lgd_col(event):

        fig = mpl_pane.object
        
        ax = fig.axes

        if enbl_bbox.value == False:
        
            ax[0].legend(
                    fontsize = font_size_slide.value,
                    ncol = event.new,
                    loc = lgd_loc.value,
                    fancybox=True,
                    shadow=True
                    )
        else:
            ax[0].legend(
                fontsize = lgd_fn_txt.value,
                ncol = lgd_col.value,
                loc = 'lower left',
                bbox_to_anchor = (lgd_bbx_x.value, lgd_bbx_y.value),
                fancybox=True,
                shadow=True
                )

        
        mpl_pane.object = fig

    def update_lgd_loc(event):

        fig = mpl_pane.object
        
        ax = fig.axes
        
        ax[0].legend(
                fontsize = font_size_slide.value,
                ncol = lgd_col.value,
                loc = event.new,
                fancybox=True,
                shadow=True
                )

        
        mpl_pane.object = fig

    def up_expx(event):

        fig = mpl_pane.object
    
        ax = fig.axes

        if event.new == True:
            
            ax[0].legend(
                    fontsize = font_size_slide.value,
                    ncol = lgd_col.value,
                    loc = lgd_loc.value,
                    fancybox=True,
                    shadow=True, 
                    mode = 'expand'
                    )
            
        else:
            
            ax[0].legend(
                    fontsize = font_size_slide.value,
                    ncol = lgd_col.value,
                    loc = lgd_loc.value,
                    fancybox=True,
                    shadow=True, 
                    )
            

        mpl_pane.object = fig


    def fun_bbox(event):

        if event.new == True:
            lgd_bbx_x.disabled = False
            lgd_bbx_y.disabled = False
            lgd_fn_txt.disabled = False
            lgd_fn_txt.value = font_size_slide.value
            # lgd_fn_col.disabled = False
            # lgd_col.disabled = True
            lgd_loc.disabled = True
            enbl_exp.disabled = True

            fig = mpl_pane.object
        
            ax = fig.axes
            
            ax[0].legend(
                    fontsize = font_size_slide.value,
                    ncol = lgd_col.value,
                    loc = 'lower left',
                    bbox_to_anchor = (lgd_bbx_x.value, lgd_bbx_y.value),
                    fancybox=True,
                    shadow=True
                    )

            mpl_pane.object = fig

        if event.new == False:
            lgd_bbx_x.disabled = True
            lgd_bbx_y.disabled = True
            lgd_fn_txt.disabled = True
            # lgd_fn_col.disabled = True
            # lgd_col.disabled = False
            lgd_loc.disabled = False
            enbl_exp.disabled = False
            lgd_bbx_x.value = 0
            lgd_bbx_y.value = 0
            # lgd_fn_col.value = 1

            fig = mpl_pane.object
        
            ax = fig.axes
            
            ax[0].legend(
                    fontsize = font_size_slide.value,
                    ncol = lgd_col.value,
                    loc = lgd_loc.value,
                    fancybox=True,
                    shadow=True
                    )

            mpl_pane.object = fig

    def up_bbox_x(event):

        fig = mpl_pane.object

        lgd_bbx_x.value = np.round(event.new, 3)
        
        ax = fig.axes
        
        ax[0].legend(
                fontsize = font_size_slide.value,
                ncol = lgd_col.value,
                loc = 'lower left',
                bbox_to_anchor = (event.new, lgd_bbx_y.value),
                fancybox=True,
                shadow=True
                )

        
        mpl_pane.object = fig

    def up_bbox_y(event):

        fig = mpl_pane.object

        lgd_bbx_y.value = np.round(event.new, 3)
        
        ax = fig.axes
        
        ax[0].legend(
                fontsize = font_size_slide.value,
                ncol = lgd_col.value,
                loc = 'lower left',
                bbox_to_anchor = (lgd_bbx_x.value, event.new),
                fancybox=True,
                shadow=True
                )

        
        mpl_pane.object = fig

    def up_fn_txt(event):

        fig = mpl_pane.object
        
        ax = fig.axes
        
        ax[0].legend(
                fontsize = event.new,
                ncol = lgd_col.value,
                loc = 'lower left',
                bbox_to_anchor = (lgd_bbx_x.value, lgd_bbx_y.value),
                fancybox=True,
                shadow=True
                )

        
        mpl_pane.object = fig



            
    file_download = pn.widgets.FileDownload(callback = save_pdf, filename = 'Vector_image' + '.' + file_format, embed=False)

    # file_input = pn.widgets.FileInput()
    # print(file_input)

    # def get_File():
    #     return file_input
    
    cl_wtchrs = []
        
    for colors in color_curves.objects:
        temp = colors.param.watch(update_color, 'value')
        cl_wtchrs.append(temp)

    ln_wtchrs = []

    for style in style_curves.objects:
        temp = style.param.watch(update_style, 'value')
        ln_wtchrs.append(temp)

    text_title.param.watch(update_title, 'value')
    text_xlabel.param.watch(update_xLabel, 'value')
    text_ylabel.param.watch(update_yLabel, 'value')
    xlim_range.param.watch(update_xlim, 'value')
    xlim_sci.param.watch(update_xSci, 'value')
    ylim_range.param.watch(update_ylim, 'value')
    ylim_sci.param.watch(update_ySci, 'value')
    title_switch.param.watch(update_swTitle, 'value')
    wdth_slide.param.watch(update_fig_wdth, 'value') 
    hght_slide.param.watch(update_fig_hght, 'value') 
    font_size_slide.param.watch(update_txt_size, 'value') 
    ln_thck_slide.param.watch(update_plot_lw, 'value') 
    lgd_col.param.watch(update_lgd_col, 'value') 
    lgd_loc.param.watch(update_lgd_loc, 'value') 
    button_update.on_click(click_button)
    enbl_bbox.param.watch(fun_bbox, 'value')
    lgd_bbx_x.param.watch(up_bbox_x, 'value')
    lgd_bbx_y.param.watch(up_bbox_y, 'value')
    lgd_fn_txt.param.watch(up_fn_txt, 'value')
    enbl_exp.param.watch(up_expx, 'value')

    # title_eval = pn.Row(text_title, title_switch)


    dash_fig_ctrl = pn.Column(title_grid, text_xlabel, text_ylabel, xlim_grid, ylim_grid, lgd_ctrl, lgd_fine)

    dash_Button = pn.Row(file_download, button_update)

    dash_iter = pn.Column(select, fig_size, txt_lw, select_fileformat, dash_Button, mpl_pane)

    plot_ctrl = pn.Row(dash_fig_ctrl, clr_ls_grid)
    # plot_view = pn.Column(plot_ctrl, )

    # dash = pn.Row(dash_fig_ctrl, mpl_pane, dash_iter, color_curves, pn.Spacer(width = 10), style_curves).servable()    
    # dash = pn.Row(dash_fig_ctrl, mpl_pane, clr_ls_grid, dash_iter).servable()    
    dash = pn.Row(plot_ctrl, dash_iter).servable()

    return dash