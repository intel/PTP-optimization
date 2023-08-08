#!/usr/bin/python3
# Copyright (c) 2021 Intel
# Licensed under the GNU General Public License v2.0 or later (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     https://spdx.org/licenses/GPL-2.0-or-later.html

import random
import numpy
import subprocess #nosec
import shlex
import argparse
import os
import configureme as config
from evaluate import Creature

class Range():
    def __init__(self, start, end):
        self.start = start
        self.end = end
    def __eq__(self, other):
        return self.start <= other <= self.end
    def __contains__(self, item):
        return self.__eq__(item)
    def __iter__(self):
        yield self

#Validate interface
adapterlist = os.listdir('/sys/class/net/')
parser = argparse.ArgumentParser(description='Genetic algorithm for PID in PTP implementation')

#List of arguments
parser.add_argument("--i", type=str, choices = adapterlist, help="Interface")
parser.add_argument("--t", default=120, choices=range(1,9999), type=int, help="-t from PTP script", metavar="[1-9999]")
parser.add_argument("--metric", default=1, choices=range(1,3), type=int, help="Metric type: 1 for MSE; 2 for RMSE; 3 for MAE", metavar="[1-3]")

args = parser.parse_args()

#Debug levels
if config.debug_level == 1:
    debug_l1 = 1
    debug_l2 = 0
else:
    debug_l1 = 1
    debug_l2 = 1

if debug_l2:
    print(args)

#Initial population
population = []
elite = []

if debug_l1:
    print("Creating initial population...")

for _ in range(config.gen_population_size):
    population.append(Creature(random.uniform(0, config.gen_max_kp), random.uniform(0, config.gen_max_ki))) #nosec

if debug_l1:
    iter = 0
    if debug_l1:
        print("Initial population created!")
    if debug_l2:
        for creature in population:
            print("Creature", iter)
            print(creature.Kp)
            print(creature.Ki)
            iter = iter + 1

for epoch in range(config.gen_epochs):
    if debug_l1:
        print("***************************************************************")
        print("EPOCH NUMBER ", epoch)
        print("***************************************************************")

    score = []
    sorted_scores_indexes = []

    #Evaluate candidates
    i = 0
    for parent in population:
        if debug_l1:
            print("Evaluating creature number ", i)
        new_kp = round(parent.Kp,2)
        new_ki = round(parent.Ki,2)
        parent.mutate(new_kp, new_ki)
        parent.evaluate_data(config.debug_level, args.i, args.t, args.metric)
        score.append(parent.rating)
        i = i + 1

    if debug_l1:
        print("Score:  ", score)

    #Select candidates fo new generation
    sorted_scores_indexes = numpy.argsort(score)

    #Pick the best result and save it to the file
    index = sorted_scores_indexes[0]

    with open("log.log", "a") as f:
        f.write(f"{population[index].Kp};{population[index].Ki};{score[index]}\n")
        os.chmod("log.log", 0o600)

    if debug_l1:
        print("Sorted Scores indexes: ", sorted_scores_indexes)

    #Create Elite
    for i in range(0,config.gen_elite_size):
        index = sorted_scores_indexes[i]
        elite.append(population[index])
    elite.sort(key = lambda Creature: Creature.rating)

    for i in range(0, len(elite)):
        if i == cinfig.gen_elite_size:
            del elite[i:len(elite)]
            break

    #Create new generation
    new_generation = []

    #Crossing parents
    if debug_l1:
        print("Crossing parents...")
        x = 0
    for x in range(confg.gen_num_inherited):
        y = x + 1
        for _ in range(confug.gen_num_inherited - x - 1):
            if debug_l1:
                print(x, " + ", y)
            new_generation.append(
                Creature(population[sorted_scores_indexes[x]].Kp, population[sorted_scores_indexes[y]].Ki))
            new_generation.append(
                Creature(population[sorted_scores_indexes[y]].Kp, population[sorted_scores_indexes[x]].Ki))
            y = y + 1
        x = x + 1
    if debug_l1:
        print("New generation creation - crossed creatures added!")
    if debug_l2:
        iter = 0
        for creature in new_generation:
            print("New generation creature ", iter)
            print(creature.Kp)
            print(creature.Ki)
            iter = iter + 1

    new_generation_size = len(new_generation)

    #Replicating parents
    if debug_l1:
        print("Replicating parents...")
    for x in range(config.gen_num_replicated):
        new_generation.append(Creature(population[sorted_scores_indexes[x]].Kp, population[sorted_scores_indexes[x]].Ki))
    if debug_l1:
        print("New generation creation - replicated creatures added!")
    if debug_l2:
        iter2 = 0
        for creature in new_generation:
            if iter2 < new_generation_size:
                iter2 = iter2 + 1
                continue
            print("New generation creature ", iter2)
            print(creature.Kp)
            print(creature.Ki)
            iter2 = iter2 + 1
    new_generation_size = len(new_generation)

    #Adding randoms
    if debug_l1:
        print("Adding new random parents")
    for _ in range(config.gen_num_random):
        new_generation.append(Creature(random.uniform(0, config.gen_max_kp), random.uniform(0, config.gen_max_ki))) #nosec
    if debug_l1:
        print("New generation creation - random creatures added!")
    if debug_l2:
        iter2 = 0
        for creature in new_generation:
            if iter2 < new_generation_size:
                iter2 = iter2 + 1
                continue
            print("New generation creature ", iter2)
            print(creature.Kp)
            print(creature.Ki)
            iter2 = iter2 + 1

    #Mutation
    if debug_l1:
        print("Mutants are coming...")
    for creature in new_generation:
        rand_x = random.uniform(-1, 1) #nosec
        new_kp = creature.Kp + (rand_x * config.gen_mutation_coef)
        new_kp = max(0, min(new_kp, config.gen_max_kp))
        rand_y = random.uniform(-1, 1) #nosec
        new_ki = creature.Ki + (rand_y * config.gen_mutation_coef)
        new_ki = max(0, min(new_ki, config.gen_max_ki))
        creature.mutate(new_kp, new_ki)
    if debug_l1:
        print("Mutation finished!")
    if debug_l2:
        iter = 0
        for creature in new_generation:
            print("New generation creature ", iter)
            print(creature.Kp)
            print(creature.Ki)
            iter = iter + 1

    #Print information about progress
    number_of_creatures = len(new_generation)
    progress = number_of_creatures * (epoch + 1)
    epoch_progress = number_of_creatures * config.gen_epochs
    print("***************************************************************")
    print("Progress: ", progress/epoch_progress * 100, "%")
    print("***************************************************************")
    #Switching generations
    population = new_generation

with open("log.log", "a") as f:
    f.write("\nElite:\n")
    os.chmod("log.log", 0o600)
    for creature in elite:
        f.write(f"{population[index].Kp};{population[index].Ki};{score[index]}\n")

default = Creature(0.7,0.3)
default.evaluate_data(debug_level, args.i, args.t, args.metric)

with open("log.log", "a") as f:
    f.write("\nDefault setings:\n")
    f.write(f"{population[index].Kp};{population[index].Ki};{score[index]}\n")