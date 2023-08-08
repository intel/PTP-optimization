#!/usr/bin/python3
# Copyright (c) 2021 Intel
# Licensed under the GNU General Public License v2.0 or later (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     https://spdx.org/licenses/GPL-2.0-or-later.html

import random
import numpy
import subprocess #nosec
from shlex import split
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
import sys
import configureme as config

Rating_table = []
Checked_data = []
Master_offset = []

class Creature():
    rating = 0

    def __init__(self, Kp, Ki):
        self.Kp = Kp
        self.Ki = Ki
        rating = 0

    def mutate(self, new_Kp, new_Ki):
        self.Kp = new_Kp
        self.Ki = new_Ki

    #Evaluate data using one of three metrics - MSE, RMSE, MAE
    def evaluate_data(self, interface, t, metric):

        #Check if provided Kp and Ki are not repeated
        repeated_data = self.validate_data()
        if(repeated_data == 0):
            print("Correct data!")
            try:
                subprocess.check_call(split('./test-phc2sys.sh -s %s -c CLOCK_REALTIME -P %s -I %s -t %s' % (str(interface), str(self.Kp), str(self.Ki), str(t)))) #nosec
            except subprocess.SubprocessError:
                print("Error calling phc2sys")
                sys.exit()
            self.get_data_from_file()

            i = 0
            if config.debug_level != 1:
                for i in enumerate(Master_offset):
                    print(Master_offset[i])

            stripped_Master_offset = Master_offset[2::]

            if config.debug_level != 1:
                for i in range(len(stripped_Master_offset)):
                    print(stripped_Master_offset[i])

            #Calculate MSE
            if(metric==1):
                if config.debug_level != 1:
                    print("Choosen metric: MSE")
                rating = rate_data_MSE(stripped_Master_offset)
            #Calculate RMSE
            elif(metric==2):
                if configdebug_level != 1:
                    print("Choosen metric: RMSE")
                rating = rate_data_RMSE(stripped_Master_offset)
            #Calculate MAE
            elif(metric==3):
                if config.debug_level != 1:
                    print("Choosen metric: MAE")
                rating = rate_data_MAE(stripped_Master_offset)

            Rating_table.append(rating)
        #If Kp and Ki are repeated, return previously calculated rating
        else:
            print("Evaluate.py: Incorrect data!")
            rating = Rating_table[repeated_data - 1]

        self.rating = rating

    #Validate Kp and Ki
    def validate_data(self):
        if(len(Checked_data) > 0):
            iter = 1
            for creature in Checked_data:
                if(creature.Kp == self.Kp and creature.Ki == self.Ki):
                    return iter
                iter = iter + 1

        Checked_data.append(Creature(self.Kp, self.Ki))
        if config.debug_level != 1:
            print("Number of already checked data: ", len(Checked_data))
        return 0

    #Get master offset from file
    def get_data_from_file(self):
        Master_offset.clear()
        file_name = "phc2sys_P%s_I%s/phc2sys_P%s_I%s.log" % (str(self.Kp), str(self.Ki), str(self.Kp), str(self.Ki))
        with open(file_name, 'r') as read_file:
            for line in read_file:
                splitted = line.split()
                Master_offset.append(splitted[4])

        return Master_offset

#Calculate MSE
def rate_data_MSE(data):
    arr = [0 for i in range(len(data))]

    array1 = list(map(float, arr))
    array2 = list(map(int, data))
    MSE = mean_squared_error(array1, array2)
    print("MSE: ", MSE)

    return MSE

#Calculate RMSE
def rate_data_RMSE(data):
    arr = [0 for i in range(len(data))]

    array1 = list(map(float, arr))
    array2 = list(map(int, data))
    RMSE = mean_squared_error(array1, array2, squared=False)
    print("RMSE: ", RMSE)

    return RMSE

#Calculate MAE
def rate_data_MAE(data):
    arr = [0 for i in range(len(data))]

    array1 = list(map(float, arr))
    array2 = list(map(int, data))
    MAE = mean_absolute_error(array1, array2)
    print("MAE: ", MAE)

    return MAE