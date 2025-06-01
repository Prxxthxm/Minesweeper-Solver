import itertools
import random

over = False
changed = False
m, n = map(int, input("Enter the dimensions of the grid (rows columns): ").split())
mines = int(input("Enter the number of mines: "))
grid = [['?' for _ in range(n)] for _ in range(m)]

def read_grid():
    global over, mines, grid, changed
    mines = 0
    for i in range(m):
        row = input(f"Enter row {i + 1} (use '?' for unknown, '*' for flag), or 'X' if the game has ended: ")
        if row.strip().upper() == 'X':
            over = True
            return
        if len(row) != n:
            print(f"Row must have exactly {n} characters.")
            over = True
            return
        for j in range(n):
            grid[i][j] = row[j]
            if row[j] == '*': mines += 1
            changed = True

def click_cell(i, j):
    if(grid[i][j] != '?'): return    
    print(f"Click cell ({i + 1}, {j + 1}) and enter the updated grid: ") #Clicking a numbered cell unlocks all its neighbours if flagged neighbours match the number
    read_grid()

def flag_cell(i, j):
    global grid, changed, mines
    if(grid[i][j] != '?'): return
    print(f"Flag cell ({i + 1}, {j + 1})")
    grid[i][j] = '*'
    mines -= 1
    changed = True

def unknown_neighbours(i, j):
    count = 0
    for x in range(max(0, i - 1), min(m, i + 2)):
        for y in range(max(0, j - 1), min(n, j + 2)):
            if grid[x][y] == '?': count += 1
    return count

def flagged_neighbours(i, j):
    count = 0
    for x in range(max(0, i - 1), min(m, i + 2)):
        for y in range(max(0, j - 1), min(n, j + 2)):
            if grid[x][y] == '*': count += 1
    return count

def basic_neighbour_filter():
    global changed
    for i in range(m):
        for j in range(n):
            if not grid[i][j].isdigit() or int(grid[i][j]) == 0: continue
            elif int(grid[i][j]) == flagged_neighbours(i, j) and unknown_neighbours(i, j) > 0: click_cell(i, j)
            elif int(grid[i][j]) == flagged_neighbours(i, j) + unknown_neighbours(i, j) and unknown_neighbours(i, j) > 0:
                for x in range(max(0, i - 1), min(m, i + 2)):
                    for y in range(max(0, j - 1), min(n, j + 2)):
                        if grid[x][y] == '?': flag_cell(x, y)

def basic_overlap_filter():
    for i in range(m):
        for j in range(n):
            if not grid[i][j].isdigit() or int(grid[i][j]) == 0: continue
            num_a = int(grid[i][j]) - flagged_neighbours(i, j)
            if num_a == 0: continue
            unknowns_a = set()
            for x in range(max(0, i - 1), min(m, i + 2)):
                for y in range(max(0, j - 1), min(n, j + 2)):
                    if grid[x][y] == '?': unknowns_a.add((x, y))

            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    ni, nj = i + dx, j + dy
                    if 0 <= ni < m and 0 <= nj < n and (ni != i or nj != j):
                        if grid[ni][nj].isdigit():
                            num_b = int(grid[ni][nj]) - flagged_neighbours(ni, nj)
                            if num_b == 0: continue
                            unknowns_b = set()
                            for x in range(max(0, ni - 1), min(m, ni + 2)):
                                for y in range(max(0, nj - 1), min(n, nj + 2)):
                                    if grid[x][y] == '?': unknowns_b.add((x, y))
                            
                            if unknowns_a and unknowns_b and unknowns_a < unknowns_b:
                                diff = unknowns_b - unknowns_a
                                diff_num = num_b - num_a
                                if diff_num == 0:
                                    for (x, y) in diff: click_cell(x, y)
                                elif len(diff) == diff_num:
                                    for (x, y) in diff: flag_cell(x, y)

