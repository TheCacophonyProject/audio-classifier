'''
Created on 5 Sep 2019

@author: tim
'''

#  https://www.youtube.com/watch?v=A0gaXfM1UN0&t=343s
# https://www.youtube.com/watch?v=D8-snVfekto
# How to Program a GUI Application (with Python Tkinter)!
# https://www.tutorialspoint.com/python3/python_gui_programming

HEIGHT = 600
WIDTH = 1000

import tkinter as tk
from tkinter import ttk

import functions

LARGE_FONT= ("Verdana", 12)


class Main_GUI(tk.Tk):
    # comment
    
    def __init__(self, *args, **kwargs):
        
        
        tk.Tk.__init__(self, *args, **kwargs)        
        tk.Tk.wm_title(self, "Cacophony Audio Manager")
        # https://stackoverflow.com/questions/47829756/setting-frame-width-and-height?rq=1
        container = tk.Frame(self,width=800, height=500)
        container.grid_propagate(False)        
        container.pack(side="top", fill="both", expand=True)        
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
       
        self.frames = {}
        
        for F in (HomePage, SettingsPage, RecordingsPage):
        
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
        
        button1 = ttk.Button(self, text="Settings Page",
                            command=lambda: controller.show_frame(SettingsPage))    
        button1.pack()
        
        button2 = ttk.Button(self, text="Recordings Page",
                            command=lambda: controller.show_frame(RecordingsPage))
        
        button2.pack()
        
class SettingsPage(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        
        recordings_Folder = functions.getRecordingsFolder()
#         print("in settings ", recordings_Folder)
        
        
        # https://www.python-course.eu/tkinter_entry_widgets.php
        
        tk.Label(self,text="Recordings location").grid(column=0, columnspan=1, row=0)
#         tk.Label(self, text="Last Name").grid(column=0, columnspan=1, row=1)

        #https://stackoverflow.com/questions/16373887/how-to-set-the-text-value-content-of-an-entry-widget-using-a-button-in-tkinter
        entryText = tk.StringVar()
        recordings_folder_entry = (tk.Entry(self, textvariable=entryText, width=80)).grid(row=0, column=1, columnspan=1)
#         recordings_folder_entry.grid(row=0, column=2, rowspan=6)
        entryText.set( recordings_Folder )
        
#         e2 = tk.Entry(self)
        
        
#         e2.grid(row=1, column=1)
        
        
        tk.Button(self, 
                  text='Save', command=lambda: functions.saveSettings(recordings_folder_entry.get())).grid(row=6, 
                                                               column=0, 
                                                               sticky=tk.W, 
                                                               pady=4)
          
#         tk.Button(self, 
#                   text='Back to Home', 
#                   command=self.quit).grid(row=3, 
#                                             column=1, 
#                                             sticky=tk.W, 
#                                             pady=4)

        tk.Button(self, 
                  text='Back to Home', 
                  command=lambda: controller.show_frame(HomePage)).grid(row=6, 
                                            column=1, 
                                            sticky=tk.W, 
                                            pady=4)
                  
#         button1 = ttk.Button(self, text="Back to Home",
#                             command=lambda: controller.show_frame(HomePage))
        
#         label = ttk.Label(self, text="Settings Page", font=LARGE_FONT)
#         label.pack(pady=10,padx=10)
        
        
        
#         button_get_names = ttk.Button(self, text="Get Names",
#                             command=lambda: functions.getRecordingsFolder())
#         button_get_names.pack()
#         
#         button1 = ttk.Button(self, text="Back to Home",
#                             command=lambda: controller.show_frame(HomePage))
#         button1.pack()
#         
#         button2 = ttk.Button(self, text="Go to Recordings Page",
#                             command=lambda: controller.show_frame(RecordingsPage))
#         button2.pack()
        
class RecordingsPage(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="Recordings Page", font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        
        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(HomePage))
        button1.pack() 
        
        button2 = ttk.Button(self, text="Go to Settings Page",
                            command=lambda: controller.show_frame(SettingsPage))
        button2.pack()       
        
app = Main_GUI()
app.mainloop() 