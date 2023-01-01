import random
from copy import deepcopy
from collections import deque
import pygame
import numpy as np
from math import *
from tkinter import *
from tkinter import messagebox
import win32gui
import sys

def front(win_name,windows):
    for i in windows:
        if i[1] == win_name:
            win32gui.ShowWindow(i[0],5)
            win32gui.SetForegroundWindow(i[0])
            break

class Cube:
    # 0 (top) 1,2,3,4 (NESW) 5 (bottom)
    def __init__(self) -> None:
        self.x = 0
        self.y = 0
        self.config = ['T','N','E','S','W','B']
        self.faces = [False]*6
        self.rotations = {
            'R':[0,2,5,4],
            'L': [0,4,5,2],
            'U': [0,1,5,3],
            'D': [0,3,5,1]
        }
        self.directions = {
            'R': [1,0],
            'L':[-1,0],
            'U':[0,-1],
            'D':[0,1]
        }
    def rotate(self,move) -> None:
        rot_faces = self.rotations[move]
        prev = self.faces[rot_faces[0]]
        for idx in rot_faces[1:]:
            self.faces[idx],prev = prev,self.faces[idx]
        self.faces[rot_faces[0]] = prev
        self.x += self.directions[move][0]
        self.y += self.directions[move][1]
    def __str__(self) -> str:
        return ', '.join([f'{self.config[idx]}: {self.faces[idx]}' for idx in range(len(self.faces))])

    def __hash__(self) -> int:
        cantor_encoding = ((self.x+self.y) * (self.x+self.y+1)) // 2 + self.y
        hash = 0
        for face in self.faces:
            hash = hash<<1 | int(face)
        return cantor_encoding ^ hash
class Board:
    # 0  1  2  3
    # 4  5  6  7
    # 8  9  10 11
    # 12 13 14 15
    def __init__(self) -> None:
        self.dims = [4,4]
        self.grid = [[False for _ in range(self.dims[0])] for _ in range(self.dims[1])]

    def reset(self) -> None:
        self.grid = [[False for _ in range(self.dims[0])] for _ in range(self.dims[1])]

    def shuffle(self) -> None:
        indices = random.sample(range(self.dims[0]*self.dims[1]),6)
        indices = [divmod(index, self.dims[0]) for index in indices]
        for index in indices:
            self.grid[index[0]][index[1]] = True
    
    def rotate_right(self,grid):
        return list(zip(*grid[::-1]))
    def rotate_left(self,grid):
        return self.rotate_right(self.rotate_right(self.rotate_right(grid)))
    def rotate_180(self,grid):
        return self.rotate_right(self.rotate_right(grid))
    def reflect_x(self,grid):
        return [row[::-1] for row in grid]
    def reflect_y(self,grid):
        return grid[::-1]

    def __str__(self) -> str:
        return '\n'.join([' '.join([str(int(elem)) for elem in line]) for line in self.grid])

    def encode_grid(self,grid):
        hash = 0
        for y in range(self.dims[0]):
            for x in range(self.dims[1]):
                hash = hash<<1 | int(grid[y][x])
        return hash
    def __hash__(self) -> int:
        return self.encode_grid(self.grid)
class Game:
    
    def __init__(self) -> None:
        self.cube = Cube()
        self.board = Board()
        self.board.shuffle()
        self.place_cube()
        self.moves = []
        self.best_moves = []

    def validate_move(self,move) -> bool:
        x = self.cube.x + self.cube.directions[move][0]
        y = self.cube.y + self.cube.directions[move][1]
        return x>=0 and y>=0 and x<self.board.dims[0] and y<self.board.dims[1]
    
    def place_cube(self):
        empty_coords = []
        for y in range(self.board.dims[0]):
            for x in range(self.board.dims[1]):
                if not self.board.grid[y][x]:
                    empty_coords.append([y,x])
        chosen_coords = random.sample(empty_coords,1)[0]
        self.cube.y = chosen_coords[0]
        self.cube.x = chosen_coords[1]
    
    def perfom_move(self,move) -> None:
        self.cube.rotate(move)
        self.board.grid[self.cube.y][self.cube.x],self.cube.faces[5] = self.cube.faces[5],self.board.grid[self.cube.y][self.cube.x]
        self.moves.append(move)

    def check_complete(self) -> None:
        for face in self.cube.faces:
            if not face:return False
        return True

    def __hash__(self) -> int:
        return self.board.__hash__()<<6 | self.cube.__hash__()

    def __eq__(self, __o: object) -> bool:
        return hash(self)==hash(__o)

    def solve(self) -> list:
        visited_states = set()
        state_queue = deque()
        self.moves = []
        self.best_moves = []
        state_queue.append(deepcopy(self))
        visited_states.add(state_queue[0])
        while state_queue:
            # print(len(state_queue))
            current_state = state_queue.popleft()
            for move in self.cube.directions:
                if current_state.validate_move(move):
                    temp_state = deepcopy(current_state)
                    temp_state.perfom_move(move)
                    if temp_state in visited_states:continue
                    if temp_state.check_complete(): 
                        self.best_moves = temp_state.moves
                        return temp_state.moves
                    state_queue.append(temp_state)
                    visited_states.add(temp_state)
        return None
    def __str__(self) -> str:
        return f'Board:\n{self.board}\nCube ({self.cube.x},{self.cube.y}):\n{self.cube}\n'

RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GREY = (180,180,180)
FPS=120
move_mapping = {'R':pygame.K_RIGHT,'L':pygame.K_LEFT,'U':pygame.K_UP,'D':pygame.K_DOWN}

class GameController:
    def __init__(self,screen,windows=[],scale=100,rotation_period=0) -> None:
        # Set up Pygame 
        self.screen = screen
        self.scale = scale
        self.windows = windows
        self.ox = (screen.get_width()-4*scale)//2
        self.oy = (screen.get_height()-4*scale)//2
        self.clock = pygame.time.Clock()
        
        # Set up game objects
        self.game = Game()
        self.solve_mode = False

        # Set up commands
        self.commands = {pygame.K_RIGHT:['R',self.move_right],pygame.K_LEFT:['L',self.move_left],pygame.K_UP:['U',self.move_up],pygame.K_DOWN:['D',self.move_down]}
        self.current_command = None
        self.position = [self.game.cube.x,self.game.cube.y]
        self.next_position = [self.game.cube.x,self.game.cube.y]

        # Set up static cube
        self.static_cube = []
        self.static_cube.append(np.reshape([0, 0, 1,1],(4,1)).astype('float64'))
        self.static_cube.append(np.reshape([1, 0, 1,1],(4,1)).astype('float64'))
        self.static_cube.append(np.reshape([1,  1, 1,1],(4,1)).astype('float64'))
        self.static_cube.append(np.reshape([0, 1, 1,1],(4,1)).astype('float64'))
        self.static_cube.append(np.reshape([0, 0, 0,1],(4,1)).astype('float64'))
        self.static_cube.append(np.reshape([1, 0, 0,1],(4,1)).astype('float64'))
        self.static_cube.append(np.reshape([1, 1, 0,1],(4,1)).astype('float64'))
        self.static_cube.append(np.reshape([0, 1, 0,1],(4,1)).astype('float64'))

        # Set up possible moves
        self.movements = {
            'R':[1,0,0],
            'L':[-1,0,0],
            'U':[0,-1,0],
            'D':[0,1,0]
        }

        # Current rotation angle
        self.angle = 0

        if rotation_period>0:
            self.angle_increment = (np.pi/2)/(FPS*rotation_period)
        else:
            # Angular speed (radian/second)
            self.angle_increment = 0.12
        # Shear ratio
        self.top_shear = 0.2
        
        # Set up faces in order: 0 (top) 1,2,3,4 (NESW) 5 (bottom)
        self.faces = []
        self.faces.append([0,1,2,3])
        for v in [4,5,6,3]:
            self.faces.append([v%4,(v+1) % 4,((v+1) % 4) + 4,v%4+4])
        self.faces.append([4,5,6,7])

    ## Rotation and transformation functions
    def rot_y(self,angle):
        return  np.array([
                    [cos(angle), 0, sin(angle)],
                    [0, 1, 0],
                    [-sin(angle), 0, cos(angle)],
                ])
    def rot_x(self,angle):
        return  np.array([
                    [1, 0, 0],
                    [0, cos(angle), -sin(angle)],
                    [0, sin(angle), cos(angle)],
                ])

    def transform(self,point,rotation=np.eye(3),translation=np.zeros((3,1))):
        translation = np.reshape(translation,(3,1))
        transformation = np.append(np.append(rotation,translation,axis=1),np.reshape([0,0,0,1],(1,4)),axis=0)
        return np.dot(transformation,point)

    def shear(self,point):
        point[0] = point[0]-point[2]*self.top_shear
        point[1] = point[1]-point[2]*self.top_shear
        return point

    ## Movement functions
    def move_left(self,point):
        return self.transform(point,self.rot_y(-self.angle))
    def move_right(self,point):
        return self.transform(self.transform(self.transform(point,translation=np.reshape(self.movements['L'],(3,1))),self.rot_y(self.angle)),translation=np.reshape(self.movements['R'],(3,1)))
    def move_up(self,point):
        return self.transform(point,self.rot_x(self.angle))
    def move_down(self,point):
        return self.transform(self.transform(self.transform(point,translation=np.reshape(self.movements['U'],(3,1))),self.rot_x(-self.angle)),translation=np.reshape(self.movements['D'],(3,1)))

    ## Drawing Functions
    def project_2d(self,point):
        return [point[0],point[1]]
    
    def connect_points(self,i, j, points):
        pygame.draw.line(
            self.screen, BLACK, (points[i][0], points[i][1]), (points[j][0], points[j][1]))

    def draw_grid(self):
        self.screen.fill(GREY)
        for y in range(4):
            for x in range(4):
                if self.game.board.grid[y][x]:
                    pygame.draw.polygon(self.screen, BLUE,[(self.ox+x*self.scale,self.oy+y*self.scale),(self.ox+(x+1)*self.ox,self.oy+y*self.scale),(self.ox+(x+1)*self.scale,self.oy+(y+1)*self.scale),(self.ox+x*self.scale,self.oy+(y+1)*self.scale)])
                else:
                    pygame.draw.polygon(self.screen, GREY,[(self.ox+x*self.scale,self.oy+y*self.scale),(self.ox+(x+1)*self.ox,self.oy+y*self.scale),(self.ox+(x+1)*self.scale,self.oy+(y+1)*self.scale),(self.ox+x*self.scale,self.oy+(y+1)*self.scale)])
                pygame.draw.polygon(self.screen, BLACK,[(self.ox+x*self.scale,self.oy+y*self.scale),(self.ox+(x+1)*self.ox,self.oy+y*self.scale),(self.ox+(x+1)*self.scale,self.oy+(y+1)*self.scale),(self.ox+x*self.scale,self.oy+(y+1)*self.scale)],width=1)

    def draw_cube(self):
        projected_points = []
        # print(self.static_cube)

        for point in self.static_cube:
            point = deepcopy(point)
            if self.current_command:
                point = self.commands[self.current_command][1](point)
            point = self.shear(point)
            point[0] += self.position[0]
            point[1] += self.position[1]
            projected2d = self.project_2d(point)
            x = int(projected2d[0] * self.scale) + self.ox
            y = int(projected2d[1] * self.scale) + self.oy
            projected_points.append([x,y])
            pygame.draw.circle(self.screen, RED, (x, y), 5)

        for p in range(4):
            self.connect_points(p, (p+1) % 4, projected_points)
            self.connect_points(p+4, ((p+1) % 4) + 4, projected_points)
            self.connect_points(p, (p+4), projected_points)

        for idx in range(len(self.game.cube.faces)):
            if self.game.cube.faces[idx]:
                face = [(projected_points[vertex][0],projected_points[vertex][1]) for vertex in self.faces[idx]]
                pygame.draw.polygon(self.screen, BLUE,face)
        
    def end_movement(self):
        self.position = self.next_position
        self.angle = 0
        self.game.perfom_move(self.commands[self.current_command][0])
        self.draw_grid()
        self.draw_cube()
        self.current_command = None

    def update(self):
        self.clock.tick(FPS)
        if self.current_command:self.angle+=self.angle_increment
        self.angle = self.angle%(np.pi/2)
        if 0<=90-np.rad2deg(self.angle)<=np.rad2deg(self.angle_increment):
            self.end_movement()
        else:
            self.draw_grid()
            self.draw_cube()
        pygame.display.update()

    def handle_commands(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if event.key == pygame.K_n:
                    return True
                if self.solve_mode:
                    if event.key == pygame.K_SPACE:
                        self.solve_mode=False
                        if self.current_command:
                            self.end_movement()
                else:
                    if event.key == pygame.K_s:
                        Tk().wm_withdraw()
                        if messagebox.askyesno('Hidden solve mode',message='Are you sure you want to start solve mode? (Press Space to stop at any point)'):
                            self.solve_mode=True
                            Tk().wm_withdraw()
                            messagebox.showinfo('Status','Solving. Please wait.')
                            self.game.solve()
                            print(self.game)
                            print(self.game.best_moves)
                            Tk().wm_withdraw()
                            messagebox.showinfo('Status','Done Solving!')
                            front("Cube Solver",self.windows)
                    if event.key in self.commands:
                        if self.current_command:
                            self.end_movement()
                        if self.game.validate_move(self.commands[event.key][0]):
                            self.current_command = event.key
                            self.next_position = [self.position[0]+self.movements[self.commands[self.current_command][0]][0],self.position[1]+self.movements[self.commands[self.current_command][0]][1]]
        
        if self.solve_mode and not self.current_command and self.game.best_moves:
            move = self.game.best_moves.pop(0)
            self.current_command = move_mapping[move]
            self.next_position = [self.position[0]+self.movements[move][0],self.position[1]+self.movements[move][1]]
        return False