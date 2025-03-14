# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 16:10:19 2022

@author: Maarten

Definition of the SettingsDialog class. This class is used to modify the
settings of the application
"""

#%% packages
import tkinter as tk


#%%

class SettingsDialog(tk.Toplevel):
    """
    Dialog to modify application settings
    """

    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self.master = master

        #settings
        self.settings = self.master.settings

        #set default size
        self.geometry('300x200')

        #set title
        self.title('Settings')

        #create variables
        self.var_linewidth = tk.StringVar(
            value=str(self.settings.linewidth))
        self.var_point_size = tk.StringVar(
            value=str(self.settings.point_size))
        self.var_sensitivity = tk.StringVar(
            value=str(self.settings.reactivation_sensitivity))

        #add attributes to store old value
        self.var_linewidth.old_value = self.var_linewidth.get()
        self.var_point_size.old_value = self.var_point_size.get()
        self.var_sensitivity.old_value = self.var_sensitivity.get()

        #use .trace() to add a method to the tkinter variables that takes action
        #if the user entered an invalid value
        self.var_linewidth.trace('w',
            lambda *args : self.check_numeric_value(self.var_linewidth))
        self.var_point_size.trace('w',
            lambda *args :self.check_numeric_value(textvar=self.var_point_size))
        self.var_sensitivity.trace('w',
            lambda *args : self.check_numeric_value(textvar=self.var_sensitivity))

        #create frames
        self.frame_linewidth = tk.Frame(master = self)
        self.frame_point_size = tk.Frame(master=self)
        self.frame_sensitivity = tk.Frame(master=self)

        #create labels
        label_width = 20
        self.label_linewidth = tk.Label(master=self.frame_linewidth,
                                        text="Linewidth",
                                        anchor="w",
                                        width=label_width)
        self.label_point_size = tk.Label(master=self.frame_point_size,
                                              text="Point size",
                                              anchor="w",
                                              width=label_width)
        self.label_sensitivity = tk.Label(master=self.frame_sensitivity,
                                              text="Re-activation sensitivity",
                                              anchor="w",
                                              width=label_width)

        unit_width = 5
        self.label_linewidth_unit = tk.Label(master=self.frame_linewidth,
                                             text="px",
                                             anchor="w",
                                             width=unit_width)
        self.label_point_size_unit = tk.Label(master=self.frame_point_size,
                                              text="px",
                                              anchor="w",
                                              width=unit_width)
        self.label_sensitivity_unit = tk.Label(master=self.frame_sensitivity,
                                               text="px",
                                               anchor="w",
                                               width=unit_width)

        #create entry fields
        entry_width = 5
        self.field_linewidth = tk.Entry(self.frame_linewidth,
                                    width=entry_width,
                                    textvariable=self.var_linewidth)
        self.field_point_size = tk.Entry(self.frame_point_size,
                                              width=entry_width,
                                              textvariable=self.var_point_size)
        self.field_sensitivity = tk.Entry(self.frame_sensitivity,
                                              width=entry_width,
                                              textvariable=self.var_sensitivity)

        #create buttons
        self.button_ok = tk.Button(self,
                                   text="OK",
                                   command=self.confirm)

        #outline all elements
        self.frame_linewidth.pack(anchor="w",pady=5)
        self.label_linewidth.pack(side="left")
        self.field_linewidth.pack(side="left")
        self.label_linewidth_unit.pack(side="left")

        self.frame_point_size.pack(anchor='w', pady=5)
        self.label_point_size.pack(side="left")
        self.field_point_size.pack(side="left")
        self.label_point_size_unit.pack(side="left")

        self.frame_sensitivity.pack(anchor='w', pady=5)
        self.label_sensitivity.pack(side="left")
        self.field_sensitivity.pack(anchor='w', side='left')
        self.label_sensitivity_unit.pack(side="left")

        self.button_ok.pack(side='bottom', pady=5)

        #bind hitting return/enter key to invocation of button/checkbox
        self.bind_class("Button",
                        "<Key-Return>",
                        lambda event: event.widget.invoke())
        self.bind_class("Checkbutton",
                        "<Key-Return>",
                        lambda event: event.widget.invoke())

        #general child-window settings
        #set child to be on top of the main window
        self.transient(master)
        #hijack all commands from the master (clicks on the main window are ignored)
        self.grab_set()
        #pause anything on the main window until this one closes (optional)
        self.master.wait_window(self)

    def check_numeric_value(self, textvar):
        """
        Check if the changes to a numeric attribute still result in a valid entry
        (positive number)

        If the changes would result in an invalid entry, the changes are undone
        by replacing the invalid entry with the value stored in the attribute
        .old_value
        """

        #If the field is empty (equal to a zero entry); accept this
        if textvar.get() == "":
            #update textvar.old_value
            textvar.old_value = textvar.get()
            return

        #valid textvar: only digits, maximum one comma and possibly a
        #negative sign at the beginning of the string

        #preprocess textvar value so we can check the conditions specified above
        value = textvar.get()
        #replace a single comma by ""
        value = value.replace(".", "", 1)
        #remove a negative sign at the beginning
        if value[0] == "-":
            if len(value) >= 2:
                value = value[1:]
            else: #len(value) == 1:
                #value is just '-', accept this
                #update textvar.old_value
                textvar.old_value = textvar.get()
                return

        if value.isdigit():
            textvar.old_value = textvar.get()
        else:
            #textvar is unvalid
            #resons for unvalidity: presence of charaters, mmore than one
            #decimal separator, negative sign on another position then the first
            textvar.set(textvar.old_value)

    def confirm(self):
        """
        Save all modified settings and close dialog
        """

        #first convert all numerc variables to positive integers
        numeric_variables = [self.var_linewidth,
                             self.var_point_size,
                             self.var_sensitivity]
        numeric_values = []

        for textvar in numeric_variables:
            value = textvar.get()
            if value in ["", "-"]:
                value = 0
            else:
                value = round(float(value))
                value = max(0, value)

            numeric_values.append(value)

        #assign all values to the corresponding attributes of settings
        self.settings.linewidth = numeric_values[0]
        self.settings.point_size = numeric_values[1]
        self.settings.reactivation_sensitivity = numeric_values[2]

        #destroy child window
        self.destroy()
