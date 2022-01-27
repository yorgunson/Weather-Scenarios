from __future__ import division
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

###################################################
pth_hrrre='/vol/project/nevs/hrrre/'
pth_plot='/mnt/user/soner.yorgun/SCENARIOS/ObjDetectCluster/HRRRE/Objectify/Plots/'
pth_array='/mnt/user/soner.yorgun/SCENARIOS/ObjDetectCluster/HRRRE/Objectify/SavedArrays/'
##################################################


def scree(src,th,time,timeW,sizeTH,cutoff,show):
    
    print 'HED'
    
    attrib=np.load(pth_array+'Attrib_{0}_{1}th_{2}.npy' .format(src,th,timeW)) # Read the spatial array that holds the object labels, VIL/ET values
    objects=np.load(pth_array+'Objects_{0}_{1}th_{2}.npy' .format(src,th,timeW))
    link=np.load(pth_array+'Linkage_{0}_{1}th_{2}_size{3}.npy' .format(src,th,timeW,sizeTH))
    CmassMember=np.load(pth_array+'CmassMember_{0}_{1}th_{2}_size{3}.npy' .format(src,th,timeW,sizeTH))
    
    members_plot=[]
    for i in range(22):
        members_plot.append('m'+str(i))
    
    part = hc.fcluster(link, cutoff, 'maxclust')
    clusters=range(1,cutoff+1)
    
    slope=np.diff(link[:,2])
    
    # Screeplot
    fig,ax1=plt.subplots()
    x_limit=15
    x_ticks=np.arange(0,15,1)
    ax1.set_ylabel('Cluster Distance',color='b')
    ax1.plot(range(1, len(link)+1), link[::-1, 2])
    plt.setp(ax1,xlabel='Partition',xlim=[0,x_limit],xticks=x_ticks)
    ax1.set_title('Screeplot',size=15)
    for tl in ax1.get_yticklabels():
        tl.set_color('b')
    
    '''    
    ax2 = ax1.twinx()
    ax2.plot(range(1, len(link)), slope[::-1],'g')
    ax2.set_ylabel('Distance Difference',color='g')
    plt.setp(ax2,xlim=[0,x_limit],xticks=x_ticks)
    for tl in ax2.get_yticklabels():
        tl.set_color('g')
    '''    
    ax1.plot([cutoff,cutoff],[0,np.max(link[::-1, 2])],'r--', lw=1)
    ax1.annotate('Possible Cutoff {0}' .format(cutoff), xy=(cutoff+0.5,np.max(link[::-1, 2])-20),fontsize=15,color='red')
    
    if show=='yes': plt.show()
    elif show=='no': plt.savefig(pth_plot+'Screeplot_{0}_size{1}.png' .format(timeW,sizeTH))