from __future__ import division
import sys
sys.path.append('/mnt/user/soner.yorgun/utils')
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
import sklearn
from GetObject import EnsembleObject
from SAL import sal, plot_heatmap, plot_memAvg_single, plot_memAvg

###################################################
pth_hrrre='/vol/project/nevs/hrrre/'
pth_plot='/mnt/user/soner.yorgun/SCENARIOS/ObjDetectCluster/HRRRE/Objectify/Plots/'
pth_array='/mnt/user/soner.yorgun/SCENARIOS/ObjDetectCluster/HRRRE/Objectify/SavedArrays/'
##################################################

#src='hrrre'
#th=3.5
#timeW='20160604_15_12'
#time=0
#sizeTH=0

def exec_sal(src,th,cutoff,time,timeW,sizeTH,show):
    
    attrib=np.load(pth_array+'Attrib_{0}_{1}th_{2}.npy' .format(src,th,timeW)) # Read the spatial array that holds the object labels, VIL/ET values
    objects=np.load(pth_array+'Objects_{0}_{1}th_{2}.npy' .format(src,th,timeW))
    link=np.load(pth_array+'Linkage_{0}_{1}th_{2}_size{3}.npy' .format(src,th,timeW,sizeTH))
    CmassMember=np.load(pth_array+'CmassMember_{0}_{1}th_{2}_size{3}.npy' .format(src,th,timeW,sizeTH))
    
    obj=EnsembleObject(objects,attrib)
    salobj=sal(objects,attrib)
         
    members=[]
    for i in range(1,19):
        members.append('postprd_mem00'+str(i).zfill(2))
            
    members_plot=[]
    for i in range(18):
        members_plot.append('m'+str(i))
    
    #cluster=clCutoff[0];cutoff=clCutoff[1]
    part = hc.fcluster(link, cutoff, 'maxclust')
    clusters=np.arange(1,cutoff+1)
    
    for cluster in clusters:
        print '######'
        print cluster
    
        cl=[]
        cl.append(CmassMember[part == cluster, 0])
        cl.append(CmassMember[part == cluster, 1])
        cl.append(CmassMember[part == cluster, 2])
        cl=np.asarray(cl)
        objtot=[]
        objects_bycluster=[]
        cmass_bycluster=[]
        
        ################################################################
        # Storing all the objects, for all members, in a given cluster #
        ################################################################
        
        for i in range(len(members)):
            
            obj_tot=0
            for j in range(cl.shape[1]):
                
                if cl[2,j]==members[i]:
                    obj_tot=obj_tot+1
                    objects_bycluster.append((members[i],int(cl[0,j]),int(cl[1,j])))
                    cmass_bycluster.append((int(cl[0,j]),int(cl[1,j])))
            
            # Storing the number of total objects produced by a given member
            objtot.append(obj_tot)
        
        objects_bycluster=np.asarray(objects_bycluster)
        cmass_bycluster=np.asarray(cmass_bycluster)
        
        d=np.sqrt((objects['total_Var'].shape[1])**2+(objects['total_Var'].shape[2])**2)
    
        
        ###########################################
        # Processing for each object in the array #
        ###########################################
        
        # For each object in the array...
        mcmass_list=[]
        vr_list=[]
        r_list=[]
        a_list=[]
        
        mem=0
        
        for m in range(len(members)):
            print members[m]
    
            # The indices of the objects belonging to a particular member
            mem_idx=np.argwhere(objects_bycluster[:,0]==members[m])
    
            vn_list=[]
            rn_list=[]
            sz_list=[]
            cmass_rn_list=[]
            
            z=0
    
            for idx in mem_idx: # For all the objects in the given member
                
                # Get the object and its attributes
                
                cmass=(int(objects_bycluster[idx[0],1]),int(objects_bycluster[idx[0],2]))
                
                area=obj.size(time,mem,cmass)
                rnMax=obj.maxValue(time,mem,cmass)
                meanPrecip=obj.meanValue(time,mem,cmass)
    
                z+=1
                
                rn=area*meanPrecip
    
                vn_list.append(rn / rnMax)    # Volume for each object in the cluster/member
                rn_list.append(rn)            # Integrated rain amount for each object in the cluster/member
                sz_list.append(area)          # Area of each object in the cluster/member
                cmass_rn_list.append((rn,attrib['cmass'][time,m,i,0],attrib['cmass'][time,m,i,1])) #For the Location calculation
            
        
            #############################
            # SAL Calculation by Member #
            #############################
            
            # Calculation of the common Cmass of the several objects belonging to a member in a given cluster (Used both in L1 and L2)
            cmass_x,cmass_y=salobj.member_cmass(cmass_rn_list)   
            mcmass_list.append((cmass_x,cmass_y))
            
            # Calculation of the weighted averaged distance between the Cmass of the individual objects, and the Cmass of the whole field
            # Used in L2
            r=salobj.member_r_ang(cmass_rn_list,cmass_x,cmass_y)
            r_list.append(r)
            
            # Building the Volume list for all objects in a given cluster and member
            vr=salobj.member_vr(rn_list,vn_list)
            vr_list.append(vr)
            
            # Building the Amplitude list for all objects in a given cluster and member
            grids=objects['obj_labels'].shape[1]*objects['obj_labels'].shape[2]
            a_list.append(salobj.member_a(rn_list,grids))
    
            mem+=1
        
        vr=np.asarray(vr_list);a=np.asarray(a_list);mcmass=np.asarray(mcmass_list);r=np.asarray(r_list)
        
        ##############################
        # SAL Calculation by Cluster #
        ##############################
        
        # Create a fill array with values 2 in case a member doesn't have contribution to a cluster
        fill_array=np.empty(vr.shape[0])
        fill_array.fill(2)
        
        # Compute SAL for cluster
        L1=salobj.calc_L1(mcmass,d,fill_array)
        L2=salobj.calc_L2(r,d,fill_array)
        struct=salobj.calc_struct(vr,fill_array)
        amp=salobj.calc_amp(a,fill_array)
        
        L=L1+L2
          
        # Calculating the Average SALS values for each cluster
        clust_agg_s=[]
        clust_agg_L=[]
        clust_agg_amp=[]
        
        cc=len(members)/(len(members)-1) # correction coefficient
        
        for i in range(len(members)):
    
            memb_mean_L=np.mean(abs(L[i,:]))
            clust_agg_L.append(memb_mean_L*cc)
            memb_mean_s=np.mean(abs(struct[i,:]))
            clust_agg_s.append(memb_mean_s*cc)
            memb_mean_amp=np.mean(abs(amp[i,:]))
            clust_agg_amp.append(memb_mean_amp*cc)
        
        avg_s=round(sum(clust_agg_s)/len(clust_agg_s),3)
        avg_amp=round(sum(clust_agg_amp)/len(clust_agg_amp),3)
        avg_L=round(sum(clust_agg_L)/len(clust_agg_L),3)
            
        ###############################
        # PLOT THE HEATMAP (SUBPLOTS) #
        ###############################
        
        fig=plt.figure(num=None, figsize=(15, 10), dpi=70, facecolor='w', edgecolor='k')
        fig.suptitle('Cluster {0}' .format(cluster),fontsize=20)
        
        ###########
        # Cluster #
        ###########
        ax=fig.add_subplot(111)
        ax.set_title('{0} Clusters / {1}' .format(cutoff,timeW))
        
        renk = ['#2200CC' ,'#D9007E' ,'#FF6600' ,'#FFCC00' ,'#ACE600' ,'#0099CC' ,'#8900CC' ,'#FF0000' ,'#FF9900' ,'#FFFF00' ,'#00CC01' ,'#0055CC','blue','green','red','yellow','black','cyan']
        for cl in set(part):
            if cl==cluster:
                clr='black'
                alp=1
            else:
                clr=renk[cl]
                alp=0.1
            ax.scatter(CmassMember[part == cl, 1], CmassMember[part == cl, 0], color=clr,alpha=alp)
        
        plt.setp(ax,xlim=[0,objects['obj_labels'].shape[3]+10],ylim=[0,objects['obj_labels'].shape[2]+10],xticks=[],yticks=[])
        
        if show=='yes': plt.show()
        elif show=='no':
            plt.savefig(pth_plot+'CMASS_{0}_cutoff{1}_cl{2}size{3}.png' .format(timeW,cutoff,cluster,th))
            plt.close()
    
    
        #################
        #      SAL      #
        #################
        
        fig=plt.figure(num=None, figsize=(20, 10), dpi=70, facecolor='w', edgecolor='k')
        fig.suptitle('Cluster {0}' .format(cluster),fontsize=20)
        cmap=plt.cm.Blues
        cmap.set_bad(color='grey')
        
        # Member Averages #
        plot_memAvg(fig,221,members_plot,clust_agg_s,clust_agg_L,clust_agg_amp)
    
        # Heatmaps of SAL #
        plot_heatmap(fig,'Structure',222,cmap,members_plot,avg_s,struct)
        plot_heatmap(fig,'Location',223,cmap,members_plot,avg_L,L)
        plot_heatmap(fig,'Amplitude',224,cmap,members_plot,avg_amp,amp)
         
        if show=='yes': plt.show()
        elif show=='no':
            plt.savefig(pth_plot+'SAL_{0}_cutoff{1}_cl{2}size{3}.png' .format(timeW,cutoff,cluster,th))
            plt.close()
