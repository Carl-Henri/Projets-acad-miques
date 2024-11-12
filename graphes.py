############################
#      Graphes Module      #
############################

import pygame
import numpy as np
import os
import json

# Objet Edge (sommet)
class Edge:
    id = 0
    position = (0.0, 0.0)
    name = 'Sommet par défaut'
    data = {
        'color': (255,255,255)
    }

    def __init__(self, id, pos, name: str):
        self.id = id
        self.position = pos
        self.name = name
        self.data = {
            'color': (255,255,255),
            'selected': False,
            'accessibles': {},
            'reliés':{},
            'distances':{}
        }

# Object Link (arrêtes)
class Link:
    id = 0
    start = 0
    end = 0
    name = 'Arête par défaut'
    oneWay = 0 
    data = {
        'functionnal1': True,
        'functionnal2': True,
        'color': (255, 255, 255),
        'speedLimit': 0, # Limite de vitesse en km/h
        'carLimit': np.inf,
        'cars1': [],
        'cars2': [],
        'length': 0,
        'globalSpeed1': 0, # Pour l'idée de Enzo
        'globalSpeed2': 0,
        'score1': 0,
        'score2': 0
    }

    def __init__(self, id: int, name: str, start: int, end: int, oneWay: int):
        self.id = id
        self.start = start
        self.end = end
        self.name = name
        self.oneWay = oneWay
        self.data = {
            'functionnal1': True,
            'functionnal2': True,
            'color': (255, 255, 255),
            'speedLimit': 0, # Limite de vitesse en km/h
            'carLimit': np.inf,
            'cars1': [], #1 = sens direct (de start à end), 2 = sens opposé
            'cars2': [],
            'length': 0,
            'globalSpeed1': 0,
            'globalSpeed2': 0,
            'score1': 0,
            'score2': 0,
        }

    def refreshFunctionnal(self, voie, graphe):
        self.data['functionnal'+voie] = (self.data['globalSpeed'+voie]/self.data['speedLimit'] >= graphe.q)

    def isFunctionnal(self, graphe):
        self.refreshFunctionnal('1', graphe)
        self.refreshFunctionnal('2', graphe)
        return self.data['functionnal1'] and self.data['functionnal2']

    def refreshColor(self, graphe):
        if self.isFunctionnal(graphe):
            self.data.color = (0, 255, 0)
        else:
            self.data.color = (255, 0, 0)

    def refreshGlobalSpeed0(self, voie):
        if len(self.data['cars'+voie]) == 1:
            self.data['globalSpeed'+voie] = self.data["speedLimit"]
        else:
            self.data['globalSpeed'+voie] = min(self.data["speedLimit"],(10/6)*(self.data['length']/len(self.data['cars'+voie])))

    def refreshGlobalSpeed(self, cars, voie):
        if len(self.data['cars'+voie]) != 0:
            car = cars[self.data['cars'+voie][0]] #voiture en tête de file
            if car.step < len(car.path)-1: #on teste si la voiture n'est pas sur sa dernière arête 
                link = car.path[car.step+1] #l'arête que veut emprunter la voiture en tête de file
                if car.way:
                        way = (car.path[car.step].end == car.path[car.step + 1].start)
                else:
                        way = (car.path[car.step].start == car.path[car.step + 1].start)
                if way: 
                    voie2 = 'cars1'
                else: 
                    voie2 = 'cars2'
                if len(link.data[voie2]) >= link.data['carLimit']: #Si l'arête suivante est pleine, la vitesse globale est nulle
                    self.data['globalSpeed'+voie] = 0
                else:
                    self.refreshGlobalSpeed0(voie)
            else:
                self.refreshGlobalSpeed0(voie)
        else:
            self.data['globalSpeed'+voie] = self.data['speedLimit']
        
    def refreshScore(self, voie):
        if self.data['globalSpeed'+voie] != 0:
            self.data['score'+voie] = self.data['length']/self.data['globalSpeed'+voie]
        else:
            self.data['score'+voie] = 10**5
    
    def isfull(self, voie) :
        if len(self.data['cars'+voie]) > self.data['carLimit'] :
            return(True)
        else : 
            return(False)

