############################
#       Main Thread        #
############################

import pygame
import random
import sys
from pygame.locals import *
import numpy as np
import graphes
import map
import cars
import sliders
import utils
import monitor

# Paramètres
settings = {
    'display': {
        'size': (1400, 700)
    },
    'running': True,
    'presets': {
        'big': [1.428923, 1.455294, 43.594896, 43.609993],
        'small': [1.4349997182878251, 1.452471386959747, 43.59668731084423, 43.60246851152952]
    },
    'selected': 'big', # big/small
    'pause': True,
    'hide': False,
    'speed': 1.0,
    'composantesNumber': 3,
    'showQ': False
}
dt = 1/60

# Initialisation
if settings['running'] :
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode(settings['display']['size'])
    font = pygame.font.SysFont('Arial', 12)

# Création du graphe
minX, maxX, minY, maxY = settings['presets'][settings['selected']][0], settings['presets'][settings['selected']][1], settings['presets'][settings['selected']][2], settings['presets'][settings['selected']][3]
(sommets, liens) = map.getToulouse(minX, maxX, minY, maxY)
Toulouse = graphes.Graphe('Toulouse', {})

n = len(sommets)
N = len(liens)

for i in range(n):
    Toulouse.addEdge(graphes.Edge(i, (int(1/20*settings['display']['size'][0]+(sommets[i][0] - minX)/(maxX-minX)*settings['display']['size'][0]*9/10), int(settings['display']['size'][1]-(sommets[i][1] - 1/40*settings['display']['size'][1]+(sommets[i][1] - minY)/(maxY-minY)*settings['display']['size'][1]*9/10))), "test"))

for i in range(N):
    sensU = 0
    if liens[i][3]:
        sensU = 1
    link = graphes.Link(i, 'test', liens[i][0], liens[i][1], liens[i][3])
    link.data['color'] = (0, 255, 0)
    link.data['speedLimit'] = liens[i][2]
    link.data['oneWay'] = sensU
    if sensU == 1:
        link.data['color'] = (255, 0, 0)
    Toulouse.addLink(link, liens[i][4])

#Emondage du graphe initial
print("Calcul des composantes connexes")
composantes = Toulouse.composantesConnexes(False)
max = 0
for composante in composantes:
    l_composante = len(composante[1])
    if l_composante > max:
        premiere_comp = composante
        max = l_composante

print("Emondage du graphe")
edgeDel = []
linkDel = []
for edge in Toulouse.edges.values():
    if not(edge in premiere_comp[0]):
        edgeDel.append(edge)

for link in Toulouse.links.values():
    if not(link in premiere_comp[1]):
        linkDel.append(link)

for v in linkDel:
    Toulouse.removeLink(v.id)
for v in edgeDel:
    Toulouse.removeEdge(v.id)

#Génération des voitures
print("Génération des voitures")
p = 0
N = 1200
Na = 0
Nn = N - Na 
edges = list(Toulouse.edges.values())
ways = Toulouse.ways(settings['selected'])

for i in range(Nn):
    ok = False
    while not(ok) :
        (start,end) = random.choice(ways[1])
        start_link = Toulouse.links[ways[0][str(start)][str(end)][0]]
        if start_link.start == start :
            voie = '1'
        else :
            voie = '2'
        if not(start_link.isfull(voie)) :
            ok = True
        else :
            ways[1].remove([start,end])
    voiture = cars.Car(i, False, start, [Toulouse.links[k] for k in ways[0][str(start)][str(end)]])
    cars.addCar(voiture)

for i in range(Nn, N):
    ok = False
    while not(ok) :
        (start,end) = random.choice(ways[1])
        start_link = Toulouse.links[ways[0][str(start)][str(end)][0]]
        if start_link.start == start :
            voie = '1'
        else :
            voie = '2'
        if not(start_link.isfull(voie)) :
            ok = True
        else :
            ways[1].remove([start,end])
    voiture = cars.Car(i, True, start, [Toulouse.links[k] for k in ways[0][str(start)][str(end)]])
    cars.addCar(voiture)

