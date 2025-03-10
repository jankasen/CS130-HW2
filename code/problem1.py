# Problem 1 Part 3 (c)
from z3 import *

n0 = Int('n0')
n1 = Int('n1')
n2 = Int('n2')

solver = Solver()

solver.add(n0 > 0, n1 > 0, n2 > 0)

if solver.check() == sat:
    model = solver.model()
    print("Satisfiable model:")
    print(model)
else:
    print("Unsatisfiable")