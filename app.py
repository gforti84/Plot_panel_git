
#--------------------------------------------------------------------------------#
#                                                                                #
#                                Python Plot                                     #
#           Authors: Gabriel Mendonça and Caio Moura                             #
#                         Last change date: 30/01/2024                           #
#                                                                                #
#   Description: web based tool for ofering python ploting functionalities.      #
#                The ploting data is gathered from a google sheet. Main ploting  #
#                parameters are already defined from this google sheet, namely   #
#                the plot title, x and y labels, and curves legends. The web     #
#                based tool allow the editing of such parameters and saving      #
#                in vector image, using pdf extension                            #
#                                                                                #
#                                                                                #
#--------------------------------------------------------------------------------#

from PlotLib.Methods import (
    certifyGspread 
)

from PlotLib.PanelLib import (
    run_panel
)

import panel as pn
import ast
import os

# from oauth2client.service_account import ServiceAccountCredentials

def panel_app():
    
    file_input = pn.widgets.FileInput(accept='.json')

    cwd_path = os.getcwd()
    load_img = os.path.join(os.path.sep, cwd_path, 'PlotLib', 'dwight_ghibli.jpg')

    img = pn.pane.JPG(load_img, width = 555)

    exp_txt = pn.pane.Str('I am the Assistant to the Regional Manager, please give me the credential file')
    
    dash = pn.Row(pn.Column(img, exp_txt, file_input)).servable()
   
    def up_file(event):
        byte_str = event.new

        dict_str = byte_str.decode("UTF-8")
        keyfile_dict = ast.literal_eval(dict_str)

        sh_name = 'Pattern_Data'
        workbook = certifyGspread(keyfile_dict, sh_name)

        dash[0] = run_panel(workbook, keyfile_dict)

    file_input.param.watch(up_file, 'value')
    
    return dash
    
# def main():

#     pn.serve(panel_app, title="Who am I?", port = 9001, websocket_origin=['*'], autoreload = True, show = True)
    
# if __name__ == "__main__":
#     main()

panel_app() 


# --> remove the pn.serve(...) from the main() and use this in the terminal
# panel serve app.py --show --autoreload --port 9001 --allow-websocket-origin *:9001 --allow-websocket-origin=*


# panel serve app.py --show --autoreload --port 9001 --allow-websocket-origin *:9001 --allow-websocket-origin=* --basic-auth my_password --cookie-secret my_super_safe_cookie_secret

