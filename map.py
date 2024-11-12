############################
#        Map Module        #
############################

import json
import math

fV = open("filaire-de-voirie.json")
fS = open("sens-de-circulation.json")
f30 = open("zones-30.json")
fR = open("zones-de-rencontre.json")

voirieData = json.load(fV)
sensData = json.load(fS)
zone30Data = json.load(f30)
zoneRencontreData = json.load(fR)

liens = {}
sommets = {}

sommetId = -1
lienId = -1

def estNouveauSommet(pos):
    for sommet in sommets.values():
        if pos == sommet:
            return False
    return True

def nouveauSommet(pos):
    global sommetId
    sommetId += 1
    sommets[sommetId] = pos
    return sommetId

def getSommetId(pos):
    for i in range(len(sommets)):
        if sommets[i] == pos:
            return i
    
def nouveauLien(startId, endId, speed, oneWay, length):
    global lienId
    lienId += 1
    liens[lienId] = [startId, endId, speed, oneWay, length]

def estSelectionne(pos, minX, maxX, minY, maxY):
    if pos[0] > minX and pos[1] < maxY and pos[0] < maxX and pos[1] > minY:
        return True
    return False

zone20 = {}
zone30 = {}
sensUnique = {}
sensUniqueCoordonnees = {}

def distance(p1, p2):
    (x1,y1), (x2,y2) = p1, p2
    return math.sqrt((x2-x1)**2 + (y2-y1)**2)

def getToulouse(minX, maxX, minY, maxY):
    print("Chargement de la ville...")
    for zone in zoneRencontreData:
        zone20[(zone["id_seg_ges"], zone["codsti"])] = True
    for zone in zone30Data:
        zone30[(zone["id_seg_ges"], zone["codsti"])] = True
    for zone in sensData:
        sensUnique[(zone["id_seg_ges"], zone["codsti"])] = True
        sensUniqueCoordonnees[(zone["id_seg_ges"], zone["codsti"])] = (zone["geo_shape"]["geometry"]['coordinates'][0][0], zone["geo_shape"]["geometry"]['coordinates'][0][-1])

    for tronçon in voirieData:
        if 'geo_shape' in tronçon['fields'].keys():
            start = tronçon['fields']['geo_shape']['coordinates'][0][0]
            end = tronçon['fields']['geo_shape']['coordinates'][0][-1]
            id_seg_ges = tronçon['fields']['id_troncon']
            codsti = str(tronçon['fields']['codsti']).replace(" ", "")
            sensU = False
            if (id_seg_ges, codsti) in sensUnique:
                sensU = True
                (startReal, endReal) = sensUniqueCoordonnees[(id_seg_ges, codsti)]
                if distance(startReal, start) > distance(endReal, start):
                    start, end = end, start

            if (estSelectionne(start, minX, maxX, minY, maxY) and estSelectionne(end, minX, maxX, minY, maxY)):
                if estNouveauSommet(start):
                    nouveauSommet(start)
                if estNouveauSommet(end):
                    nouveauSommet(end)

                startId = getSommetId(start)
                endId = getSommetId(end)

                speed = 50
                if (id_seg_ges, codsti) in zone20:
                    speed = 20
                elif (id_seg_ges, codsti) in zone30:
                    speed = 30
                
                length = tronçon['fields']['longueur']

                nouveauLien(startId, endId, speed, sensU, length)
    return (sommets, liens)