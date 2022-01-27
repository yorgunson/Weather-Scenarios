import sys
sys.path.append('/mnt/user/soner.yorgun/utils')
from time import strftime, strptime
from datetime import datetime, timedelta
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as col
import math
from mpl_toolkits.basemap import Basemap
import numpy.ma as ma
import random
import matplotlib.colors as col
import matplotlib.cm as cm
import scipy.cluster.hierarchy as hc
import itertools
import pygrib as pgrb
from GetObject import EnsembleObject

###################################################
pth_hrrre='/vol/project/nevs/hrrre/'
pth_plot='/mnt/user/soner.yorgun/SCENARIOS/ObjDetectCluster/HRRRE/Objectify/Plots/'
pth_array='/mnt/user/soner.yorgun/SCENARIOS/ObjDetectCluster/HRRRE/Objectify/SavedArrays/'
##################################################

nws_vil_colors = [".95",".85",".75",".65", ".55", ".45", ".35", "#02fd02", "#fdf802", "#fd9500", "#fd0000", "#d40000", "#bc0000", "#f800fd", "#9854c6", "#483d8b"]
cmap4 = col.ListedColormap(nws_vil_colors, 'NWS_vil')
cm.register_cmap(cmap=cmap4)

members=[]
for i in range(1,19):
    members.append('postprd_mem00'+str(i).zfill(2))
        
members_plot=[]
for i in range(19):
    members_plot.append('m'+str(i))

def VARplot(year,month,day,issue,lead,show):
    
    timeW=year+month+day+'_'+issue+'_'+lead
    
    plot=-1
    fig, ax = plt.subplots(3,6,figsize=(20, 10),facecolor='w', edgecolor='k')
    ax = ax.ravel()
    fig.suptitle('VIL {0}' .format(timeW),fontsize=15)
    
    for m in range(len(members)):
    
        #print 'member=',members[m]
        
        path=pth_hrrre+year+month+day+issue+'/'
        fname=path+members[m]+'/wrftwo_mem00'+members[m][13:15]+'_'+lead+'.grb2'
        
        # Read the files and variables
        dr = pgrb.open(fname)
        d=dr.select(name='Vertically-integrated liquid')[0]
        data=d.values
    
        a = 'white'  
        b = 'blue'  
        c= 'green'  
        d = 'yellow'
        e = 'red'    
        cmap2 = col.LinearSegmentedColormap.from_list('own2',[a,b,c,d,e])	
        cm.register_cmap(cmap=cmap2)
    
        plot=plot+1
     
        img=ax[plot].contourf(data,levels=[0,1,2,3,4,5,6,7,8,9,10],cmap='NWS_vil')
        plt.setp(ax[plot],xticks=[],yticks=[])
        ax[plot].set_title('{0}' .format(members_plot[m]),size=12)
    
    cbar_ax = fig.add_axes([0.92, 0.15, 0.03, 0.7])
    plt.colorbar(img,cax=cbar_ax)
    
    if show=='yes': plt.show()
    elif show=='no': plt.savefig(pth_plot+'VIL_{0}.png' .format(timeW))    


