from netCDF4 import Dataset
from time import strftime, strptime
from datetime import datetime, timedelta
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import math
import numpy.ma as ma
import random
import matplotlib.colors as col
import matplotlib.cm as cm
import scipy.cluster.hierarchy as hc
import itertools

###################################################
pth_hrrre='/vol/project/nevs/hrrre/'
pth_plot='/mnt/user/soner.yorgun/SCENARIOS/ObjDetectCluster/HRRRE/Objectify/Plots/'
pth_array='/mnt/user/soner.yorgun/SCENARIOS/ObjDetectCluster/HRRRE/Objectify/SavedArrays/'
##################################################


def DecBound_Cmass(src,th,timeW,sizeTH,cutoff,show):

    attrib=np.load(pth_array+'Attrib_{0}_{1}th_{2}.npy' .format(src,th,timeW)) # Read the spatial array that holds the object labels, VIL/ET values
    objects=np.load(pth_array+'Objects_{0}_{1}th_{2}.npy' .format(src,th,timeW))
    link=np.load(pth_array+'Linkage_{0}_{1}th_{2}_size{3}.npy' .format(src,th,timeW,sizeTH))
    CmassMember=np.load(pth_array+'CmassMember_{0}_{1}th_{2}_size{3}.npy' .format(src,th,timeW,sizeTH))
       
    members=[]
    for i in range(1,19):
        members.append('postprd_mem00'+str(i).zfill(2))
        
    members_plot=[]
    for i in range(22):
        members_plot.append('m'+str(i))
    
    #cutoff=4
    part = hc.fcluster(link, cutoff, 'maxclust')
    
    renk = ['#2200CC' ,'#D9007E' ,'#FF6600' ,'#FFCC00' ,'#ACE600' ,'#0099CC' ,'#8900CC' ,'#FF0000' ,'#FF9900' ,'#FFFF00' ,'#00CC01' ,'#0055CC','blue','green','red','yellow','black','cyan']
    
    plot=-1
        
    fig, ax = plt.subplots(3,6,figsize=(20, 10),facecolor='w', edgecolor='k')
    ax = ax.ravel()
    fig.suptitle('Cluster Cmass / {0} Clusters' .format(cutoff),fontsize=15)
    
    for i in range(len(members)):
        plot=plot+1
        idx_list=[]
        precip_list=[]
        precip=np.zeros((objects['obj_Var'].shape[2],objects['obj_Var'].shape[3]))
            
        idx=np.where(CmassMember[:,2]==members[i])
        y=np.array(CmassMember[idx,0][0],dtype=int)
        x=np.array(CmassMember[idx,1][0],dtype=int)
    
        for cl in set(part):
            clr=renk[cl]
            alp=0.1
            ax[plot].scatter(CmassMember[part == cl, 1], CmassMember[part == cl, 0], color=clr,alpha=alp)
         
        clr='black'
        ax[plot].scatter(x, y, color=clr,s=5)#,alpha=alp)
        plt.setp(ax[plot],xticks=[],yticks=[],xlim=(0,objects['obj_Var'].shape[3]),ylim=(0,objects['obj_Var'].shape[2]))
        ax[plot].set_title('{0}' .format(members[i]),size=12)
    plt.show()
    #plt.savefig(pth_plot+'CmassMembers_th{0}_cutoff{1}_{2}_size{3}.png' .format(th,cutoff,timeW,sizeTH))
    
