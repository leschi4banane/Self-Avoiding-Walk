import os
import sys
import math
import time
import multiprocessing

SIZE: int = int(sys.argv[1])

found: set = set()

class Walker:
    def __init__(self, size: int, start: tuple) -> None:
        self.size = size

        self.neighbors = self.pre_calc_neighbors()

        self.path = [start]
        self.path_set = set(self.path)

        self.possibilities = []

        self.found = set()

    def get_neighbors(self, cords) -> list:
        x, y = cords
        size = self.size
        possible = ((x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y))
        return [pair for pair in possible if 0 <= pair[0] < size and 0 <= pair[1] < size]

    def pre_calc_neighbors(self) -> dict:
        neighbor_dict = {}
        for x in range(self.size):
            for y in range(self.size):
                neighbor_dict[(x, y)] = self.get_neighbors((x, y))
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

    
    def generate(self) -> int:
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
                    print(f"{self.path[0]} done")
                    return self.found
                
                new = self.possibilities[-1].pop()
                self.path.pop()
                self.path.append(new)
                continue

            new, other = neighbors
            self.path.append(new)
            self.possibilities.append(other)

def process_start_point(start_point, shared_dict):
    shared_dict[start_point] = Walker(SIZE, start_point).generate()

if __name__ == '__main__':
    start = time.time()

    processes = []
    manager = multiprocessing.Manager()
    return_dict = manager.dict()

    for x in range(math.ceil(SIZE/2)):
        for y in range(x + 1):
            if (x+y) % 2 == 1 and SIZE % 2 == 1:
                continue
            p = multiprocessing.Process(target=process_start_point, args=((x,y), return_dict))
            p.start()
            processes.append(p)
    
    print(f"Started {len(processes)} processes on {multiprocessing.cpu_count()} cores")

    for p in processes:
        p.join()

    for val in return_dict.values():
        found.update(val)
    
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