def OBJplot(src,th,clCutoff,timeW,sizeTH,gl,show):
    
    attrib=np.load(pth_array+'Attrib_{0}_{1}th_{2}.npy' .format(src,th,timeW)) # Read the spatial array that holds the object labels, VIL/ET values
    objects=np.load(pth_array+'Objects_{0}_{1}th_{2}.npy' .format(src,th,timeW))
    link=np.load(pth_array+'Linkage_{0}_{1}th_{2}_size{3}.npy' .format(src,th,timeW,sizeTH))
    CmassMember=np.load(pth_array+'CmassMember_{0}_{1}th_{2}_size{3}.npy' .format(src,th,timeW,sizeTH))
    
    obj=EnsembleObject(objects,attrib)
    
    objs=np.empty_like(objects['obj_Var'])
    
    cluster=clCutoff[0];cutoff=clCutoff[1]
    part = hc.fcluster(link, cutoff, 'maxclust')
        
    aa=[]
    aa.append(CmassMember[part == cluster, 0])
    aa.append(CmassMember[part == cluster, 1])
    aa.append(CmassMember[part == cluster, 2])
    aa=np.asarray(aa)
    
    plot=-1
    fig, ax = plt.subplots(3,6,figsize=(20, 10),facecolor='w', edgecolor='k')
    ax = ax.ravel()
    fig.suptitle('Objects {0}' .format(timeW),fontsize=15)
    
    for m in range(len(members)):
    
        #print 'member=',members[m]
        
        mem_idx=np.argwhere(aa[2,:]==members[m])
        for i in range(mem_idx.shape[0]):
                
            cmass=(int(aa[0,mem_idx[i][0]]),int(aa[1,mem_idx[i][0]]))
            sz=obj.size(0,m,cmass)
            
            if gl=='g' and sz<=sizeTH:
                
                grid=obj.ObjGrid(0,m,cmass)
                #objs[0,m,grid[:,0],grid[:,1]]=0
                objs[0,m,grid[:,0],grid[:,1]]=objects['obj_Var'][0,m,grid[:,0],grid[:,1]]
                    
            elif gl=='l' and sz>sizeTH:
                    
                grid=obj.ObjGrid(0,m,cmass)
                #objs[0,m,grid[:,0],grid[:,1]]=0
                objs[0,m,grid[:,0],grid[:,1]]=objects['obj_Var'][0,m,grid[:,0],grid[:,1]]
                    
            else:
                print 'Adam Gibi Gir Su Veriyi'
                continue
    
        a = 'white'  
        b = 'blue'  
        c= 'green'  
        d = 'yellow'
        e = 'red'    
        cmap2 = col.LinearSegmentedColormap.from_list('own2',[a,b,c,d,e])	
        cm.register_cmap(cmap=cmap2)

        plot=plot+1
        
        img=ax[plot].contourf(objs[0,m,:,:],levels=[0,1,2,3,4,5,6,7,8,9,10],cmap='NWS_vil')
        plt.setp(ax[plot],xticks=[],yticks=[])
        ax[plot].set_title('{0}' .format(members_plot[m]),size=12)
    
    cbar_ax = fig.add_axes([0.92, 0.15, 0.03, 0.7])
    plt.colorbar(img,cax=cbar_ax)
    
    if show=='yes': plt.show()
    elif show=='no':
        plt.savefig(pth_plot+'{0}/Objects_{1}_cutoff{2}_cl{3}_size{4}.png' .format(timeW,timeW,cutoff,cluster,sizeTH))
        plt.close()


