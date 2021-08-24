import random
n=3
##square =[[0 for x in range(n)] 
##            for y in range(n)]

from itertools import permutations

def magic_num(max_num,n):
    total = 0
    for i in range(1,max_num+1):
        total += i
    return total//n

max_num = n*n
global magic_number

magic_number = magic_num(max_num,n)

print("magic_num = ",magic_number)

# Generate all possible grids
r = range(1, max_num+1)
grids = permutations(r)



def _all_sums(grid):
    """Check that each row and column of the grid sums to magic_number"""
    return (_sum_is(grid, 0, 1, 2) and  # rows 
            _sum_is(grid, 3, 4, 5) and
            _sum_is(grid, 6, 7, 8) and
            _sum_is(grid, 0, 3, 6) and  # columns
            _sum_is(grid, 1, 4, 7) and
            _sum_is(grid, 2, 5, 8) and 
            _sum_is(grid, 0, 4, 8) and  # diagonals
            _sum_is(grid, 2, 4, 6))


def _sum_is(grid, a, b, c):
    global magic_number
    """Determine if the given 3 cells in the grid sum up to magic_number"""
    sum_ = grid[a] + grid[b] + grid[c]
    return sum_ == magic_number

def print_solutions(solutions):
    for s in solutions:
        print("\n")
        print('|' + '|' . join ( map ( str , s[: 3 ])) + '|')
        print('|' + '|' . join ( map ( str , s[3: 6 ])) + '|')
        print('|' + '|' . join ( map ( str , s[6:])) + '|')
        
solutions = [g for g in grids if _all_sums(g)]

print("solutions = ")
print_solutions(solutions)

print("num grids (9!)=",len(list(grids)))

