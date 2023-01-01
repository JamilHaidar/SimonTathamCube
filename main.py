import pygame
from tkinter import *
from tkinter import messagebox

from objects import GameController

import win32gui
windows = []
def windowEnumerationHandler(hwnd, windows):
    windows.append((hwnd, win32gui.GetWindowText(hwnd)))

WIDTH, HEIGHT = 600, 600
pygame.display.set_caption("Cube Solver")
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Allows focus back on game to automatically allow for inputs after Tkinter popup
# From: https://stackoverflow.com/questions/63395415/how-to-change-focus-to-pygame-window
win32gui.EnumWindows(windowEnumerationHandler, windows)

game_controller = GameController(screen,windows,rotation_period=0.2)

while True:
    if game_controller.handle_commands():
        game_controller = GameController(screen,rotation_period=0.2)
    game_controller.update()
    if game_controller.game.check_complete():
        Tk().wm_withdraw() #to hide the main window
        if messagebox.askyesno('Congratulations!',message='Complete!! Try again?'):
            game_controller = GameController(screen,rotation_period=0.2)
        else:
            break
pygame.quit()