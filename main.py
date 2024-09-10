import random
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import numpy as np

class Flower:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.pollen = 100
        self.nectar = 100
        self.visited = False

class DockingStation:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.stored_pollen = 0
        self.stored_nectar = 0

class BeeDrone:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.pollen_cargo = 0
        self.nectar_cargo = 0
        self.max_cargo = 500
        self.speed = 1
        self.state = "seeking_flower"
        self.target = None

    def move(self, target_x, target_y, obstacles):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
       
        if distance <= self.speed:
            self.x, self.y = target_x, target_y
        else:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed

    def collect(self, flower):
        pollen_collected = min(flower.pollen, self.max_cargo - self.pollen_cargo)
        nectar_collected = min(flower.nectar, self.max_cargo - self.nectar_cargo)
       
        self.pollen_cargo += pollen_collected
        self.nectar_cargo += nectar_collected
        flower.pollen -= pollen_collected
        flower.nectar -= nectar_collected
        flower.visited = True

    def deposit(self, station):
        station.stored_pollen += self.pollen_cargo
        station.stored_nectar += self.nectar_cargo
        self.pollen_cargo = 0
        self.nectar_cargo = 0

class Simulation:
    def __init__(self, num_drones, num_flowers, num_stations):
        self.drones = [BeeDrone(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(num_drones)]
        self.flowers = [Flower(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(num_flowers)]
        self.stations = [DockingStation(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(num_stations)]

    def find_nearest_unvisited(self, x, y, objects):
        unvisited = [obj for obj in objects if isinstance(obj, Flower) and not obj.visited]
        if unvisited:
            return min(unvisited, key=lambda obj: math.sqrt((obj.x - x)**2 + (obj.y - y)**2))
        return None

    def find_nearest(self, x, y, objects):
        return min(objects, key=lambda obj: math.sqrt((obj.x - x)**2 + (obj.y - y)**2))

    def all_flowers_visited(self):
        return all(flower.visited for flower in self.flowers)

    def run_step(self):
        for drone in self.drones:
            if drone.state == "seeking_flower":
                if not drone.target or not isinstance(drone.target, Flower) or drone.target.visited:
                    drone.target = self.find_nearest_unvisited(drone.x, drone.y, self.flowers)
                    if not drone.target:
                        if self.all_flowers_visited():
                            drone.state = "returning"
                            drone.target = self.find_nearest(drone.x, drone.y, self.stations)
                        continue

                drone.move(drone.target.x, drone.target.y, self.drones)
                if math.isclose(drone.x, drone.target.x, abs_tol=0.5) and math.isclose(drone.y, drone.target.y, abs_tol=0.5):
                    drone.collect(drone.target)
                    drone.target = None
               
            elif drone.state == "returning":
                if not drone.target or not isinstance(drone.target, DockingStation):
                    drone.target = self.find_nearest(drone.x, drone.y, self.stations)
                drone.move(drone.target.x, drone.target.y, self.drones)
                if math.isclose(drone.x, drone.target.x, abs_tol=0.5) and math.isclose(drone.y, drone.target.y, abs_tol=0.5):
                    drone.deposit(drone.target)
                    drone.state = "seeking_flower"
                    drone.target = None
                    for flower in self.flowers:
                        flower.visited = False

    def visualize(self):
        root = tk.Tk()
        root.title("Bee Drone Simulation")

        fig, ax = plt.subplots(figsize=(8, 8))
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack()

        drone_scatter = ax.scatter([], [], c='yellow', marker='o', s=50, label='Drones')
        flower_scatter = ax.scatter([], [], c='red', marker='*', s=100, label='Flowers')
        visited_flower_scatter = ax.scatter([], [], c='green', marker='*', s=100, label='Visited Flowers')
        station_scatter = ax.scatter([], [], c='blue', marker='s', s=100, label='Docking Stations')

        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.legend()

        def update():
            self.run_step()
           
            # Update drones
            drone_positions = np.array([[drone.x, drone.y] for drone in self.drones])
            drone_scatter.set_offsets(drone_positions)
           
            # Update flowers
            unvisited_flowers = np.array([[flower.x, flower.y] for flower in self.flowers if not flower.visited])
            visited_flowers = np.array([[flower.x, flower.y] for flower in self.flowers if flower.visited])
           
            if len(unvisited_flowers) > 0:
                flower_scatter.set_offsets(unvisited_flowers)
            else:
                flower_scatter.set_offsets(np.empty((0, 2)))
           
            if len(visited_flowers) > 0:
                visited_flower_scatter.set_offsets(visited_flowers)
            else:
                visited_flower_scatter.set_offsets(np.empty((0, 2)))
           
            # Update stations
            station_positions = np.array([[station.x, station.y] for station in self.stations])
            station_scatter.set_offsets(station_positions)
           
            canvas.draw()
            root.after(50, update)

        def on_click(event):
            if event.button == 1:  # Left click
                new_flower = Flower(event.xdata, event.ydata)
                self.flowers.append(new_flower)
            elif event.button == 3:  # Right click
                self.stations.append(DockingStation(event.xdata, event.ydata))

        fig.canvas.mpl_connect('button_press_event', on_click)

        update()
        root.mainloop()

# Run the simulation
if __name__ == "__main__":
    sim = Simulation(num_drones=10, num_flowers=20, num_stations=3)
    sim.visualize()