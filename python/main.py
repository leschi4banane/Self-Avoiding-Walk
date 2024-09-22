import os
import sys
import math
import time
from multiprocessing import Pool, cpu_count

SIZE: int = int(sys.argv[1])

class Walker:
    def __init__(self, size: int, start: tuple, path = []) -> None:
        self.size = size

        self.neighbors = self.preCalcNeighbors()

        if not path:
            self.path = [start]
        else:
            self.path = path
        self.path_set = set(self.path)
        
        self.possibilities = []

        self.found = set()
        
    def split(self) -> list:
        return [Walker(self.size, None, [self.path[-1], possibility]) for possibility in self.neighbors[self.path[-1]]]

    def getNeighbors(self, cords) -> list:
        x, y = cords
        size = self.size
        possible = ((x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y))
        return [pair for pair in possible if 0 <= pair[0] < size and 0 <= pair[1] < size]

    def preCalcNeighbors(self) -> dict:
        neighbor_dict = {}
        for x in range(self.size):
            for y in range(self.size):
                neighbor_dict[(x, y)] = self.getNeighbors((x, y))
        return neighbor_dict

    def choose_neighbor(self, cords) -> tuple:
        path_set = set(self.path)
        neighbor_options = [neighbor for neighbor in self.neighbors[cords] if neighbor not in path_set]
        return (neighbor_options[0], neighbor_options[1:]) if neighbor_options else None
    
    def choose_neighbor(self, cords) -> tuple:
        path_set = set(self.path)
        neighbor_options = [neighbor for neighbor in self.neighbors[cords] if neighbor not in path_set]
        if not neighbor_options:
            return None
        
        return neighbor_options[0], neighbor_options[1:]

    def generate(self) -> set:
        end_len = self.size * self.size
        while True:
            neighbors = self.choose_neighbor(self.path[-1])
            if not neighbors:
                if len(self.path) == end_len:
                    self.found.add(tuple(self.path))

                while self.possibilities and not self.possibilities[-1]:
                    self.path.pop()
                    self.possibilities.pop()

                if not self.possibilities:
                    print(".", end="", flush=True)
                    return self.found
                
                new = self.possibilities[-1].pop()
                self.path.pop()
                self.path.append(new)
                continue

            new, other = neighbors
            self.path.append(new)
            self.possibilities.append(other)

def split_processes(points):
    walkers = [Walker(SIZE, start_point) for start_point in points]
    
    new = []
    for walker in walkers:
        new.extend(walker.split())
        
    return new

def start_walker(walker):
    return  walker.generate()
    
def multicore_calc(points):
    
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(start_walker, points)
        pool.close()
        pool.join()
    return results

if __name__ == '__main__':
    start = time.time()

    start_points = []

    for x in range(math.ceil(SIZE/2)):
        for y in range(x + 1):
            if (x+y) % 2 == 1 and SIZE % 2 == 1:
                continue
            start_points.append((x, y))
    
    split_walkers = split_processes(start_points)
    
    print(f"Calculating {len(start_points)} starting points as {len(split_walkers)} split walkers on {cpu_count()} cores")
    found = set().union(*multicore_calc(split_walkers))
    print()

    for solution in set(found):
        found.add(tuple([(y, x) for x, y in solution]))

    for solution in set(found):
        found.add(tuple([(SIZE - x - 1, y) for x, y in solution]))
        found.add(tuple([(x, SIZE - y - 1) for x, y in solution]))
        found.add(tuple([(SIZE - x - 1, SIZE - y - 1) for x, y in solution]))

    print(f"Found {len(found)} solutions")
    print(f"Calculations took {time.time() - start:.5f} seconds")

    start = time.time()
    
    if not os.path.exists("out"):
        os.makedirs("out")

    with open(f'out/{SIZE}.txt', 'w') as file:
        for cords in found:
            file.write(f"{cords}\n")

    print(f"Saved to file in {time.time() - start:.5f} seconds")