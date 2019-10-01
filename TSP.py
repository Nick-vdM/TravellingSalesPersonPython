"""Implements Simulated Annealing. By Nick van der Merwe; s5151332 Griffith University student"""
import random
import sys
import time
from math import e
from math import log

import TSP_tools as tsp


def randomise(cities, start_time, max_time):
    """Calls shuffle on the cities"""
    random.shuffle(cities.route)
    return time.perf_counter() - start_time


def brute_force(cities, start_time, max_time):
    pass


def greedy(cities, start_time, max_time):
    unmapped = tsp.Tour()
    unmapped.route = cities.route.copy()
    cities.route.clear()

    start_index = random.randint(0, len(unmapped) - 1)
    cities.route.append(unmapped.route[start_index - 1])
    del unmapped.route[start_index - 1]

    while len(unmapped) > 0:
        best_dist = sys.maxsize
        best_index = 0
        for i in range(len(unmapped)):
            if tsp.find_dist(cities.route[len(cities) - 1], unmapped.route[i]) < best_dist:
                best_index = i
        cities.route.append(unmapped.route[best_index])
        del unmapped.route[best_index]

        if time.perf_counter() - start_time > max_time:
            return time.perf_counter() - start_time

    return time.perf_counter() - start_time


def two_opt(cities, start_time, max_time):
    """Executes the 2 opt algorithm on the input and returns a path"""
    # Randomise the order of the cities
    randomise(cities, start_time, max_time)
    last_length = sys.maxsize
    while last_length > cities.get_dist():
        last_length = cities.get_dist()
        for i in range(len(cities)):
            # Make sure the time isn't too long
            if time.perf_counter() - start_time > max_time:
                return time.perf_counter() - start_time
            for j in range(i + 1, len(cities) - 1):
                to_swap = [i, j]
                pre_dist = tsp.find_dist(cities.route[to_swap[0]], cities.route[to_swap[0] - 1]) + \
                           tsp.find_dist(cities.route[to_swap[1]], cities.route[to_swap[1] - 1])
                cities.route[to_swap[0]:to_swap[1]] = \
                    reversed(cities.route[to_swap[0]:to_swap[1]])
                post_dist = tsp.find_dist(cities.route[to_swap[0]], cities.route[to_swap[0] - 1]) + \
                            tsp.find_dist(cities.route[to_swap[1]], cities.route[to_swap[1] - 1])
                if post_dist > pre_dist:
                    cities.route[to_swap[0]:to_swap[1]] = \
                        reversed(cities.route[to_swap[0]:to_swap[1]])
    return time.perf_counter() - start_time


def simulated_annealing(cities, start_time, max_time):
    """Executes the anneal algorithm on the input and returns a path"""
    anneal_start = time.time()
    # Randomise the order of the cities
    random.seed(time.perf_counter())  # Keep it random
    random.shuffle(cities.route)
    # Variables to be used
    temperature = 0
    cooling = 0
    loops = 0
    CALC_VARS_AT = 1000  # What loop to calculate temp & cooling
    av_delta = 0  # Used for calculating initial temperature
    while time.perf_counter() - start_time < max_time:
        loops += 1

        # Pick a two random cities
        to_swap = [0, 0]
        while to_swap[0] == to_swap[1]:
            # Must be different and swap[0] < swap[1]
            to_swap = [random.randint(0, len(cities) - 1),
                       random.randint(to_swap[0], len(cities) - 1)]

        # Measure the space between them and the city behind them
        pre_dist = tsp.find_dist(cities.route[to_swap[0]], cities.route[to_swap[0] - 1]) + \
                   tsp.find_dist(cities.route[to_swap[1]], cities.route[to_swap[1] - 1])
        # Swap the edges
        cities.route[to_swap[0]:to_swap[1]] = \
            reversed(cities.route[to_swap[0]:to_swap[1]])

        # Measure it again and calculate delta
        post_dist = tsp.find_dist(cities.route[to_swap[0]], cities.route[to_swap[0] - 1]) + \
                    tsp.find_dist(cities.route[to_swap[1]], cities.route[to_swap[1] - 1])

        delta = (post_dist - pre_dist) / pre_dist
        # If its worse roll a chance to keep it
        if delta >= 0:
            random.seed(time.perf_counter())  # Keep it random
            roll = random.random()
            if temperature != 0.0:
                prob = e ** (-delta / temperature)
            else:
                # If temperature is 0, set 100% chance to swap
                prob = 0

            if roll > prob:
                # Swap it back if the chance failed
                cities.route[to_swap[0]:to_swap[1]] = \
                    reversed(cities.route[to_swap[0]:to_swap[1]])
        temperature *= cooling

        # On the 1000th loop set temperature & cooling
        av_delta += delta
        if loops == CALC_VARS_AT:
            # Estimate how many loops will be completed
            c_time = time.time()
            loops_per = CALC_VARS_AT / (c_time - anneal_start)
            est_total_loops = loops_per * (max_time - (c_time - anneal_start))

            multiplier = 2.1  # Used to find best number of iterations at the end
            while len(cities) ** multiplier > est_total_loops:
                # If there isn't enough time given, lower the multiplier so it still runs
                multiplier -= 0.05

            # Find av delta
            av_delta /= loops
            # Set initial chance to 30% to keep a bad swap
            temperature = -av_delta / log(0.3)
            # Reduce that to 1 / 10000 by the time that the square
            # of the number of nodes iterations remain
            T_k = (-av_delta / log(0.0001))
            cooling = (T_k / temperature) ** \
                      (1 / (est_total_loops - (len(cities) ** multiplier)))
    return max_time


if __name__ == "__main__":
    start_time = time.time()
    # Find the file
    anneal_path = tsp.Tour()
    anneal_path.find_nodes(sys.argv[1])

    # Find a route
    route = 0
    simulated_annealing(anneal_path, start_time, int(sys.argv[2]))

    anneal_path.print_map()
