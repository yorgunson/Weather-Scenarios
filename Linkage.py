from netCDF4 import Dataset
from time import strftime, strptime
from datetime import datetime, timedelta
import numpy as np
import math
import numpy.ma as ma
import random
import scipy.cluster.hierarchy as hc

###################################################
pth_hrrre='/vol/project/nevs/hrrre/'
pth_plot='/mnt/user/soner.yorgun/SCENARIOS/ObjDetectCluster/HRRRE/Objectify/Plots/'
pth_array='/mnt/user/soner.yorgun/SCENARIOS/ObjDetectCluster/HRRRE/Objectify/SavedArrays/'
##################################################

def link(src,th,time,timeW,sizeTH):
    
    attrib=np.load(pth_array+'Attrib_{0}_{1}th_{2}.npy' .format(src,th,timeW)) # Read the spatial array that holds the object labels, VIL/ET values
    objects=np.load(pth_array+'Objects_{0}_{1}th_{2}.npy' .format(src,th,timeW))

    #sizeTH=0
    
    # Forming a full array of centers of mass from each SREF member to be fed into clustering 
    cmass_list=[]
    member_list=[]
    for m in range(objects['member'].shape[1]):
        for i in range(attrib['cmass'].shape[2]):
            if attrib['cmass'][time,m,i,0]!=0 and attrib['cmass'][time,m,i,1]!=0 and attrib['area'][time,m,i] > sizeTH:
                cmass_list.append((attrib['cmass'][time,m,i,0],attrib['cmass'][time,m,i,1]))
                member_list.append(objects['member'][time,m])
    
    
    cmass_array=np.asarray(cmass_list)
    member_array=np.asarray(member_list)
    CmassMember=np.column_stack((cmass_array,member_list))
    
    link = hc.ward(cmass_array)
    
    np.save(pth_array+'Linkage_{0}_{1}th_{2}_size{3}' .format(src,th,timeW,sizeTH),link)
    np.save(pth_array+'CmassMember_{0}_{1}th_{2}_size{3}' .format(src,th,timeW,sizeTH),CmassMember)

