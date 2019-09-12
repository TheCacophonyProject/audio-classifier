'''
Created on 5 Sep 2019

@author: tim
'''

#  https://www.youtube.com/watch?v=A0gaXfM1UN0&t=343s
# https://www.youtube.com/watch?v=D8-snVfekto
# How to Program a GUI Application (with Python Tkinter)!
# https://www.tutorialspoint.com/python3/python_gui_programming

HEIGHT = 600
WIDTH = 1400

import tkinter as tk
from tkinter import ttk
from tkinter import *

import gui_functions

LARGE_FONT= ("Verdana", 12)


class Main_GUI(tk.Tk):
    # comment
    
    def __init__(self, *args, **kwargs):
        
        
        tk.Tk.__init__(self, *args, **kwargs)        
        tk.Tk.wm_title(self, "Cacophony Audio Manager")
        # https://stackoverflow.com/questions/47829756/setting-frame-width-and-height?rq=1
        container = tk.Frame(self,width=WIDTH, height=HEIGHT)
        container.grid_propagate(False)        
        container.pack(side="top", fill="both", expand=True)        
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
       
        self.frames = {}
        
        for F in (HomePage, SettingsPage, RecordingsPage, TaggingPage):
        
            frame = F(container, self)
            self.frames[F] = frame
            
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame(HomePage)
        
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        
def qf(param):
    print(param)
        
class HomePage(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
       
        label = tk.Label(self, text="Home Page", font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        
        button1 = ttk.Button(self, text="Settings",
                            command=lambda: controller.show_frame(SettingsPage))    
        button1.pack()
        
        tagging_button = ttk.Button(self, text="Tagging",
                            command=lambda: controller.show_frame(TaggingPage))        
        tagging_button.pack()
        
        button2 = ttk.Button(self, text="Recordings Page",
                            command=lambda: controller.show_frame(RecordingsPage))        
        button2.pack()
        
class SettingsPage(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        
        recordings_Folder = gui_functions.getRecordingsFolderWithOutHome()
        
        # https://www.python-course.eu/tkinter_entry_widgets.php        
        tk.Label(self,text="Recordings location").grid(column=0, columnspan=1, row=0)

        #https://stackoverflow.com/questions/16373887/how-to-set-the-text-value-content-of-an-entry-widget-using-a-button-in-tkinter
        entryText = tk.StringVar()
        recordings_folder_entry = tk.Entry(self, textvariable=entryText, width=80)
        recordings_folder_entry.grid(row=0, column=1, columnspan=1)
        entryText.set( recordings_Folder )
        

        tk.Button(self, 
                  text='Save', command=lambda: gui_functions.saveSettings(recordings_folder_entry.get())).grid(row=6, 
                                                               column=0, 
                                                               sticky=tk.W, 
                                                               pady=4)     

        tk.Button(self, 
                  text='Back to Home', 
                  command=lambda: controller.show_frame(HomePage)).grid(row=6, 
                                            column=1, 
                                            sticky=tk.W, 
                                            pady=4)                  

        
class TaggingPage(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="Tagging Page", font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        
        get_tags_button = ttk.Button(self, text="Get tags from server",
                            command=lambda: gui_functions.get_all_tags_for_all_devices_in_local_database())
        get_tags_button.pack()  
        
        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(HomePage))
        button1.pack() 
        
        

class RecordingsPage(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        title_label = ttk.Label(self, text="Recordings Page", font=LARGE_FONT)
#         label.pack(pady=10,padx=10)
        title_label.grid(column=0, columnspan=1, row=0)
        
        device_name_label = ttk.Label(self, text="Device name e.g fpF7B9AFNn6hvfVgdrJB").grid(column=0, columnspan=1, row=1)
             
        device_name = StringVar(value='fpF7B9AFNn6hvfVgdrJB')
        device_name_entry = tk.Entry(self,  textvariable=device_name, width=30).grid(column=1, columnspan=1, row=1)
        
        device_super_name_label = ttk.Label(self, text="Device Super name (e.g. Hammond Park").grid(column=2, columnspan=1, row=1)
        
        device_super_name = StringVar(value='Hammond Park')
        device_super_name_entry = tk.Entry(self,  textvariable=device_super_name, width=30).grid(column=3, columnspan=1,row=1)
       
        
        
        get_recordings_button = ttk.Button(self, text="Load Recordings from local folder",
                            command=lambda: gui_functions.load_recordings_from_local_folder(device_name.get(), device_super_name.get())).grid(column=0, columnspan=2, row=2)
#         get_recordings_button = ttk.Button(self, text="Load Recordings from local folder",
#                             command=lambda: gui_functions.load_recordings_from_local_folder(device_super_name.get())).grid(column=0, columnspan=1, row=2)
 

        get_recording_information_from_server_button = ttk.Button(self, text="Get Recording Information for recordings imported from local file system",
                            command=lambda: gui_functions.update_recording_information_for_all_local_database_recordings()).grid(column=0, columnspan=2, row=3)
              
        
        get_new_recordings_from_server_button = ttk.Button(self, text="Get New Recordings From Server",
                            command=lambda: gui_functions.get_recordings_from_server(device_name.get(), device_super_name.get())).grid(column=0, columnspan=2, row=4)
        get_new_recordings_from_server_label = ttk.Label(self, text="This will get the recordings for the device in the device name box. It will also assign a super name from the Super Name box").grid(column=2, columnspan=3, row=4)  
                                               
        
        scan_local_folder_for_recordings_not_in_local_db_and_update_button = ttk.Button(self, text="Scan recordings folder for recordings not in local db and update",
                            command=lambda: gui_functions.scan_local_folder_for_recordings_not_in_local_db_and_update(device_name.get(), device_super_name.get())).grid(column=0, columnspan=2, row=5)
                                                
        scan_label = ttk.Label(self, text="If you do NOT know the device name or super name enter unknown in the fields. The device name will be updated automatically").grid(column=2, columnspan=3, row=5)                   
                       
        
        back_to_home_button = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(HomePage)).grid(column=0, columnspan=1, row=6)
        

                
        
app = Main_GUI()
app.mainloop() 