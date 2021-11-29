from dataclasses import dataclass, field
import numpy as np

from typedef.pytypes import *
from typedef.obstacle_types import BasePolytopeObstacle

@dataclass
class VehicleBody(BasePolytopeObstacle):
    """
    Class to represent the body of a rectangular vehicle in the body frame
    
    verticies everywhere are computed with the assumption that 0 degrees has the vehicle pointing east.
    matrices are computed for 0 degrees, with the assumption that they are rotated by separate code.
    """
    
    # dimensions of the stock rover
    vehicle_flag: int = field(default = 0)  # for different types of vehicles
    # Wheelbase
    lf: float = field(default = 0)
    lr: float = field(default = 0)
    # Total Length and width
    l: float = field(default = 0)
    w : float = field(default = 0)
    h:  float = field(default = 0)

    # Wheel diameter and width
    wheel_d: float = field(default = 0.72)
    wheel_w: float = field(default = 0.22)
    
    def __post_init__(self):
        if self.vehicle_flag == 0:
            self.lr = 1.35
            self.lf = 1.35
            self.w = 1.85
            self.l = 4.6
        else:
            raise NotImplementedError('Unrecognized rover flag: %d'%self.vehicle_flag)
    
        self.__calc_V__()
        self.__calc_A_b__()
        return
        
    def __calc_V__(self):
        xy = np.array([[self.w/2, self.l/2],
                       [self.w/2, self.l/2],
                       [-self.w/2, self.l/2],
                       [-self.w/2, self.l/2],
                       [self.w/2, self.l/2]])
        
        V = xy[:-1,:]
                           
        object.__setattr__(self,'xy',xy)
        object.__setattr__(self,'V',V  )
        return
        
    def __calc_A_b__(self):
        A = np.array([[1,0],
                      [0,1],
                      [-1,0],
                      [0,-1]])
        
        b = np.array([self.l/2, self.w/2, self.l/2, self.w/2])
        object.__setattr__(self,'A',A)
        object.__setattr__(self,'b',b)
        return
    
    
    