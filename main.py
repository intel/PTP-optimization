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
parser.add_argument("--pop_size", default=8, choices=range(1,9999), type=int, help="Initial population size", metavar="[1-9999]")
parser.add_argument("--epochs", default=10, choices=range(1,9999), type=int, help="Number of epochs", metavar="[1-9999]")
parser.add_argument("--max_kp", default=15, choices=Range(0.0,9999.0), type=float, help="Max value that is considered for Kp", metavar="[0.0-9999.0]")
parser.add_argument("--max_ki", default=15, choices=Range(0.0,9999.0), type=float, help="Max value that is considered for Ki", metavar="[0.0-9999.0]")
parser.add_argument("--num_random", default=2, choices=range(0,9999), type=int, help="Number of random parents added to each epoch", metavar="[0-9999]")
parser.add_argument("--num_inherited", default=5, choices=range(0,9999), type=int, help="Number of the best parents that are crossed to create a new generation", metavar="[0-9999]")
parser.add_argument("--num_replicated", default=4, choices=range(1,9999), type=int, help="Number of the best parents that are replicated to create a new generation", metavar="[1-9999]")
parser.add_argument("--mutation_coef", default=1, choices=range(0,9999), type=float, help="Mutation coefficient", metavar="[0-9999]")
parser.add_argument("--debug_level", default=1, choices=range(1,2), type=int, help="Debug level: 1 for basic; 2 for full logging", metavar="[1-2]")
parser.add_argument("--i", type=str, choices = adapterlist, help="Interface")
parser.add_argument("--t", default=120, choices=range(1,9999), type=int, help="-t from PTP script", metavar="[1-9999]")
parser.add_argument("--metric", default=1, choices=range(1,3), type=int, help="Metric type: 1 for MSE; 2 for RMSE; 3 for MAE", metavar="[1-3]")
parser.add_argument("--elite_size", default=1, choices=range(1,9999), type=int, help="Number of elite chromosoms", metavar="[1-9999]")

args = parser.parse_args()

#Debug levels
if args.debug_level == 1:
    debug_l1 = 1
    debug_l2 = 0

if args.debug_level == 2:
    debug_l1 = 1
    debug_l2 = 1

if debug_l2:
    print(args)

#Initial population
population = []
elite = []

if debug_l1:
    print("Creating initial population...")

for _ in range(args.pop_size):
    population.append(Creature(random.uniform(0, args.max_kp), random.uniform(0, args.max_ki))) #nosec

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

for epoch in range(args.epochs):
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
        parent.evaluate_data(args.debug_level, args.i, args.t, args.metric)
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
    for i in range(0,args.elite_size):
        index = sorted_scores_indexes[i]
        elite.append(population[index])
    elite.sort(key = lambda Creature: Creature.rating)

    for i in range(0, len(elite)):
        if i == args.elite_size:
            del elite[i:len(elite)]
            break

    #Create new generation
    new_generation = []

    #Crossing parents
    if debug_l1:
        print("Crossing parents...")
        x = 0
    for x in range(args.num_inherited):
        y = x + 1
        for _ in range(args.num_inherited - x - 1):
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
    for x in range(args.num_replicated):
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
    for _ in range(args.num_random):
        new_generation.append(Creature(random.uniform(0, args.max_kp), random.uniform(0, args.max_ki))) #nosec
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
        new_kp = creature.Kp + (rand_x * args.mutation_coef)
        new_kp = max(0, min(new_kp, args.max_kp))
        rand_y = random.uniform(-1, 1) #nosec
        new_ki = creature.Ki + (rand_y * args.mutation_coef)
        new_ki = max(0, min(new_ki, args.max_ki))
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
    epoch_progress = number_of_creatures * args.epochs
    print("***************************************************************")
    print("Progress: ", progress/epoch_progress * 100, "%")
    print("***************************************************************")
    #Switching generations
    population = new_generation

with open("log.log", "a") as f:
    f.write("\nElite:\n")
    os.chmod("log.log", 0o600)
    for creature in elite:
        f.write(f'{creature.Kp};{creature.Ki};{creature.rating}\n')

default = Creature(0.7,0.3)
default.evaluate_data(args.debug_level, args.i, args.t, args.metric)

with open("log.log", "a") as f:
    f.write("\nDefault setings:\n")
    f.write(f'{default.Kp};{default.Ki};{default.rating}\n')
