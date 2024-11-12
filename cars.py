#############################
#        Cars Module        #
#############################

import pygame

cars = {}

class Car:
    id = 0
    position = 0 #position normalisé 
    path = [] #liste des links ie trajet de la voiture
    naive_path = []
    step = 0 #étape de la voiture dans le trajet
    start = 0 #int, sommet de depart
    selfDrived = False
    way = True #True si la voiture roule de start à end et False sinon

    def __init__(self, id, selfDrived, start, path):
        self.id = id
        self.selfDrived = selfDrived
        self.path = path
        self.naive_path = self.path.copy()
        self.step = 0 
        self.start = start
        ilink = self.path[0]
        self.position = 0
        if start == ilink.start:
            self.way = True
            ilink.data['cars1'].append(self.id)
        else:
            self.way = False
            ilink.data['cars2'].append(self.id)
        
    def voie(self):
        if self.way:
            return('1')
        else:
            return('2')
    
    def reset_path(self):
        self.path = self.naive_path.copy()
    
    def set_pos(self, val):
        self.position = val
    
    def refreshPosition(self, dt, graphe):
        newPos = self.position*self.path[self.step].data['length'] + self.path[self.step].data['globalSpeed'+self.voie()]*dt # Diviser par 3.6 pour être réaliste
        if newPos > self.path[self.step].data['length']: # Changement d'arrête
            if self.selfDrived:
                if self.step + 1 < len(self.path):
                    self.refreshpath3(graphe, 6, 2)
                else:
                    removeCar(self.id)
                    return()
            if self.step + 1 < len(self.path):
                self.path[self.step].data['cars'+self.voie()].remove(self.id)
                newPos = newPos - self.path[self.step].data['length']
                reste_dt = newPos/self.path[self.step].data['globalSpeed'+self.voie()]
                if self.way:
                    self.way = (self.path[self.step].end == self.path[self.step + 1].start)
                else:
                    self.way = (self.path[self.step].start == self.path[self.step + 1].start)
                self.step += 1
                self.path[self.step].data['cars'+self.voie()].append(self.id)
                self.position = reste_dt*self.path[self.step].data['globalSpeed'+self.voie()]/self.path[self.step].data['length']
            else:
                removeCar(self.id)
                
        else:
            self.position = newPos/self.path[self.step].data['length']

    def reset_position(self):
        if self.id in cars:
            self.path[self.step].data['cars'+self.voie()].remove(self.id)
        self.step = 0
        ilink = self.path[0]
        self.position = 0
        if self.start == ilink.start:
            self.way = True
            ilink.data['cars1'].append(self.id)
        else:
            self.way = False
            ilink.data['cars2'].append(self.id)
    
    def set_selfDrived(self, val):
        self.selfDrived = val

    def refreshpath1(self, graphe):
        saved_path = self.path[:self.step+1]
        if self.way:
            if self.path[-1].end == self.path[-2].start or self.path[-1].end == self.path[-2].end:
                newpath = graphe.a_star(self.path[self.step].end,self.path[-1].start, False)
            else:
                newpath = graphe.a_star(self.path[self.step].end,self.path[-1].end, False)
        else:
            if self.path[-1].end == self.path[-2].start or self.path[-1].end == self.path[-2].end:
                newpath = graphe.a_star(self.path[self.step].start,self.path[-1].start, False)
            else:
                newpath = graphe.a_star(self.path[self.step].start,self.path[-1].end,False)
        self.path = saved_path + newpath[0]
    
    def refreshpath2(self, graphe):
        if self.way:
            way = (self.path[self.step].end == self.path[self.step + 1].start)
        else:
            way = (self.path[self.step].start == self.path[self.step + 1].start)
        if way: 
            voie = '1'
        else:
            voie = '2'
        self.path[self.step+1].refreshFunctionnal(voie, graphe)
        if not(self.path[self.step+1].data['functionnal'+voie]) :
            if self.path[-1].start == self.path[-2].start or self.path[-1].start == self.path[-2].end:
                if self.way :
                    newpath = graphe.a_star(self.path[self.step].end, self.path[-1].end,True)
                else :
                    newpath = graphe.a_star(self.path[self.step].start, self.path[-1].end,True)
            else :
                if self.way :
                    newpath = graphe.a_star(self.path[self.step].end, self.path[-1].start,True)
                else :
                    newpath = graphe.a_star(self.path[self.step].start, self.path[-1].start,True)
            if len(newpath[0]) != 0 :
                saved_path = self.path[:self.step+1]
                self.path = saved_path + newpath[0]

    def compare_score(self, new_path,r, ratio) :
        new_score = 0
        current_score = 0
        for link in self.path[self.step+1:self.step+r+1] :
            current_score+=link.data['length']
        for link in new_path :
            new_score+=link.data['length']
        if new_score <= ratio*current_score :
            return(True)
        else :
            return(False)

    def refreshpath3(self, graphe, r, ratio):
        if self.way:
            way = (self.path[self.step].end == self.path[self.step + 1].start)
        else:
            way = (self.path[self.step].start == self.path[self.step + 1].start)
        if way: 
            voie = '1'
        else:
            voie = '2'
        self.path[self.step+1].refreshFunctionnal(voie, graphe)
        if not(self.path[self.step+1].data['functionnal'+voie]) and self.step+r < len(self.path) :
            if self.path[self.step+r].start == self.path[self.step+r-1].start or self.path[self.step+r].start == self.path[self.step+r-1].end:
                if self.way :
                    newpath = graphe.a_star(self.path[self.step].end, self.path[self.step+r].end,True)
                else :
                    newpath = graphe.a_star(self.path[self.step].start, self.path[self.step+r].end,True)
            else :
                if self.way :
                    newpath = graphe.a_star(self.path[self.step].end, self.path[self.step+r].start,True)
                else :
                    newpath = graphe.a_star(self.path[self.step].start, self.path[self.step+r].start,True)
            if len(newpath[0]) != 0 and self.compare_score(newpath[0],r, ratio) :
                self.path = self.path[:self.step+1] + newpath[0] + self.path[self.step+r+1:]
              
    def display(self, screen, graphe, hide):
        t = self.position
        start = graphe.edges[self.path[self.step].start].position
        end = graphe.edges[self.path[self.step].end].position
        x,y=0.0,0.0
        if self.way:
            x = end[0]*t + (1-t)*start[0]
            y = end[1]*t + (1-t)*start[1]
        else:
            x = start[0]*t + (1-t)*end[0]
            y = start[1]*t + (1-t)*end[1]
        
        if not(hide):
            if self.selfDrived:
                pygame.draw.circle(screen, (0,0,255), (x,y), 3.0)
            else:
                pygame.draw.circle(screen, (0,255,0), (x,y), 3.0)

def resetcars(liste):
    global cars
    cars = liste.copy()

def addCar(car: Car):
    cars[car.id] = car

toDelete = []

def removeCar(id: int):
    toDelete.append(id)

def update():
    global toDelete
    if len(toDelete) > 0:
        for id in toDelete:
            cars[id].path[cars[id].step].data['cars'+cars[id].voie()].remove(id)
            del cars[id]
        toDelete = []