# Objet Graphe
class Graphe:
    name = 'Graphe par défaut'
    edges = {}
    links = {}
    data = {}
    q = 0.5

    def __init__(self, name: str, data: dict):
        self.name = name
        self.data = data    

    def addEdge(self, edge: Edge):
        self.edges[edge.id] = edge

    def removeEdge(self, id: int):
        toDel = []
        for link in self.links.values():
            if link.start == id or link.end == id:
                toDel.append(link.id)
        for i in toDel:
            self.removeLink(i)
        del self.edges[id]

    def addLink(self, link: Link, length):
        # math.sqrt((self.edges[link.start].position[0] - self.edges[link.end].position[0])**2 + (self.edges[link.start].position[1] - self.edges[link.end].position[1])**2)
        link.data['length'] = length
        link.data['carLimit'] = link.data['length']/5
        self.links[link.id] = link
        if link.oneWay == 1:
            self.edges[link.start].data['accessibles'][link.end] = link
        else:
            self.edges[link.start].data['accessibles'][link.end] = link
            self.edges[link.end].data['accessibles'][link.start] = link
        self.edges[link.start].data['reliés'][link.end] = link
        self.edges[link.end].data['reliés'][link.start] = link
    
    def removeLink(self, id: int):
        start, end = self.links[id].start, self.links[id].end
        if end in self.edges[start].data['accessibles']:
            del self.edges[start].data['accessibles'][end]
        if start in self.edges[start].data['accessibles']:
            del self.edges[end].data['accessibles'][start]
        del self.links[id]

    def refreshSpeeds(self, cars):
        for link in self.links.values():
            link.refreshGlobalSpeed(cars,'1')
            link.refreshGlobalSpeed(cars,'2')
    
    def setq(self, value):
        self.q = value

    def voisines(self, start: Edge, end: Edge, test_fun): 
        if end.id in start.data['accessibles']:
            link = start.data['accessibles'][end.id]
            if link.start == start:
                voie = '1'
            else:
                voie = '2'
            link.refreshFunctionnal(voie, self)
            if link.data['functionnal'+voie] or not(test_fun) :
                link.refreshScore(voie)
                return(True, link.data['score'+voie], link)
        return(False, np.inf, None)

    def display(self, surface: pygame.surface, showQ: bool, font):
        for link in self.links.values():
            pygame.draw.line(surface, link.data['color'], self.edges[link.start].position, self.edges[link.end].position, 2)
            if showQ:
                (x,y) = ((self.edges[link.start].position[0]+self.edges[link.end].position[0])/2, (self.edges[link.start].position[1]+self.edges[link.end].position[1])/2 + 5)
                text = font.render(str(link.data['globalSpeed1']/link.data['speedLimit'])+" ; "+str(link.data['globalSpeed2']/link.data['speedLimit']), False, (255, 255, 255))
                surface.blit(text,(x,y))
        for edge in self.edges.values():
            pygame.draw.circle(surface, edge.data['color'], edge.position, 2.0)
    
    def distance(self,i,j) :
        u,v = self.edges[i], self.edges[j]
        return(((u.position[0]-v.position[0])**2 + (u.position[1]-v.position[1])**2)**1/2)
    
    def distances(self) :
        for i in self.edges.keys() :
            res = {j:self.distance(i,j) for j in self.edges.keys()}
            self.edges[i].data['distances'] = res

    def a_star(self, start: int, end: int, test_fun : bool):
        #renvoie path,score
        dic = dict([sommet, [np.inf, None, np.inf]] for sommet in self.edges.values())
        current_edge = self.edges[start]
        dic[self.edges[start]] = [0, None,self.edges[start].data['distances'][end]]
        dic_edges_unprocessed = dic.copy()
        while len(dic_edges_unprocessed) > 0 and self.edges[end] in dic_edges_unprocessed:
            for edge in dic_edges_unprocessed:
                voisines = self.voisines(current_edge,edge,test_fun)
                if voisines[0]:
                    if dic[edge][0] > dic[current_edge][0] + voisines[1]:
                        dic[edge][0] = dic[current_edge][0] + voisines[1]
                        dic[edge][2] = dic[edge][0] + edge.data['distances'][end]
                        dic[edge][1] = current_edge
            
            dic_edges_unprocessed.pop(current_edge)
            stop = True
            score_min = np.inf
            for edge in dic_edges_unprocessed:
                if dic[edge][2] < score_min:
                    score_min = dic[edge][2]
                    current_edge = edge
                    stop = False
            if stop:
                break

        edge = self.edges[end]
        path = [edge]
        if dic[edge][0] == np.inf:
            return([], np.inf)
        while edge != self.edges[start]:
            edge = path[0]
            path = [dic[edge][1]] + path

        N = len(path)
        liens = []
        for i in range(1,N-1):
            v = self.voisines(path[i], path[i+1], test_fun)
            if v[0]:
                liens.append(v[2])

        return(liens, dic[self.edges[end]][0])

    def full_Dijkstra(self, start: int, list_end):
        #renvoie path,score

        dic = dict([sommet, [np.inf, None]] for sommet in self.edges.values())

        current_edge = self.edges[start]
        dic[self.edges[start]] = [0, None]
        dic_edges_unprocessed = dic.copy()
        while len(dic_edges_unprocessed) > 0:
            for edge in dic_edges_unprocessed:
                voisines = self.voisines(current_edge,edge, False)
                if voisines[0]:
                    if dic[edge][0] > dic[current_edge][0] + voisines[1]:
                        dic[edge][0] = dic[current_edge][0] + voisines[1]
                        dic[edge][1] = current_edge
        
            dic_edges_unprocessed.pop(current_edge)
            stop = True
            duree_min = np.inf
            for edge in dic_edges_unprocessed:
                if dic[edge][0] < duree_min:
                    duree_min = dic[edge][0]
                    current_edge = edge
                    stop = False
            
            if stop:
                break
        liste_res = {}
        couple_relies = []
        for end in list_end:
            if end != start:
                edge = self.edges[end]
                if dic[edge][0] != np.inf:
                    path = [edge]
                    while edge != self.edges[start]:
                        edge = path[0]
                        path = [dic[edge][1]] + path

                    N = len(path)
                    liens = []
                    for i in range(1,N-1):
                        v = self.voisines(path[i], path[i+1], False)
                        if v[0]:
                            liens.append(v[2].id)
                    liste_res[str(end)] = liens
                    couple_relies.append((start,end))
        return(liste_res,couple_relies)
    
    def ways(self, map):
        if os.path.exists('ways/' + map + '.json'):
            file = open('ways/' + map + '.json')
            ways = json.load(file)
            return(ways)
        else:
            res = [{},[]]
            for i in self.edges.keys():
                dijkstra = self.full_Dijkstra(i, self.edges.keys())
                res[0][str(i)] = dijkstra[0]
                res[1] += dijkstra[1]
            dump = json.dumps(res)
            file = open('ways/' + map + '.json', "w")
            file.write(dump)
            file.close()
            return(res)
            
    def accessibles(self, start: Edge, functionnal):
            edges, links = [], []
            for edge_id,link in start.data['reliés'].items():
                if (not functionnal) or link.isFunctionnal(self):
                    links.append(link)
                    edges.append(self.edges[edge_id])
            return(edges, links)

    def resetColor(self):
        for sommet in self.edges.values():
            sommet.data['color'] = (255,255,255)
        for arrete in self.links.values():
            arrete.data['color'] = (255,255,255)
    
    def composantesConnexes(self, functionnal: bool):
        composantes = []
        n = 0
        for composante in composantes:
            n += len(composante[0])
        while n < len(self.edges.values()):
            restants = []
            for edge in self.edges.values():
                treated = False
                for composante in composantes:
                    if edge in composante[0]:
                        treated = True
                        break
                if not treated:
                    restants.append(edge)
                    break
                    
            départ = None
            parcourus = []
            liens = []
            while len(restants) > 0:
                départ = restants[0]
                restants.pop(0)
                (edges, links) = self.accessibles(départ, functionnal)
                for accessible in edges:
                    if accessible not in parcourus and accessible not in restants:
                        restants.append(accessible)
                for link in links:
                    if link not in liens:
                        liens.append(link)
                parcourus.append(départ)
            composantes.append([parcourus, liens])
            n = 0
            for composante in composantes:
                n += len(composante[0])
        return composantes
    
    def composantesConnexesDesc(self, n: int):
        composantes = self.composantesConnexes(True)
        desc = []
        while len(desc) < min(n, len(composantes)):
            max = 0
            biggest = None
            for composante in composantes:
                l = len(composante[1])
                if l >= max and (not composante in desc):
                    max = l
                    biggest = composante
            desc.append(biggest)
        return desc
    
    def refreshComposantesConnexes(self, number):
        print("Calcul des composantes connexes")
        self.resetColor()
        composantes = self.composantesConnexesDesc(number)
        colors = [(255,0,0), (255,135,0), (255, 211, 0), (222, 255, 10), (161, 255, 10), (10, 255, 153), (10, 239, 255), (20, 125, 245), (88, 10, 255), (190, 10, 255)]
        for i in range(len(composantes)):
            (sommets, arretes) = composantes[i]
            for sommet in sommets:
                sommet.data['color'] = colors[i]
            for arrete in arretes:
                arrete.data['color'] = colors[i]

    def spreadCars(self, cars):
        for link in self.links.values():
            n1 = len(link.data['cars1'])
            for i in range(n1):
                cars[link.data['cars1'][i]].set_pos(1 - (i+1)/n1)
            n2 = len(link.data['cars2'])
            for i in range(n2):
                cars[link.data['cars2'][i]].set_pos(1 - (i+1)/n2)

    def len_deux_cc(self):
        deux_cc = self.composantesConnexesDesc(2)
        if len(deux_cc) == 2:
            return(len(deux_cc[0][1]),len(deux_cc[1][1]))
        else:
            return(len(deux_cc[0][1]),0)
    