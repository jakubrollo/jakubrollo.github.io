import random
import clingo
from collections import defaultdict
import time


class SimpleClingo:
    """A simply usable Python binding to clingo. Provides easy-to-use methods for solving ASP programs."""
    def __init__(self):
        self.program_paths = []
        self.additional_clauses = []
        self.loading_time = 0
        self.grounding_time = 0
        self.solving_only_time = 0
        self.solving_time = 0
        self.n_ground_rules = 0

    def load_path(self, program_path):
        """Loads a program by given path. Multiple can be loaded and additional clauses added by add_clause."""
        self.program_paths.append(program_path)

    def add_clause(self, clause):
        """Adds a single clause by given text representation."""
        self.additional_clauses.append(clause)

    def reset(self):
        """Resets the program."""
        self.__init__()

    def solve(self, n_solutions=1, randomness=1.0, seed=None, suppress_warnings=False, verbose=False):
        """
        Solves the given ASP program. Randomness is a float 0.0 - 1.0, which determines how often a random
        assignment is picked rather than a heuristic one (1 = always, 0 = never).
        Therefore high randomness may reduce performance.
        """

        method_start = time.time()
        # =================
        #  Loading program
        # =================
        if seed is None:
            seed = random.randint(0, 2_147_483_647)
        args = ["--rand-freq={}".format(randomness), "--seed={}".format(seed), str(n_solutions)]
        if randomness > 0.9:
            # Helps the randomness a little bit
            args.append("--sign-def=rnd")
        if suppress_warnings:
            args += ["-Wno-atom-undefined", "-Wno-file-included", "-Wno-variable-unbounded", "-Wno-operation-undefined",
                     "-Wno-global-variable"]

        program = clingo.Control(args)

        for program_path in self.program_paths:
            program.load(program_path)

        for clause in self.additional_clauses:
            program.add('base', [], clause)

        loading_end = time.time()

        # ===================
        #  Grounding program
        # ===================
        program.ground([('base', [])])

        # Noting number of ground clauses
        stats = program.statistics['problem']['lpStep']
        self.n_ground_rules = int(stats['rules'] + stats['rules_tr'])

        if verbose:
            print("Program grounded to {} rules".format(self.n_ground_rules))
            print("Solving program, using heuristic in {:.2f}% of cases"
                  .format(100 * (1 - randomness)))

        grounding_end = time.time()

        # =================
        #  Solving program
        # =================
        models = []
        with program.solve(yield_=True) as handle:
            for m in handle:
                models.append(self.model_to_instantiation(m.symbols(atoms=True)))

        solving_end = time.time()
        self.__note_solving_time(method_start, loading_end, grounding_end, solving_end)

        if verbose:
            self.print_solving_time()

        return models

    def __note_solving_time(self, method_start, loading_end, grounding_end, solving_end):
        self.loading_time = loading_end - method_start
        self.grounding_time = grounding_end - loading_end
        self.solving_only_time = solving_end - grounding_end
        self.solving_time = solving_end - method_start

    def print_solving_time(self):
        """Prints time statistics of solving last program."""
        times = map(
            lambda x: "{:.2f}s".format(x) if x >= 0.1 else "{:.1f}ms".format(x * 1000),
            [self.solving_time, self.loading_time, self.grounding_time]
        )
        print("Solving took {} (of which loading {}, grounding {}))".format(*times))

    @staticmethod
    def model_to_instantiation(model):
        """Converts the clingo model to a dictionary. Nullary arguments are given the True value. Unary are modelled
        as lists of numbers. Others are modelled as lists of lists of arguments.

        All integers are converted from their string representations."""
        instantiation = defaultdict(list)
        for symbol in model:
            name = symbol.name
            if symbol.negative:
                name = '-' + name
            full_name = '{}/{}'.format(name, len(symbol.arguments))

            if len(symbol.arguments) == 0:
                # Null-ary symbol are modelled as True
                instantiation[name] = instantiation[full_name] = True
            elif len(symbol.arguments) == 1:
                # Unary symbols are modelled as lists of numbers
                val = list(map(SimpleClingo.int_if_possible, symbol.arguments))
                instantiation[name] += val
                instantiation[full_name] += val
            else:
                # (2+)-ary symbols are modelled as lists of lists of numbers
                val = list(map(SimpleClingo.int_if_possible, symbol.arguments))
                instantiation[name].append(val)
                instantiation[full_name].append(val)

        return instantiation

    @staticmethod
    def int_if_possible(s):
        try:
            return int(str(s))
        except (ValueError, TypeError):
            return str(s)
