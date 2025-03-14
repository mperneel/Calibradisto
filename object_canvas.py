# -*- coding: utf-8 -*-
"""
Created on Fri Jul 23 13:09:09 2021

@author: Maarten
"""
#%% import packages
import tkinter as tk

#%%

class ObjectCanvas(tk.Frame):
    """
    The ObjectCanvas shows all defined objects (lines) and allows to select and/or
    delete one of the previously defined lines
    """

    def __init__(self, master, **kwargs):
        super().__init__(**kwargs)

        #assign master
        self.master = master

        #update idletasks
        self.master.master.update_idletasks()

        #create listbox and scrollbar
        self.list_lines = tk.Listbox(master=self)
        self.scrollbar = tk.Scrollbar(self,
                                      orient="vertical",
                                      width=20)

        #configure scrollbar
        self.scrollbar.config(command=self.list_lines.yview)
        self.list_lines.config(yscrollcommand=self.scrollbar.set)

        #bind events to self.list_lines
        self.list_lines.bind("<<ListboxSelect>>",
                               lambda event: self.activate_line())
        self.list_lines.bind("<Delete>",
                               lambda event: self.delete_line())

        #create button_frm
        self.buttons_frm = tk.Frame(master=self)
        self.btn_draw_new_line = tk.Button(master=self.buttons_frm,
                                           text="draw new",
                                           command=self.draw_new_line)
        self.btn_delete_line = tk.Button(master=self.buttons_frm,
                                         text='delete',
                                         command=self.delete_button_pressed)

        #position all elements

        #format self.buttons_frm
        self.btn_draw_new_line.grid(row=0,
                                    column=0,
                                    sticky='news')
        self.btn_delete_line.grid(row=0,
                                  column=1,
                                  sticky='news')
        self.buttons_frm.columnconfigure(0, weight=1)
        self.buttons_frm.columnconfigure(1, weight=1)

        #format self
        self.buttons_frm.pack(side='bottom',
                              fill="x")
        self.list_lines.pack(side="left",
                             fill=tk.BOTH,
                             expand=True)
        self.scrollbar.pack(side="left",
                            fill="y")


        #set attributes containing information about the application state
        self.active_line_index = None
        #index (within listbox) of currently active line

        #attribute with annotations object
        self.annotations = self.master.annotations

    def reset(self):
        """
        delete all current lines
        """
        self.list_lines.delete(0, tk.END)

    def load_lines(self):
        """
        Load the lines in self.list_lines
        """
        #delete all current lines
        self.list_lines.delete(0, tk.END)

        #load new/updated lines
        for confirmed, name in zip(self.annotations.confirmed, self.annotations.names):
            if confirmed:
                self.list_lines.insert(tk.END, name)

    def delete_line(self):
        """
        Delete a line
        """
        #this method may only be invoked if line_canvas is active from the
        #perspective of the annotation_canvas
        if not self.master.annotation_canvas.line_canvas_active:
            return

        if len(self.list_lines.curselection()) == 0:
            #if no lines are selected (or declared), no line may be deleted
            return

        self.list_lines.delete(self.list_lines.curselection()[0])
        self.annotations.delete_line(index=self.active_line_index)
        self.master.annotation_canvas.update_image(mode=0)

    def delete_button_pressed(self):
        """
        Actions which should be performed when the delet button is invoked
        """
        #activate line_canvas is active from the perspective of annotation_canvas
        self.master.annotation_canvas.line_canvas_active = True

        #if the button was invoked after a line was activated by selection of
        #some keypoint in the annotation canvas, firstly the method activate_line
        #should be executed.
        #if this is not the case, no changes will happen as a result of invoking
        #activate_line()
        self.activate_line()

        #delete line
        self.delete_line()

        #de-activate line_canvas is active from the perspective of annotation_canvas
        self.master.annotation_canvas.line_canvas_active = False

    def activate_line(self, list_index=None):
        """
        change active line
        """

        #set attribute, so annotation_canvas knows the line_canvas is currently
        #used
        self.master.annotation_canvas.line_canvas_active = True

        if list_index is None:
            current_selection = self.list_lines.curselection()
            if len(current_selection) > 0:
                self.active_line_index = current_selection[0]
        else:
            self.active_line_index = list_index

        if self.active_line_index is not None:
            self.master.annotation_canvas.update_active_line(line_id=self.active_line_index)

    def draw_new_line(self):
        """
        Start the drawing of a new line
        """
        self.active_line_index = None
        self.list_lines.select_clear(0, tk.END)
        self.master.annotation_canvas.new_line()

    def activate_next_line(self):
        """
        Activate the next line
        """
        if self.active_line_index is None:
            self.activate_line(list_index=0)
        else:
            list_index = (self.active_line_index + 1) % len(self.list_lines.get(0,tk.END))
            self.activate_line(list_index=list_index)

    def activate_previous_line(self):
        """
        Activate the previous line
        """
        if self.active_line_index is None:
            self.activate_line(list_index=0)
        else:
            list_index = (self.active_line_index - 1)  % len(self.list_lines.get(0,tk.END))
            self.activate_line(list_index=list_index)