def OBJplot_bound(src,th,clCutoff,timeW,sizeTH,gl,binary,show):
    
    attrib=np.load(pth_array+'Attrib_{0}_{1}th_{2}.npy' .format(src,th,timeW)) # Read the spatial array that holds the object labels, VIL/ET values
    objects=np.load(pth_array+'Objects_{0}_{1}th_{2}.npy' .format(src,th,timeW))
    link=np.load(pth_array+'Linkage_{0}_{1}th_{2}_size{3}.npy' .format(src,th,timeW,sizeTH))
    CmassMember=np.load(pth_array+'CmassMember_{0}_{1}th_{2}_size{3}.npy' .format(src,th,timeW,sizeTH))
    
    obj=EnsembleObject(objects,attrib)
    
    #objs=np.empty_like(objects['obj_Var'])
    if binary=='yes':objs=np.zeros_like(objects['obj_Var'])
    if binary=='no':objs=np.empty_like(objects['obj_Var'])
    
    cluster=clCutoff[0];cutoff=clCutoff[1]
    part = hc.fcluster(link, cutoff, 'maxclust')
        
    aa=[]
    aa.append(CmassMember[part == cluster, 0])
    aa.append(CmassMember[part == cluster, 1])
    aa.append(CmassMember[part == cluster, 2])
    aa=np.asarray(aa)
    
    plot=-1
    fig, ax = plt.subplots(3,6,figsize=(20, 10),facecolor='w', edgecolor='k')
    ax = ax.ravel()
    fig.suptitle('Objects {0}' .format(timeW),fontsize=15)
    
    # get the bounds of the region
    maxi=max(aa[0,:].astype(int))
    maxj=max(aa[1,:].astype(int))
    mini=min(aa[0,:].astype(int))
    minj=min(aa[1,:].astype(int))
    
    if mini-10<0:ilim1=0
    else:ilim1=mini-10
            
    if maxi+10>objects['obj_Var'].shape[2]:ilim2=objects['obj_Var'].shape[2]
    else:ilim2=maxi+10
            
    if minj-10<0:jlim1=0
    else:jlim1=minj-10
            
    if maxj+10>objects['obj_Var'].shape[3]:jlim2=objects['obj_Var'].shape[3]
    else:jlim2=maxj+10
    
    # Plots
    for m in range(len(members)):
        
        mem_idx=np.argwhere(aa[2,:]==members[m])
        for i in range(mem_idx.shape[0]):
            
            idx=mem_idx[i][0]    
            cmass=(int(aa[0,idx]),int(aa[1,idx]))
            sz=obj.size(0,m,cmass)

            if gl=='g' and sz<=sizeTH:
                
                grid=obj.ObjGrid(0,m,cmass)
                if binary=='no':objs[0,m,grid[:,0],grid[:,1]]=objects['obj_Var'][0,m,grid[:,0],grid[:,1]]
                if binary=='yes':objs[0,m,grid[:,0],grid[:,1]]=1
                    
            elif gl=='l' and sz>sizeTH:
                    
                grid=obj.ObjGrid(0,m,cmass)
                if binary=='no':objs[0,m,grid[:,0],grid[:,1]]=objects['obj_Var'][0,m,grid[:,0],grid[:,1]]
                if binary=='yes':
                    objs[0,m,grid[:,0],grid[:,1]]=1
                    
            else:
                print 'Adam Gibi Gir Su Veriyi'
                continue
    
        a = 'white'  
        b = 'blue'  
        #c= 'green'  
        #d = 'yellow'
        #e = 'red'    
        cmap2 = col.LinearSegmentedColormap.from_list('own2',[a,b])	
        cm.register_cmap(cmap=cmap2)

        plot=plot+1
        
        if binary=='no':img=ax[plot].contourf(objs[0,m,:,:],levels=[0,1,2,3,4,5,6,7,8,9,10],cmap='NWS_vil')
        if binary=='yes':img=ax[plot].contourf(objs[0,m,:,:],cmap=cmap2)
        #plt.setp(ax[plot],xticks=[],yticks=[])
        plt.setp(ax[plot],xlim=[jlim1,jlim2],ylim=[ilim1,ilim2],xticks=[],yticks=[])
        ax[plot].set_title('{0}' .format(members_plot[m]),size=12)
    
    cbar_ax = fig.add_axes([0.92, 0.15, 0.03, 0.7])
    plt.colorbar(img,cax=cbar_ax)
    
    if show=='yes': plt.show()
    elif show=='no':
        plt.savefig(pth_plot+'{0}/Objects_{1}_cutoff{2}_cl{3}_size{4}.png' .format(timeW,timeW,cutoff,cluster,sizeTH))
        plt.close()
        
        
