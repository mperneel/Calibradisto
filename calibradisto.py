# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 11:55:28 2023

@author: Maarten

Master script of Calibragen
"""

#%% Load packages
import ctypes
import os
import tkinter as tk
import numpy as np

from annotation_canvas import AnnotationCanvas
from object_canvas import ObjectCanvas
from annotations import Annotations
from settings import Settings
from settings_dialog import SettingsDialog

#%% Main application

class Application(tk.Frame):
    """
    Master window of CoBRA pointer
    """
    def __init__(self, master=None, program_dir=None):
        #initiate frame
        tk.Frame.__init__(self, master)
        self.pack()
        self.master = master

        #make sure the application fills the whole window
        self.master.state('zoomed')
        root.update()

        #Declare attributes
        self.program_dir = program_dir #path to software files
        self.mode = 0 #annotation mode
        self.wdir = None #working directory
        self.detector = None #detector class to initiate annotations
        self.bool_prime_annotations = False
        #boolean indicating if annotations should be primed
        self.df_loss = None
        #dataframe with losses for annotated images

        #get useable width and height (expressed in pixels)
        self.uw = root.winfo_width() #useable_width
        self.uh = root.winfo_height() #useable_height

        #format application

        #initiate main panel
        self.main_panel = tk.PanedWindow(bd=0,
                                         bg="black",
                                         orient=tk.HORIZONTAL)
        self.main_panel.pack(fill=tk.BOTH,
                             expand=True)

        #set title
        self.master.title("Calibradisto")

        #Declare attributes belonging to custom classes
        #annotations
        self.annotations = Annotations()

        #setings
        self.settings = Settings()

        #canvas to show image
        self.annotation_canvas = AnnotationCanvas(master=self,
                                                  bd=10,
                                                  width=self.uw * 0.7,
                                                  height=self.uh)

        #canvas with masks
        self.object_canvas = ObjectCanvas(master=self,
                                      width=int(self.uw * 0.15),
                                      height=int(self.uh*0.5))

        #add annotation canvas
        self.main_panel.add(self.annotation_canvas)

        #create second paned window on the left side to add skeleton_canvas
        #and object_canvas above each other
        self.right_panel = tk.PanedWindow(self.main_panel,
                                        bd=0,
                                        bg="black",
                                        orient=tk.VERTICAL)

        self.main_panel.add(self.right_panel)

        #add mask canvas
        self.right_panel.add(self.object_canvas)

        #configure menu
        self.menubar = tk.Menu(self.master)
        self.master.config(menu=self.menubar)

        #file menu
        self.file_menu = tk.Menu(self.menubar, tearoff=False)
        self.file_menu.add_command(label="Open image (Ctrl+O)",
                                   command=self.annotation_canvas.open_image)
        self.file_menu.add_command(label="Close image (Ctrl+W)",
                                   command=self.annotation_canvas.close_image)
        self.file_menu.add_command(label="Save annotations (Ctrl+S)",
                                   command=self.save)
        self.file_menu.add_command(label="Delete point (Del)",
                                   command=self.annotation_canvas.delete_point)
        self.file_menu.add_command(label="Delete line (Ctrl+Del)",
                                   command=self.annotation_canvas.delete_line)
        self.menubar.add_cascade(label="File", menu=self.file_menu)

        self.master.bind("<Control-o>", lambda event: self.annotation_canvas.open_image())
        self.master.bind("<Control-w>", lambda event: self.annotation_canvas.close_image())
        self.master.bind("<Control-Delete>", lambda event: self.annotation_canvas.delete_line())
        self.master.bind("<Key-Delete>", lambda event: self.delete_point())
        #Delete is bound to two methods therefore a method in the Application
        #class is provoked, which activates on it's turn
        #self.skeleton_canvas.delete_point() or
        #self.annotation_canvas.delete_point(), depending on the mode of the
        #application (annotation mode or skeleton mode)

        self.master.bind("<Control-s>", lambda event: self.save())
        #Save is bound to two methods, therefore, a method in the Application
        #class is first provoked, which activates on it's turn the appropriate
        #method of SkeletonCanvas or AnnotationCanvas

        #disable all menu items which may only be used when an image is opened
        self.file_menu.entryconfig("Close image (Ctrl+W)", state="disabled")
        self.file_menu.entryconfig("Save annotations (Ctrl+S)", state="disabled")
        self.file_menu.entryconfig("Delete point (Del)", state="disabled")
        self.file_menu.entryconfig("Delete line (Ctrl+Del)", state="disabled")

        #setting menu
        self.settings_menu = tk.Menu(self.menubar, tearoff=False)
        self.settings_menu.add_command(label="Settings", command=self.modify_settings)
        self.menubar.add_cascade(label="Settings", menu=self.settings_menu)

        #help menu
        self.help_menu = tk.Menu(self.menubar, tearoff=False)
        self.help_menu.add_command(label="Help (F1)", command=self.launch_help)
        self.menubar.add_cascade(label="Help", menu=self.help_menu)

        self.master.bind("<F1>", lambda event: self.launch_help())

        #bind events to methods
        self.master.bind("<Configure>", lambda event: self.resize_app())

        self.master.bind("<Key-Return>",
                         lambda event: self.annotation_canvas.new_line())
        #remark that the key is bound to self.master (root)

        #dimension self.window properly
        self.resize_app()

    def launch_help(self):
        """
        Launch the help file
        """
        os.startfile(os.path.join(self.program_dir, "help.pdf"))

    def resize_app(self):
        """
        Adjust the position of the sash when te application is resized
        """
        uw = root.winfo_width() #useable_width
        if self.uw != uw:
            uw_init = self.uw
            self.uw = uw

            sash_position_new = np.round(self.main_panel.sash_coord(0)[0] * self.uw/uw_init)\
                .astype(int)
            self.main_panel.sash_place(0,
                                       x=sash_position_new,
                                       y=self.main_panel.sash_coord(0)[1])

    def delete_point(self):
        """
        Decisive method to delete a keypoint of an object or a keypoint of the
        skeleton
        """
        self.annotation_canvas.delete_point()

    def save(self):
        """
        Decisive method to save the annotations of the current image or the skeleton
        """
        self.annotation_canvas.save()

    def configure_menus(self):
        """
        Enable or disable menu options if there is/isn't an image loaded
        """
        if self.annotation_canvas.image_name is not None:
            self.file_menu.entryconfig("Close image (Ctrl+W)", state="active")
            self.file_menu.entryconfig("Save annotations (Ctrl+S)", state="active")
            self.file_menu.entryconfig("Delete point (Del)", state="active")
            self.file_menu.entryconfig("Delete line (Ctrl+Del)", state="active")
        else: #self.annotation_canvas.image_name is None:
            self.file_menu.entryconfig("Close image (Ctrl+W)", state="disabled")
            self.file_menu.entryconfig("Save annotations (Ctrl+S)", state="disabled")
            self.file_menu.entryconfig("Delete point (Del)", state="disabled")
            self.file_menu.entryconfig("Delete line (Ctrl+Del)", state="disabled")

    def modify_settings(self):
        """
        Open a dialog to modify the application settings
        """
        SettingsDialog(master=self)
        self.annotation_canvas.update_image(mode=0)


#%% Start mainloop

#adjust DPI to screen resolution
ctypes.windll.shcore.SetProcessDpiAwareness(1)

#start mainloop
root = tk.Tk()

#set application icon
if os.path.exists("icon/calibradisto_icon.ico"):
    #this case will be executed when the application is run from the .py file
    root.iconbitmap("icon/calibradisto_icon.ico")
elif os.path.exists("_internal/icon/calibradisto_icon.ico"):
    #this case will be executed when the application is run from a .exe file
    #generated with pyinstaller
    root.iconbitmap("_internal/icon/calibradisto_icon.ico")

soft_dir = os.getcwd()
app = Application(master=root, program_dir=soft_dir)
app.mainloop()
