############################
#       Monitor Module     #
############################

import matplotlib.pyplot as plt
import numpy as np
import utils

def show_percolation(q_list,tp_list,ts_list,q0) :
    fig, ax1 = plt.subplots()    
    color = 'tab:green'
    ax1.set_xlabel('q')
    ax1.set_ylabel('G', color=color)
    ax1.plot(q_list,tp_list,color=color)
    ax1.tick_params(axis='y', labelcolor = color)
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('SG', color = color)
    ax2.plot(q_list, ts_list, color = color)
    ax2.tick_params(axis='y', labelcolor = color)
    plt.axvline(q0,linestyle = '--', label = 'q0 ='+str(int(q0*100)/100))
    plt.legend()
    plt.show()

def aux(q_list,tp_list,ts_list,q0,ax1, title) :   
    color = 'tab:green'
    ax1.set_xlabel('q')
    ax1.set_ylabel('G', color=color)
    ax1.set_title(title)
    ax1.plot(q_list,tp_list,color=color)
    ax1.axvline(q0,linestyle = '--', label = 'q0 ='+str(int(q0*100)/100))
    ax1.tick_params(axis='y', labelcolor = color)
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('SG', color = color)
    ax2.plot(q_list, ts_list, color = color)
    ax2.tick_params(axis='y', labelcolor = color)

def show_selfdriving_cars(time, n, p, saved_cars, graphe, dt, initial_state, save_result) :
    p_list = np.linspace(0,1,n)
    q0_list = []
    nn = n**(1/2)
    reset = False
    if nn != int(nn) :
        nn = int(nn) + 1
        m = n//nn + 1
        fig,axs = plt.subplots(m,nn, constrained_layout=True)
    else :
        nn = int(nn)
        fig,axs = plt.subplots(nn+1,nn, constrained_layout=True)
    for k in range(n) :
        r =(k+1)%nn
        if r !=0 :
            i,j = (k+1)//nn,r-1
        else :
            i,j = (k+1)//nn-1, nn-1
        ax1 = axs[i,j]
        pp = p_list[k]
        q0,q_list,tp_list,ts_list = utils.simulation_percolation(time,pp,saved_cars,graphe,dt,reset)
        reset = True
        q0_list.append(q0)
        aux(q_list,tp_list,ts_list,q0,ax1,'p ='+str(int(pp*100)/100))
    if initial_state :
        utils.simulation(time, p, saved_cars, graphe, dt, True)
    if j != nn-1 :
        ax1 = axs[i,j+1]
    else :
        ax1 = axs[i+1,0]
    ax1.plot(p_list,q0_list,color='black')
    ax1.set_xlabel('p')
    ax1.set_ylabel('q0')
    if save_result:
        plt.savefig(("results/sdc Cars " + str(len(saved_cars))+ " Time " + str(time) +" 3"+".svg"), dpi="figure", format="svg")
    else:
        plt.show()

def show_q0_evolution(time,n,p,saved_cars,graphe,dt,reset,save_result) :
    time_list, q0_list = utils.simulation_q0_evolution(time,n,p,saved_cars,graphe,dt,reset)
    plt.plot(time_list,q0_list)
    plt.ylabel('q0')
    plt.xlabel('time')
    if save_result:
        plt.savefig(("results/q0(t) " + str(len(saved_cars))+".svg"), dpi="figure", format='svg')
    else:
        plt.show()

def aux2(time_list,q0_list,ax1,title) :
    color = 'tab:blue'
    ax1.set_xlabel('time')
    ax1.set_ylabel('q0')
    ax1.set_title(title)
    ax1.plot(time_list,q0_list,color=color)
    m = sum(q0_list)/len(q0_list)
    ax1.axhline(m,linestyle = '--', label = str(int(m*1000)/1000))
    ax1.legend()

def show_multiple_q0_evolution(time,n_q0,n_p,p,saved_cars,graphe,dt,initial_state,save_result) :
    p_list = np.linspace(0,1,n_p)
    q0_list = []
    nn = n_p**(1/2)
    reset = False
    if nn != int(nn) :
        nn = int(nn) + 1
        m = n_p//nn + 1
        fig,axs = plt.subplots(m,nn, constrained_layout=True)
    else :
        nn = int(nn)
        fig,axs = plt.subplots(nn+1,nn, constrained_layout=True)
    for k in range(n_p) :
        r =(k+1)%nn
        if r !=0 :
            i,j = (k+1)//nn,r-1
        else :
            i,j = (k+1)//nn-1, nn-1
        ax1 = axs[i,j]
        pp = p_list[k]
        time_list, q0_list = utils.simulation_q0_evolution(time,n_q0,pp,saved_cars,graphe,dt,reset)
        reset = True
        aux2(time_list,q0_list,ax1,'p ='+str(int(pp*100)/100))
    if initial_state :
        utils.simulation(time, p, saved_cars, graphe, dt, True)
    if j != nn-1 :
        ax1 = axs[i,j+1]
    else :
        ax1 = axs[i+1,0]
    if save_result:
        plt.savefig(("results/q0s Cars " + str(len(saved_cars))+ " Time " + str(time) +" 3"+".svg"), dpi="figure", format="svg")
    else:
        plt.show()