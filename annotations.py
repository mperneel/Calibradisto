# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 13:56:46 2023

@author: Maarten
"""
#%% packages
import json
import os
import numpy as np

#%%

class Annotations():
    """
    The Annotations class stores all annotation data and has several methods
    to modify the annotation data
    """

    def __init__(self):
        self.lines = []
        self.names = []
        self.confirmed = [] #confirmed lines may be shown in the object canvas

    def new_line(self):
        """
        Create a new line
        """
        self.lines.append(np.empty(shape=(0,2)))
        self.confirmed.append(False)

        if len(self.names) == 0:
            self.names.append("0")
        else:
            self.names.append(str(int(self.names[-1]) + 1))

    def delete_line(self, index=None):
        """
        Delete a line
        """
        #we use pop(), which is an in-place operator for lists
        self.lines.pop(index)
        self.names.pop(index)
        self.confirmed.pop(index)

    def remove_nan_objects(self):
        """
        Remove lines without points
        """

        #loop backwards since this is convenient for removing multiple lines
        #in a single loop
        for i, line in reversed(list(enumerate(self.lines))):
            if len(line) == 0:
                self.delete_line(index=i)

    def save(self, filename):
        """
        save annotations to .json file
        """

        #check inputs
        if ("." not in filename) or\
            (filename.split(".")[-1] != "json"):
            raise ValueError("Specified filename is invalid")

        #remove empty lines
        self.remove_nan_objects()

        #convert annotations to dictionary
        #the object 'names' are not saved
        lines_dict = {}
        i = -1
        for line in self.lines:
            i += 1
            lines_dict[str(i)] = line.round(2).tolist()

        with  open(filename, 'w') as f:
            #using a with structure closes the file automatically when the
            #body of the with structure is completed
            json.dump(lines_dict, f, indent=4)

    def import_annotations(self, filename):
        """
        import annotations
        """

        #check inputs
        if not os.path.exists(filename):
            raise ValueError(f"{filename} not found")

        #load annotations
        with open(filename) as f:
            lines_dict = json.load(f)

        i = -1
        for _, item in lines_dict.items():
            i += 1
            self.lines.append(np.array(item))
            self.names.append(str(i))
            self.confirmed.append(True)

        #remove lines without points
        self.remove_nan_objects()

    def confirm_all(self):
        """
        Confirm all objects
        """
        self.confirmed = [True] * len(self.confirmed)

    def reset(self):
        """
        Reset the annotations
        """
        self.lines = []
        self.names = []
        self.confirmed = []
