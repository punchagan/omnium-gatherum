"""
Implements a small composer like the one in Nokia phones.  Just a
weekend hack.  Nothing serious, Really.
"""

from numpy import loadtxt, hstack, ones, zeros, zeros_like
import pygame
import pygame.mixer as mix

pygame.init()

ssp = zeros(3000)
mix.init(frequency=22050, size=-16, channels=2)

def parse_note(note):
    if note[:2].isdigit():
        l = int(note[:2])
        n = note[2:]
    else:
        l = int(note[:1])
        n = note[1:]

    if n[0] == '.':
        l = l/2*3
        n = n[1:]

    return l, n.upper()

def find_note(note):
    t, note = parse_note(note)
    n = notes[note]
    note = zeros((400*24)/t)
    if n > 0:
        note[:-100:n] = -0.2
    else:
        note[:-100:] = 0
    return note

def find_tune(tune):
    return mix.Sound(hstack([find_note(note) for note in tune]))

notes = {
    "#F1": 59,
    "G1": 56,
    "#G1": 53,    
    "A1": 50,
    "B1": 44,
    "C2": 42,
    "#C2": 39,
    "D2": 37,
    "#D2": 35,
    "E2": 33,
    "F2": 31,
    "#F2": 29,
    "G2": 28,
    "#G2": 26,
    "A2": 25,
    "#A2": 23,
    "B2": 22,
    "C3": 21,
    "-": 0
    }

jgm = "4C2 4D2 4E2 4E2 4E2 4E2 4E2 4E2 2E2 4E2 4E2 4D2 4E2 2F2 2E2 4E2 4E2 2D2 4D2 4d2 4b1 4d2 1c2 2c2 2g2 4g2 2g2 4g2 4g2 4g2 2g2 4g2 4g2 4f2 4a2 2g2 2F2 4f2 4f2 2e2 4e2 4e2 4d2 4f2 1e2 2e2 2E2 4e2 4e2 2e2 4e2 4e2 4g2 4g2 2g2 4f2 4f2 2f2 2e2 4e2 4e2 4d2 4d2 4d2 4d2 4b1 4d2 1c2 2c2 4C3 4b2 1c3 2c3 4b2 4a2 1b2 2b2 4a2 4g2 1a2 1a2 4c2 4c2 4d2 4d2 4e2 4e2 4d2 4e2 1f2" 

mytune = jgm
mytune = mytune.replace(',', ' ')
mytune = mytune.split()

if __name__ == "__main__":
    t = find_tune(mytune)
    t.play()
    pygame.event.wait()
