# Common tools used for multiple algorithms
from math import sqrt
import os


class Node:
    """A single node on a map for readability"""

    def __init__(self, index, x, y):
        self.index = index
        self.x = x
        self.y = y


# Finds the distance between two nodes
def find_dist(node_a, node_b):
    """Finds the distance between two given points"""
    return sqrt((node_a.x - node_b.x) ** 2 +
                (node_a.y - node_b.y) ** 2)


class Tour:
    """A whole map. Contains the route, filename and variety of tools"""

    def __init__(self):
        self.route = []
        self._last_measured = []  # Updates whenever get_dist is used
        self._file_name = ""
        self._distance = -1

        self.run_time = 0
        self.date_solved = ""
        self.algorithm_name = ""
        self.comment = ""

    def __len__(self):
        """Overloads the len() function for readability"""
        return len(self.route)

    def find_nodes(self, file_name):
        """Imports all the nodes in the city"""
        # Make sure route is clear
        self.route.clear()
        # Get the file open

        self._file_name = file_name
        file_path = ''
        if os.path.isabs(self._file_name):
            file_path = self._file_name
        else:
            file_path = "TSP_EUC/" + self._file_name
        file = open(file_path, "r")
        # The coordinates always start on the 7th line so just skip to it
        for line in file:
            if "COMMENT" in line:
                self.comment = line[10:-1]
            elif "NODE_COORD_SECTION" in line:
                break

        # Find all the nodes
        for line in file:
            if "EOF" not in line:
                line = line.split()
                self.route.append(Node(float(line[0]), float(line[1]), float(line[2])))
            else:
                break

    def get_dist(self):
        """Finds the length of the tour"""
        # If its already found just return it
        if self.route == self._last_measured:
            return self._distance
        self._distance = 0
        for i in range(len(self.route) - 1):
            self._distance += find_dist(self.route[i], self.route[i + 1])
        # Return back to starting point
        self._distance += find_dist(self.route[-1], self.route[0])
        # Reset _last_measured
        self._last_measured = self.route.copy()
        return self._distance

    def print_map(self):
        """Prints the map in the specified format"""
        print(self._file_name)
        printed_points = []

        print("Tour Length: ", self.get_dist())
        print("Tour:")
        for point in self.route:
            if point.index in printed_points:
                # Announce there's a duplicate if one's found
                print("ERROR: Duplicate found", point.index)
            print(point.index)
            printed_points.append(point.index)
        print("-1")
        # Report any missing nodes
        for i in range(len(self.route)):
            if i + 1 not in printed_points:
                print("Node", i, "seems to be missing!")
