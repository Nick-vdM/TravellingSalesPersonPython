import os
import sqlite3
import sys
import time
from datetime import date

import TSP
import TSP_tools


class Database:

    def __init__(self):
        self.tour = TSP_tools.Tour()
        # TODO: Swap to connecting to dwarf.ict & put this as the exception
        self.connection = sqlite3.connect("tsp.db")
        self.cursor = self.connection.cursor()

        self.problem_solved = False
        self.problem_name = ""
        self.run_time = 0
        self.algorithm_name = ""

        self._create_database_if_not_exists()

    def _create_database_if_not_exists(self):
        create_map = """
            CREATE TABLE IF NOT EXISTS Maps
            (
              Name      VARCHAR(31) NOT NULL,
              NodeCount INTEGER     NOT NULL,
              CONSTRAINT pk PRIMARY KEY (Name)
            );


        """

        self.cursor.execute(create_map)

        create_cities = """
            CREATE TABLE IF NOT EXISTS Cities
            (
              MapName VARCHAR(31) NOT NULL,
              "Index" INTEGER     NOT NULL,
              x       DOUBLE      NOT NULL,
              y       DOUBLE      NOT NULL,

              CONSTRAINT MapName_FK FOREIGN KEY (MapName) REFERENCES Maps (Name),
              CONSTRAINT TourPoints_PK PRIMARY KEY (MapName, "Index")
            );
        """

        self.cursor.execute(create_cities)

        create_solutions = """
            CREATE TABLE IF NOT EXISTS Solutions
            (
              -- Column with type INTEGER PRIMARY KEY auto increments
              Identifier    INTEGER     NOT NULL,
              MapName       VARCHAR(31) NOT NULL,
              Distance      DOUBLE      NOT NULL,

              IndexOrder    VARCHAR     NOT NULL,

              RunTime       DOUBLE      NOT NULL,
              Author        VARCHAR(31),
              Date          DATE        NOT NULL,
              AlgorithmUsed VARCHAR(15) NOT NULL,

              CONSTRAINT Solutions_PK PRIMARY KEY (Identifier),
              CONSTRAINT MapName_FK FOREIGN KEY (MapName) REFERENCES Maps (Name)
            );
        """

        self.cursor.execute(create_solutions)

    def _problem_exists(self, problem_name):
        search = f"""
            SELECT Name
            FROM Maps
            WHERE Name = "{problem_name}"
        """
        self.cursor.execute(search)
        if self.cursor.fetchone():
            return True
        else:
            return False

    def add_problem(self, problem_name, file_name):
        if self._problem_exists(problem_name):
            print("ERROR: That problem name is taken!")
            return

        # Reuse find_nodes function instead of processing manually
        self.tour.find_nodes(file_name)
        insert_map = f"""
            INSERT INTO Maps (Name, NodeCount)
            VALUES ("{problem_name}",{len(self.tour)})
        """

        self.cursor.execute(insert_map)

        for node in self.tour.route:
            insert_point = f"""
                INSERT INTO Cities (MapName, "Index", x, y)
                VALUES ("{problem_name}", {node.index}, {node.x},{node.y})
            """

            self.cursor.execute(insert_point)
        print("Added " + problem_name + " successfully")

    def _save_tour_as_solution(self):
        if not self.problem_solved:
            return
        solution_string = ""
        for city in self.tour.route:
            solution_string = solution_string + (str(city.index) + " ")

        # Sometimes you can't access a user's computer name or username
        try:
            author = os.environ['COMPUTERNAME']
        except:
            try:
                author = os.environ['USER']
            except:
                author = "unknown"

        insert_solution = f"""
            INSERT INTO Solutions (MapName, Distance, IndexOrder, RunTime, Author, Date, AlgorithmUsed)
            VALUES ("{problem_name}", "{self.tour.get_dist()}", "{solution_string}","{self.run_time}",
            "{author}","{date.today()}","{self.algorithm_name}")
        """
        self.cursor.execute(insert_solution)

    def _load_in_problem(self, problem_name):
        if self.problem_name == problem_name and not self.problem_solved:
            return

        self.problem_solved = False
        self.problem_name = problem_name
        self.cursor.execute(f"""
            SELECT *
            FROM Cities 
            WHERE MapName = "{problem_name}"
        """)
        self.tour.route.clear()
        for r in self.cursor.fetchall():
            self.tour.route.append(TSP_tools.Node(r[1], r[2], r[3]))

    def solve(self, algorithm, problem_name, max_time):
        if not self._problem_exists(problem_name):
            print("That problem isn't in the database!")
            return
        self._load_in_problem(problem_name)
        self.algorithm_name = algorithm.__name__
        self.problem_solved = True
        self.run_time = algorithm(self.tour, time.perf_counter(), max_time)
        self._save_tour_as_solution()
        print("Solved " + problem_name + " successfully")

    def solution_made_before(self, problem_name):
        self.cursor.execute(f"SELECT * FROM Solutions WHERE MapName = '{problem_name}'")
        if self.cursor.fetchone():
            return True
        else:
            return False

    def _tour_from_solution_string(self, solution_string, problem_name):
        if problem_name != self.problem_name or self.problem_solved:
            # Reload the problem
            self._load_in_problem(problem_name)

        tour_solution = TSP_tools.Tour()
        for index in solution_string.split():
            tour_solution.route.append(self.tour.route[int(index) - 1])
        return tour_solution

    def fetch_all_solutions_to(self, problem_name):
        """Returns a list of tours"""
        # This isn't required in the assignment, but seems like it could be useful
        if self.problem_name != problem_name:
            self._load_in_problem(problem_name)
        if not self.solution_made_before(problem_name):
            print("That problem hasn't been solved yet")
            return
        solutions = []
        self.cursor.execute(f"""
            SELECT *
            FROM Solutions
            WHERE  MapName = "{problem_name}"
        """)
        for r in self.cursor.fetchall():
            new_solution = self._tour_from_solution_string(r[3], self.problem_name)
            new_solution._last_measured = new_solution.route.copy()
            new_solution._distance = r[1]
            new_solution.author = r[5]
            new_solution.date_solved = r[6]
            new_solution.algorithm_used = r[7]
            solutions.append(new_solution)
        return solutions

    def _load_in_solution_row(self, row):
        solution_string = row[3]
        problem_name = row[1]
        if self.problem_name != problem_name:
            self._load_in_problem(problem_name)
        self.tour = self._tour_from_solution_string(solution_string, problem_name)

        self.tour._last_measured = self.tour.route.copy()
        self.tour._file_name = row[1]  # Not actually the file name, but the closest thing the db stores
        self.tour._distance = row[2]
        self.tour.author = row[5]
        self.tour.date_solved = row[6]
        self.tour.algorithm_used = row[7]

    def fetch_solution(self, solution_number):
        # Not a necessary function, but could be useful
        self.cursor.execute(f"""
            SELECT *
            FROM Solutions
            WHERE Identifier = {solution_number}
        """)
        row = self.cursor.fetchone()
        if not row:
            print("ERROR: that problem ID doesn't exist")
            return
        self._load_in_solution_row(self, row)

    def fetch_best_solution(self, problem_name):
        if not self.solution_made_before(problem_name):
            print("That problem hasn't been solved yet")
            return

        self.cursor.execute(f"""
            SELECT *
            FROM Solutions
            WHERE MapName = '{problem_name}'
            AND Distance = (SELECT MIN(Distance) FROM Solutions WHERE MapName = '{problem_name}')
        """)
        row = self.cursor.fetchone()
        self._load_in_solution_row(row)

    def __del__(self):
        self.connection.commit()
        self.connection.close()


if __name__ == '__main__':
    start_time = time.perf_counter()
    db = Database()

    problem_name = sys.argv[1].lower()
    command = sys.argv[2].lower()
    if command == "add":
        file_name = sys.argv[3]
        db.add_problem(problem_name, file_name)
    elif command == "solve":
        # Assuming simulated annealing for now
        max_time = int(sys.argv[3])
        db.solve(TSP.simulated_annealing, problem_name, max_time)
    elif command == "fetch":
        # This command actually means fetch best solution
        db.fetch_best_solution(problem_name)
        # This isn't necessary but print it anyways to verify it works
        db.tour.print_map()
    elif command == "test":
        # hidden command that tests everything
        # syntax is <problem_name> TEST <file_name>
        file_name = sys.argv[3]
        db.add_problem(problem_name, file_name)
        # Run every algorithm 5 times
        for i in range(5):
            print("Starting algorithm loop #", i)
            db.solve(TSP.randomise, problem_name, 10)
            db.solve(TSP.greedy, problem_name, 10)
            db.solve(TSP.two_opt, problem_name, 10)
            db.solve(TSP.simulated_annealing, problem_name, 10)

        db.fetch_best_solution(problem_name)
        db.tour.print_map()
    else:
        print("Unknown command. Exiting")