def constraint_propagation():
    constraints = []
    for i in range(m):
        for j in range(n):
            if not grid[i][j].isdigit() or int(grid[i][j]) == 0: continue
            unknowns = set()
            for x in range(max(0, i - 1), min(m, i + 2)):
                for y in range(max(0, j - 1), min(n, j + 2)):
                    if grid[x][y] == '?': unknowns.add((x, y))
            mines_left = int(grid[i][j]) - flagged_neighbours(i, j)
            if unknowns and mines_left >= 0: constraints.append((unknowns, mines_left))

    for i in range(len(constraints)):
        set_a, mines_a = constraints[i]
        for j in range(len(constraints)):
            if i == j: continue
            set_b, mines_b = constraints[j]
            if set_a < set_b:
                diff = set_b - set_a
                diff_mines = mines_b - mines_a
                if diff_mines == 0 and diff:
                    for (x, y) in diff: 
                        click_cell(x, y)
                        changed = True
                elif len(diff) == diff_mines and diff_mines > 0:
                    for (x, y) in diff: 
                        flag_cell(x, y)
                        changed = True

def collect_constraints_and_unknowns():
    constraints = []
    unknowns = set()
    for i in range(m):
        for j in range(n):
            if not grid[i][j].isdigit() or int(grid[i][j]) == 0: continue
            num = int(grid[i][j]) - flagged_neighbours(i, j)
            cells = {(x, y) for x in range(max(0, i - 1), min(m, i + 2)) for y in range(max(0, j - 1), min(n, j + 2)) if grid[x][y] == '?'}
            if cells:
                constraints.append((cells, num))
                unknowns |= cells
    return constraints, list(unknowns)

def monte_carlo_guess():
    constraints, unknowns = collect_constraints_and_unknowns()
    if not unknowns:
        unknowns = [(i, j) for i in range(m) for j in range(n) if grid[i][j] == '?']
        if not unknowns: return
        i, j = random.choice(unknowns)
        print(f"Guessing random cell ({i+1}, {j+1})")
        click_cell(i, j)
        return

    sample_count = 1000
    mine_counts = {cell: 0 for cell in unknowns}
    valid_samples = 0
    mines_left = min(len(unknowns), max(mines, 0))

    for _ in range(sample_count):
        mine_cells = set(random.sample(unknowns, mines_left))
        assignment = {cell: (1 if cell in mine_cells else 0) for cell in unknowns}
        if all(sum(assignment.get(cell, 0) for cell in cells) == num for cells, num in constraints):
            valid_samples += 1
            for cell in unknowns:
                if assignment[cell]: mine_counts[cell] += 1


    if valid_samples == 0:
        i, j = random.choice(unknowns)
        print(f"Guessing random cell ({i+1}, {j+1})")
        click_cell(i, j)
        return

    min_prob = 2
    best_cell = None
    for cell in unknowns:
        prob = mine_counts[cell] / valid_samples
        if prob < min_prob:
            min_prob = prob
            best_cell = cell

    i, j = best_cell
    print(f"Guessing least risky cell ({i+1}, {j+1}) with estimated mine probability {min_prob:.2%}")
    click_cell(i, j)

def constraint_brute_force():
    constraints, unknowns = collect_constraints_and_unknowns()
    if not unknowns: return

    if len(unknowns) > 20: 
        print("Too many unknowns, using Monte Carlo method instead.")
        monte_carlo_guess()
        return
    
    all_assignments = []
    for mines in itertools.product([0, 1], repeat=len(unknowns)):
        assignment = dict(zip(unknowns, mines))
        if all(sum(assignment.get(cell, 0) for cell in cells) == num for cells, num in constraints): all_assignments.append(assignment)

    if not all_assignments: return

    for cell in unknowns:
        mine_in_all = all(a[cell] == 1 for a in all_assignments)
        safe_in_all = all(a[cell] == 0 for a in all_assignments)
        if mine_in_all: flag_cell(*cell)
        elif safe_in_all: click_cell(*cell)

def solve_grid():    
    global over, changed 
    while not over:
        changed = False
        if all(grid[i][j] == '?' for i in range(m) for j in range(n)): 
            candidates = [(i, j) for i in range(max(0, m//2 - m//10), min(m, m//2 + m//10 + 1)) for j in range(max(0, n//2 - n//10), min(n, n//2 + n//10 + 1)) if grid[i][j] == '?']
            i, j = random.choice(candidates)
            click_cell(i, j)
        
        basic_neighbour_filter()
        basic_overlap_filter()
        if(not changed): constraint_propagation()
        if(not changed): constraint_brute_force()
        if(not changed): monte_carlo_guess()

        if(not any(grid[i][j] == '?' for i in range(m) for j in range(n))): over = True;        
    
solve_grid()