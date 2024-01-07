from itertools import count
from typing import List
from queue import PriorityQueue

import numpy as np

from parksim.route_planner.graph import Vertex, Edge, WaypointsGraph
from parksim.utils.spline import calc_spline_course

class AStarGraph(WaypointsGraph):
    """
    Graph with a* result
    """
    def __init__(self, path: List['Edge']):
        """
        docstring
        """
        self.edges = path

        if path == []:
            self.vertices = []
        else:
            self.vertices = [self.edges[0].v1]

            for e in self.edges:
                self.vertices.append(e.v2)

    def path_cost(self):
        """
        compute the cost along the planned path. Now computed as the sum of all edge costs
        """
        cost = 0
        for e in self.edges:
            cost += e.c

        return cost

    def plot(self, ax = None, plt_ops = {}):
        """
        plot the A* result
        """
        ax = super().plot(ax=ax, plt_ops=plt_ops)
        ax.plot(self.vertices[0].coords[0], self.vertices[0].coords[1], marker='s', markersize=4, mfc='none', **plt_ops)
        ax.plot(self.vertices[-1].coords[0], self.vertices[-1].coords[1], marker='x', markersize=4, mfc='none', **plt_ops)

        return ax

    def compute_ref_path(self, offset: float = 0):
        """
        Compute vehicle ref path with offset from the center line
        """
        # collect x, y, yaw from A* solution
        axs = []
        ays = []

        # calculate splines

        # generate list of x, y waypoints
        for v in self.vertices:
            axs.append(v.coords[0])
            ays.append(v.coords[1])

        cxs, cys, cyaws, _, _ = calc_spline_course(axs, ays, ds=0.1)
        cxs = [cxs[j] + offset * np.sin(cyaws[j]) for j in range(len(cxs))]
        cys = [cys[j] - offset * np.cos(cyaws[j]) for j in range(len(cys))]

        return cxs, cys, cyaws

class AStarPlanner(object):
    """
    A* planner for planning shortest path on the graph
    """
    def __init__(self, v_start: 'Vertex', v_goal: 'Vertex'):
        self.v_start = v_start
        self.v_goal = v_goal

        self.fringe = PriorityQueue()
        self.closed = set()
        
        # A counter object to prevent nodes with same cost
        self.counter = count()

        # (Vertex, Path, Cost-along-path)
        start = (self.v_start, [], 0)
        self.fringe.put((0, next(self.counter), start))

    def solve(self):
        """
        solve the path
        """
        while not self.fringe.empty():
            _, _, (v, path, cost) = self.fringe.get()

            if v == self.v_goal:
                # the returned path is a list of edges
                # print("Solved")
                return AStarGraph(path)
            
            if v not in self.closed:
                self.closed.add(v)

                for child, edge in zip(*v.get_children()):
                    new_cost = cost + edge.c
                    aStar_cost = new_cost + child.dist(self.v_goal)
                    new_node = (child, path + [edge], new_cost)
                    self.fringe.put((aStar_cost, next(self.counter), new_node))

        raise Exception('Path is not found')

    def solve_with_heading(self, heading: float = 0):
        """
        solve the path
        """
        while not self.fringe.empty():
            _, _, (v, path, cost) = self.fringe.get()
            # print("ost:",aStar_cost_)
            if v == self.v_goal:
                print((path + [edge])[0].v1.coords, (path + [edge])[0].v2.coords)

                # the returned path is a list of edges
                # print("Solved")
                return AStarGraph(path)
            if v not in self.closed:
                self.closed.add(v)

                for child, edge in zip(*v.get_children()):
                    if v == self.v_start:
                        path_vector = child.coords - self.v_start.coords
                        # print(child.coords)
                        heading_cost = np.fabs(heading - np.arctan2(path_vector[1], path_vector[0]))
                        if heading_cost > np.pi/2:
                            continue    

                    new_cost = cost + edge.c
                    aStar_cost = new_cost + child.dist(self.v_goal)
                    new_node = (child, path + [edge], new_cost)
                    self.fringe.put((aStar_cost, next(self.counter), new_node))

        raise Exception('Path is not found')