############################
#       Utils Module       #
############################

import numpy as np
import cars as c

def derive(x_list,y_list):
    d_list = []
    for i in range(1,len(x_list)):
        d_list.append((y_list[i] - y_list[i-1])/(x_list[i]-x_list[i-1]))
    return(d_list)

def calcul_q0(x_list,y_list):
    d = derive(x_list,y_list)
    i = d.index(min(d))+1
    q0 = (x_list[i] + x_list[i-1])/2
    return(q0)

def reset_simulation(p, saved_cars, graphe) :
    for car in saved_cars.values(): 
        car.reset_position()
    c.resetcars(saved_cars)
    graphe.spreadCars(c.cars)
    n = len(c.cars)
    i = 0
    for voiture in c.cars.values():
        if i < int(p*n):
            voiture.set_selfDrived(True)
        else: 
            voiture.set_selfDrived(False)
            voiture.reset_path()
        i += 1

def simulation(time,p,saved_cars,graphe,dt,reset) :
    if reset :
        reset_simulation(p,saved_cars,graphe)
    for i in range(time):
        graphe.refreshSpeeds(c.cars)
        for car in c.cars.values():
            car.refreshPosition(dt,graphe)
        c.update()

def simulation_percolation(time,p,saved_cars,graphe,dt,reset) :
    simulation(time,p,saved_cars,graphe,dt,reset)
    saved_q = graphe.q
    q_list = np.linspace(0.01,1,50)
    tp_list = []
    ts_list = []
    for q in q_list:
        graphe.setq(q)
        (tp,ts) = graphe.len_deux_cc()
        tp_list.append(tp)
        ts_list.append(ts)
    graphe.setq(saved_q)
    q0 = calcul_q0(q_list,tp_list)
    return(q0,q_list,tp_list,ts_list)

def simulation_q0_evolution(t_ref,n,p, saved_cars, graphe, dt, reset) :
    if reset :
        reset_simulation(p,saved_cars,graphe)
    time_list = [int(i) for i in np.linspace(0,t_ref,n)]
    q0_list = []
    q_list = np.linspace(0.01,1,50)
    for i in range(t_ref+1):
        for car in c.cars.values():
            car.refreshPosition(dt,graphe)
        graphe.refreshSpeeds(c.cars)
        c.update()
        if i in time_list :
            saved_q = graphe.q
            tp_list = []
            ts_list = []
            for q in q_list:
                graphe.setq(q)
                (tp,ts) = graphe.len_deux_cc()
                tp_list.append(tp)
                ts_list.append(ts)
            graphe.setq(saved_q)
            q0 = calcul_q0(q_list,tp_list)
            q0_list.append(q0)
    return(time_list, q0_list)