Toulouse.spreadCars(cars.cars)

saved_cars = cars.cars.copy()

def set_p(val):
    global p
    n = len(saved_cars)
    p = val
    i = 0
    for voiture in saved_cars.values():
        if i < int(val*n):
            voiture.set_selfDrived(True)
        else:
            voiture.set_selfDrived(False)
        i+=1

print('Début de la simulation')
#Distances entre les sommets
Toulouse.distances()
# Sliders
sliders.sliders.append(sliders.Slider((0,1),Toulouse.setq,'q',Toulouse.q))
sliders.sliders.append(sliders.Slider((0,1),set_p,'p',p))
"""def setSpeed(speed):
    settings['speed'] = speed
sliders.sliders.append(sliders.Slider((0.5, 10.0), setSpeed, 'speed', settings['speed']))
"""
"""res = 0
for link in Toulouse.links.values() :
    if link.oneWay :
        res+=link.data['carLimit']
    else : 
        res+= 2*link.data['carLimit']
print(res)"""

Toulouse.setq(0.5)
#monitor.show_multiple_q0_evolution(int(sys.argv[2]),50,5,p,saved_cars,Toulouse,dt,True,True)
#monitor.show_q0_evolution(int(sys.argv[2]),int(int(sys.argv[2])/50),0,saved_cars,Toulouse,dt,False,True)
#monitor.show_selfdriving_cars(int(sys.argv[2]),7,0,saved_cars,Toulouse,dt,False,True)
time = 0
while settings['running']:
    # Fond noir
    screen.fill((0,0,0))

    # Event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                Toulouse.refreshComposantesConnexes(settings['composantesNumber'])
            elif event.key == pygame.K_p:
                settings['pause'] = not settings['pause']
            elif event.key == pygame.K_h:
                settings['hide'] = not settings['hide']
            elif event.key == pygame.K_a:
                saved_q = Toulouse.q
                q_list, tp_list, ts_list = np.linspace(0.01,1,50), [], []
                for q in q_list:
                    Toulouse.setq(q)
                    (tp,ts) = Toulouse.len_deux_cc()
                    tp_list.append(tp)
                    ts_list.append(ts)
                Toulouse.setq(saved_q)
                q0 = utils.calcul_q0(q_list,tp_list)
                monitor.show_percolation(q_list,tp_list,ts_list,q0)
            elif event.key == pygame.K_r:
                utils.reset_simulation(p, saved_cars, Toulouse)
                time = 0
            elif event.key == pygame.K_q:
                monitor.show_selfdriving_cars(time,3,p,saved_cars,Toulouse,dt,True,False)
            elif event.key == pygame.K_RIGHTPAREN:
                print(len(cars.cars))
            elif event.key == pygame.K_t:
                set_p(0)
            elif event.key == pygame.K_x:
                settings['showQ'] = not settings['showQ']
            elif event.key == pygame.K_g:
                print(time)
        elif event.type == MOUSEBUTTONDOWN:
            sliders.updateSliders(pygame.mouse.get_pos())            
    
    # Drawing Sliders
    for slider in sliders.sliders:
        slider.draw(screen, font)
    
    # Affichage du graphe
    Toulouse.display(screen, settings['showQ'], font)
    Toulouse.refreshSpeeds(cars.cars)

    # Affichage des voitures
    for car in cars.cars.values():
        car.display(screen, Toulouse, settings['hide'])
        if not(settings['pause']):
            car.refreshPosition(dt,Toulouse)
        if car.selfDrived :
            for link in car.path :
                link.data['color'] = (0,127,200)
    cars.update()

    for edge in Toulouse.edges.values() :
        edge.data['color'] = (0,0,0)
    
    if not(settings['pause']):
        time += 1
    pygame.display.flip()
    #pygame.time.wait(int(dt*1000))