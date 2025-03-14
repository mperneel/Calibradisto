# -*- coding: utf-8 -*-
"""
Created on Fri Jul 23 13:05:13 2021

@author: Maarten

In this script, the AnnotationCanvas class is defined. AnnotationCanvas regulates
all modifications to the annotations
"""
#%% import packages
import os
import tkinter.messagebox as tkmessagebox
import tkinter.filedialog as tkfiledialog
import numpy as np
import cv2
from PIL import Image, ImageTk

from general_image_canvas import GeneralImageCanvas

#%%main code

class AnnotationCanvas(GeneralImageCanvas):
    """
    AnnotationCanvas shows the image with the annotations
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.master = master
        self.annotations = self.master.annotations
        self.settings = self.master.settings
        self.point_id = 0
        self.line_id = 0
        self.currently_saved = True
        self.new_point_created = False
        self.point_active = False #is there an active point?
        self.currently_saved = True #saved status

        self.image_name = None #image name
        self.image_inter_scale = 1.0 #scale of self.image_inter
        self.image = None #image matrix
        self.image_inter = None #intermediary image matrix
        #basic modifications to self.image are done once and then stored
        #in self.image_inter to speed up the code
        self.image_inter_1 = None
        self.image_shown = None #matrix with shown image

        self.point_active = False

        self.line_id_canvas_active = False

        self.bind("<Button-1>",
                  self.button_1)
        self.bind("<ButtonRelease-1>",
                  self.button_1_release)
        self.bind("<B1-Motion>",
                  self.motion_b1)

    def update_image(self, mode=0):
        """
        Update image

        mode : int
            0 : the image is constructed from scratch\n
            1 : the code starts from the rescaled image with all non-active
            lines drawn. This mode is used to redraw only the currently active line
        """

        if self.image_name is None:
            #no image is loaded
            #display nothing
            self.itemconfigure(self.image_photoimage, image=None)
            self._image_photoimage = None
            return

        #There is an image loaded

        #get image height and width
        image_height, image_width = self.image.shape[:2]

        #get scale and intercepts
        s = self.zoom_level
        dx = self.zoom_delta_x
        dy = self.zoom_delta_y

        #get annotations
        lines = self.annotations.lines

        #if scale of image has changed, update image in mode 0
        if self.image_inter_scale != s:
            mode = 0

        #rescale image
        if mode == 0:
            #resize self.image_inter according to scale s
            self.image_inter = cv2.resize(self.image,
                                          dsize=(int(image_width * s),
                                                 int(image_height * s)))
            self.image_inter_scale = s

        #draw non active lines
        if mode == 0:
            for i, line in enumerate(lines):
                if i != self.line_id:
                    #copy the coordinates of line
                    line = line.copy()

                    #compute coordinates on the scaled image
                    line *= s

                    #round coordinates and convert to integer
                    line = np.round(line,0).astype(int)

                    #to make sure no lines are drawn above points, firstly the lines are
                    #drawn and secondly the points are drawn

                    #draw line segments
                    for j in range(len(line) - 1):
                        start_point = line[j]
                        end_point = line[j + 1]
                        cv2.line(self.image_inter,
                                 start_point,
                                 end_point,
                                 color=(255,0,0),
                                 thickness=self.settings.linewidth)

                    #draw points
                    for j, point in enumerate(line):
                        cv2.circle(self.image_inter,
                                   point,
                                   radius=self.settings.point_size,
                                   color=(255,0,0),
                                   thickness=-1)

        #draw active line
        self.image_inter_1 = self.image_inter.copy()
        if mode in [0, 1]:
            i = self.line_id
            line = lines[i].copy()

            #compute coordinates on the scaled image
            line *= s

            #round coordinates and convert to integer
            line = np.round(line,0).astype(int)

            #to make sure no lines are drawn above points, firstly the lines are
            #drawn and secondly the points are drawn

            #draw line segments
            for j in range(len(line) - 1):
                start_point = line[j]
                end_point = line[j + 1]
                cv2.line(self.image_inter_1,
                         start_point,
                         end_point,
                         color=(255,255,0),
                         thickness=self.settings.linewidth)

            #draw points
            for j, point in enumerate(line):
                cv2.circle(self.image_inter_1,
                           point,
                           radius=self.settings.point_size,
                           color=(0,255,0),
                           thickness=-1)

        self.image_shown = self.image_inter_1.copy()

        #slice self.image_shown so slice fits in self
        uw = self.winfo_width()
        uh = self.winfo_height()
        if (self.image_shown.shape[1] > uw) or\
            (self.image_shown.shape[0] > uh):
            self.image_shown = self.image_shown[dy : dy + uh,
                                                dx: dx + uw,
                                                :]

        #show image
        image_shown = Image.fromarray(self.image_shown)
        image_shown = ImageTk.PhotoImage(image_shown)

        self.itemconfigure(self.image_photoimage, image=image_shown)
        self._image_photoimage = image_shown

    def open_image(self):
        """
        Open a dialog to choose an image to load
        """

        #ask for a filepath
        filepath = tkfiledialog.askopenfilename()

        #check if an actual filepath was given
        if filepath == "":
            return

        #close the currently opened image (if this is the case)
        if self.image_name is not None:
            self.close_image()

        #load the image (and annotations)
        self.load_image(filepath, full_path=True)

        #configure menus of master
        self.master.configure_menus()

    def load_image(self, filename, full_path=True):
        """
        Decisive method to load an image, together with it's annotations (if
        availabe)

        Parameters
        ----------
        filename : string
            DESCRIPTION.
        full_path : bool, optional
            DESCRIPTION. The default is True.
        """

        #set wdir and image_name
        if full_path is True:
            wdir, image_name = os.path.split(filename)
            self.wdir = wdir
            os.chdir(self.wdir)
        else: #full_path = False
            wdir = self.wdir
            image_name = filename

        #check if file is a valid image
        if (len(image_name.split(".")) > 1) and \
            image_name.split(".")[1] in ['jpg', 'png']:

            if self.currently_saved:
                #annotations are saved (or there is currently no image shown)
                self.image_name = image_name
                self.import_image()
            else:
                #there are currently unsaved changes in the annotations
                message = "do you want to save the annotation changes you made " +\
                          "for the current image?"
                answer = tkmessagebox.askyesnocancel("Save modifications",
                                                     message=message)
                if answer is True:
                    #Save changes
                    self.save()
                    self.image_name = image_name
                    self.import_image()
                elif answer is False:
                    #Discard changes
                    self.image_name = image_name
                    self.import_image()
                #else: #answer==None
                    #nothing has to be done
        else:
            #there was selected an object, but it was not a supported image
            tkmessagebox.showerror("Invalid file",
                                   "Only files with the extension .jpg or .png are supported")

    def import_image(self):
        """
        Executive method to import image and load annotations (if available)
        """
        #reset parameters
        self.reset_parameters()

        #Update title of application
        self.master.master.title("Calibradisto " + self.image_name)

        #import image
        image = cv2.imread(self.image_name)
        self.image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        #import annotations (if they exist)
        if self.image_name.split('.')[0] + '.json' in os.listdir():
            self.annotations.import_annotations(self.image_name.split('.')[0] + '.json')

        #Set initial zoom level
        self.reset_zoom_level()

        #Update image
        self.new_line()
        self.update_image(mode=0)

    def reset_parameters(self):
        """
        Reset attributes to their default value
        """
        self.zoom_level = 1.0
        self.zoom_delta_x = 0
        self.zoom_delta_y = 0
        self.mouse_x = 0
        self.mouse_y = 0
        self.image_inter_scale = 1.0

        self.image = None
        self.image_inter = None
        self.image_inter_1 = None
        self.image_shown = None

        self.line_id = 0
        self.point_id = 0

        self.currently_saved = True
        self.point_active = False

        self.image_photoimage = self.create_image(0, 0, anchor='nw')

    def save(self):
        """
        Save the annotations
        """
        #check if an image is loaded
        if self.image_name is None:
            return

        #remove NaN-objects
        self.annotations.remove_nan_objects()

        #save annotations
        filename = self.image_name.split(".")[0]
        self.annotations.save(filename + '.json')

        #set state of self.currently_saved to True
        self.currently_saved = True

    def new_point(self, event):
        """
        Create a point

        Parameters
        ----------
        event : tkinter.Event
            ButtonPress event at the position where a new point should be created
        """
        s = self.zoom_level

        x = (event.x + self.zoom_delta_x) / (s)
        y = (event.y + self.zoom_delta_y) / (s)

        self.annotations.lines[self.line_id] =\
            np.append(self.annotations.lines[self.line_id], [[x, y]], axis=0)
        self.point_id = len(self.annotations.lines[self.line_id]) - 1
        self.new_point_created = True

        #set state of self.currently_saved to False
        self.currently_saved = False

        #update image
        self.update_image(mode=1)

    def motion_b1(self, event):
        """
        Desicive method to move a point

        Parameters
        ----------
        event : tkinter.Event
            Motion event
        """
        if self.point_active or self.new_point_created:
            self.move_current_point(event)

    def move_current_point(self, event):
        """
        Executive method to move a point

        Parameters
        ----------
        event : tkinter.Event
            Motion event
        """

        s = self.zoom_level

        #update point coordinates
        x = (event.x + self.zoom_delta_x) / s
        y = (event.y + self.zoom_delta_y) /s
        self.annotations.lines[self.line_id][self.point_id,:] = [x, y]

        #set state of currently_saved to False
        self.currently_saved = False

        #update mouse positions
        self.mouse_x = event.x
        self.mouse_y = event.y

        #update the shown image
        self.update_image(mode=1)

    def button_1(self, event):
        """
        Decisive method to re-activate a point or draw a new point
        """
        #check if an image was loaded
        if self.image_name is None:
            return

        #get image coordinates
        s = self.zoom_level
        x = (event.x  + self.zoom_delta_x) / s
        y = (event.y  + self.zoom_delta_y) / s
        location = np.array([x, y])

        #set self.point_active to False
        #at the end of this method, self.point_active should again be True
        self.point_active = False

        if len(self.annotations.lines) > 0:
            for i, line in enumerate(self.annotations.lines):

                #check if line has points
                if len(line) == 0:
                    continue

                #check if a point should be reactivated

                #compute distances
                dist = np.sqrt(np.sum((line - location)**2, axis=1))

                #if distance is lower than treshold, reactivate point
                if min(dist) < self.settings.reactivation_sensitivity/s:
                    self.point_active = True
                    self.line_id = i
                    self.point_id = np.argmin(dist)

                    #update image
                    self.update_image(mode=0)


                #check if a line has to be split

                #check if line has at least 2 points
                if len(line) < 2:
                    continue

                #get norm vectors for all line segments
                A = line[:-1] #start points
                B = line[1:] #end points
                delta = B - A
                n = np.stack((delta[:,1], -1 * delta[:,0]), axis=1)

                #normalise norm vectors
                n /= np.sqrt(np.sum(n**2, axis=1)).reshape(-1,1)

                #check if point is possibly on a line
                for j, (n_j, A_j, B_j) in enumerate(zip(n, A, B)):
                    n_j = n_j.reshape(-1,1)
                    A_j = A_j.reshape(-1,1)
                    B_j = B_j.reshape(-1,1)

                    v = location.reshape(-1,1) - A_j
                    u = n_j

                    d = v.transpose().dot(u) / np.sqrt(u.transpose().dot(u))
                    d = np.abs(d)

                    if d > self.settings.reactivation_sensitivity/s:
                        #point is not on line
                        continue

                    #point is on line

                    #check if point is on the line segment, and not on the line
                    #but outside of the line segment
                    end_points = np.concatenate((A_j, B_j), axis=1)

                    if np.all(np.sum(location.reshape(-1,1) > end_points, axis=1) == 1) and\
                        np.all(np.sum(location.reshape(-1,1) < end_points, axis=1) == 1):
                        #point is on line segment
                        line = np.concatenate((line[:j+1,:],
                                               location.reshape(1,-1),
                                               line[j+1:,:]),
                                              axis=0)
                        self.annotations.lines[i] = line

                        self.point_active = True
                        self.line_id = i
                        self.point_id = j + 1

        if not self.point_active:
            self.new_point(event)
            self.point_active = True

        self.update_image(mode=0)

    def new_line(self):
        """
        Create a new object
        """
        #remove empty lines
        self.annotations.remove_nan_objects()

        #confirm all objects
        self.annotations.confirm_all()

        #add new line to annotations
        self.annotations.new_line()

        #update self.line_id and self.point_id
        self.line_id = len(self.annotations.lines) - 1
        self.point_id = None

        #no point is currently activated
        self.point_active = False

        #update object canvas
        self.master.object_canvas.load_lines()

        #update image
        self.update_image(mode=0)

    def delete_point(self):
        """
        Delete the currently activated point
        """
        if self.point_id is not None:
            #delete point
            self.annotations.lines[self.line_id] =\
                np.delete(self.annotations.lines[self.line_id],
                          self.point_id,
                          axis=0)

            #assign self.point_id to index of last point of line
            if len(self.annotations.lines[self.line_id]) > 0:
                self.point_id = len(self.annotations.lines[self.line_id]) - 1
                #self.point activated should be True
                self.point_active = True
            else:
                self.point_id = None
                #set self.point_active to False
                self.point_active = False


            #set state of self.currently_saved to False
            self.currently_saved = False

            #update image
            self.update_image(mode=1)

    def button_1_release(self, event):
        """
        Actions to take when left mouse button is released
        """

        #check if an image was loaded
        if self.image_name is None:
            return

        self.mouse_x = event.x
        self.mouse_y = event.y

        if self.new_point_created:
            self.new_point_created = False

    def delete_line(self, line_id=None):
        """
        Delete a line
        """
        if line_id is None:

            if self.point_active is False:
                #There is currently no point (and thus no object) selected
                tkmessagebox.showinfo("Delete object",
                                      "Select first a point of the line you " +\
                                          "want to delete")
            else: #self.line_id is not None:
                #There is currently a point (and thus also a line) selected
                if len(self.annotations.lines) > 1:
                    #delete line
                    self.annotations.delete_line(index=self.line_id)

        else: #line_id is not None:

            #set active objecty correctly
            self.update_active_line(line_id=line_id)

            #delete line
            self.annotations.delete_line(index=self.line_id)

        #the activated point (if present) is deleted, so there is no point
        #any more activated
        self.point_active = False

        #remove NaN objects
        self.annotations.remove_nan_objects()

        #set state of self.currently_saved to False
        self.currently_saved = False

        #initiate new object
        self.new_line()

        #update image
        self.update_image(mode=0)

    def close_image(self):
        """
        Close the current image
        """

        if self.currently_saved is False:
            #there are currently unsaved changes in the annotations
            message = "do you want to save the annotation changes you made " +\
                      "for the current image?"
            answer = tkmessagebox.askyesnocancel("Save modifications",
                                                 message=message)
            if answer is True:
                #Save changes
                self.save()

                #set state of self.currently_saved to True
                self.currently_saved = True

        #reset annotation_canvas
        self.reset_parameters()

        #reset annotations
        self.annotations.reset()

        #refresh object canvas
        self.master.object_canvas.load_lines()

        self.image_name = None
        self.image = None
        self.image_inter = None
        self.image_shown = None

        #update image
        self.update_image(mode=0)

    def update_active_line(self, line_id):
        """
        Change the currently active line
        """

        #set id of active object
        self.line_id = line_id #id of current object
        self.point_id = None

        self.update_image(mode=0)