def OBJplot_bound_sub(src,th,clCutoff,timeW,sizeTH,gl,binary,show):
    
    attrib=np.load(pth_array+'Attrib_{0}_{1}th_{2}.npy' .format(src,th,timeW)) # Read the spatial array that holds the object labels, VIL/ET values
    objects=np.load(pth_array+'Objects_{0}_{1}th_{2}.npy' .format(src,th,timeW))
    link=np.load(pth_array+'Linkage_{0}_{1}th_{2}_size{3}.npy' .format(src,th,timeW,sizeTH))
    CmassMember=np.load(pth_array+'CmassMember_{0}_{1}th_{2}_size{3}.npy' .format(src,th,timeW,sizeTH))
    
    obj=EnsembleObject(objects,attrib)
    
    #objs=np.empty_like(objects['obj_Var'])
    if binary=='yes':objs=np.zeros_like(objects['obj_Var'])
    if binary=='no':objs=np.empty_like(objects['obj_Var'])
    
    cluster=clCutoff[0];cutoff=clCutoff[1]
    part = hc.fcluster(link, cutoff, 'maxclust')
        
    aa=[]
    aa.append(CmassMember[part == cluster, 0])
    aa.append(CmassMember[part == cluster, 1])
    aa.append(CmassMember[part == cluster, 2])
    aa=np.asarray(aa)
    
    plot=-1
    fig, ax = plt.subplots(3,6,figsize=(20, 10),facecolor='w', edgecolor='k')
    ax = ax.ravel()
    fig.suptitle('Objects {0}' .format(timeW),fontsize=15)
    
    # get the bounds of the region
    maxi=max(aa[0,:].astype(int))
    maxj=max(aa[1,:].astype(int))
    mini=min(aa[0,:].astype(int))
    minj=min(aa[1,:].astype(int))
    
    if mini-10<0:ilim1=0
    else:ilim1=mini-10
            
    if maxi+10>objects['obj_Var'].shape[2]:ilim2=objects['obj_Var'].shape[2]
    else:ilim2=maxi+10
            
    if minj-10<0:jlim1=0
    else:jlim1=minj-10
            
    if maxj+10>objects['obj_Var'].shape[3]:jlim2=objects['obj_Var'].shape[3]
    else:jlim2=maxj+10
    
    # Plots
    for m in range(len(members)):
        
        mem_idx=np.argwhere(aa[2,:]==members[m])
        for i in range(mem_idx.shape[0]):
            
            idx=mem_idx[i][0]    
            cmass=(int(aa[0,idx]),int(aa[1,idx]))
            sz=obj.size(0,m,cmass)

            if gl=='g' and sz<=sizeTH:
                
                grid=obj.ObjGrid(0,m,cmass)
                if binary=='no':objs[0,m,grid[:,0],grid[:,1]]=objects['obj_Var'][0,m,grid[:,0],grid[:,1]]
                if binary=='yes':objs[0,m,grid[:,0],grid[:,1]]=1
                    
            elif gl=='l' and sz>sizeTH:
                    
                grid=obj.ObjGrid(0,m,cmass)
                if binary=='no':objs[0,m,grid[:,0],grid[:,1]]=objects['obj_Var'][0,m,grid[:,0],grid[:,1]]
                if binary=='yes':
                    objs[0,m,grid[:,0],grid[:,1]]=1
                    
            else:
                print 'Adam Gibi Gir Su Veriyi'
                continue
    
        a = 'white'  
        b = 'blue'  
        #c= 'green'  
        #d = 'yellow'
        #e = 'red'    
        cmap2 = col.LinearSegmentedColormap.from_list('own2',[a,b])	
        cm.register_cmap(cmap=cmap2)

        plot=plot+1
        
        objs[0,m,:110,:]=0
        
        if binary=='no':img=ax[plot].contourf(objs[0,m,:,:],levels=[0,1,2,3,4,5,6,7,8,9,10],cmap='NWS_vil')
        if binary=='yes':img=ax[plot].contourf(objs[0,m,:,:],cmap=cmap2)
        #plt.setp(ax[plot],xticks=[],yticks=[])
        plt.setp(ax[plot],xlim=[jlim1,jlim2],ylim=[110,ilim2],xticks=[],yticks=[])
        ax[plot].set_title('{0}' .format(members_plot[m]),size=12)
    
    cbar_ax = fig.add_axes([0.92, 0.15, 0.03, 0.7])
    plt.colorbar(img,cax=cbar_ax)
    
    if show=='yes': plt.show()
    elif show=='no':
        plt.savefig(pth_plot+'{0}/Objects_{1}_cutoff{2}_cl{3}_size{4}.png' .format(timeW,timeW,cutoff,cluster,sizeTH))
        plt.close()

if "__main__" == __name__:

    #OBJplot(src='hrrre',th=3.5,clCutoff=(4,4),timeW='20160604_15_12',sizeTH=0,gl='l')

    #VARplot(year='2016',month='06',days=range(4,5),issue='15',lead='12')
    VARplot(year='2016',month='06',days=range(16,17),issue='15',lead='04',show='yes')


