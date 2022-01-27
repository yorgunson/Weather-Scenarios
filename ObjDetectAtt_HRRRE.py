from netCDF4 import Dataset
from time import strftime, strptime
from datetime import datetime, timedelta
import numpy as np
import math
#from prod_proj import ProdProj as pp
import numpy.ma as ma
import random
import pygrib as pgrb

###################################################
pth_hrrre='/vol/project/nevs/hrrre/'
pth_plot='/mnt/user/soner.yorgun/SCENARIOS/ObjDetectCluster/HRRRE/Objectify/Plots/'
pth_array='/mnt/user/soner.yorgun/SCENARIOS/ObjDetectCluster/HRRRE/Objectify/SavedArrays/'
##################################################

def ObjDetectAtt(year,month,day,issue,lead,th):
    
    members=[]
    for i in range(1,19):
        members.append('postprd_mem00'+str(i).zfill(2))
    
    timeW=year+month+day+'_'+issue+'_'+lead
    
    #th=3.5 # Value threshold
    
    # Create the iteration list that will check adjacent cells for the region growing method
    list_i=[1,1,1,0,0,0,-1,-1,-1]
    list_j=[-1,0,1,-1,0,1,-1,0,1,]
    iterator=zip(list_i,list_j)
    
    # Get Dimensions
    path=pth_hrrre+year+month+day+issue+'/'
    fname=path+members[0]+'/wrftwo_mem00'+members[0][13:15]+'_'+lead+'.grb2'
    dr = pgrb.open(fname)
    d=dr.select(name='Vertically-integrated liquid')[0]
    data=d.values
    x2=data.shape[1];x1=0;y2=data.shape[0];y1=0
    y_lim=y2-y1+2
    x_lim=x2-x1+2
    
    
    dim1=str(len(members))
    dim2=str(y_lim)
    dim3=str(x_lim)
    
    objects=np.zeros(1, dtype=[('member',dim1+'|S64'),
                                ('obj_labels','('+dim1+','+dim2+','+dim3+')int'),
                                ('obj_Var','('+dim1+','+dim2+','+dim3+')float'),
                                ('total_Var','('+dim1+','+dim2+','+dim3+')float')])
    
    
    ###################################################
    ## OBJECT IDENTIFICATION - REGION GROWING METHOD ##
    ###################################################
    print "-------------------"
    print "Identifying Objects"
    print "-------------------"
    time_idx=0
    
    for m in range(len(members)):
            
        print 'member=',members[m]
        
        path=pth_hrrre+year+month+day+issue+'/'
        fname=path+members[m]+'/wrftwo_mem00'+members[m][13:15]+'_'+lead+'.grb2'
            
        # Read the files and variables
        dr = pgrb.open(fname)
        d=dr.select(name='Vertically-integrated liquid')[0]
        data=d.values
       
        data=data[y1:y2,x1:x2]
        data=np.pad(data, ((1,1),(1,1)), 'constant', constant_values=(0,)) # Padding zeros to boundaries for object detection
        data_th=np.copy(data)
            
    
        objects['member'][time_idx,m]=members[m]
            
        # First populate the total_precip field of the array
        objects['total_Var'][time_idx,m,:,:]=data
            
        # Threshold the precip array and make it binary
        np.place(data_th, data_th>=th, 100)
        np.place(data_th, data_th<th, 0)
        np.place(data_th, data_th>0, 1)
            
        # Duplicate the VIL array to work on
        data_work=np.copy(data_th)
                        
        bigdec=0 # Decision to stop the while loop that finds all objects for a given time and location
        rcount=0 # The labels of the objects
        while bigdec==0:
            
            # Get all the gridpoints that satisfy the threshold 
            pick=np.argwhere(data_work==1)
                
            # If there is no gridpoints to satisfy the precip threshold (i.e., no objects) break the loop
            if len(pick)==0:
                break
                
            # Pick a random gridpoint with precip>=th
            a=np.random.choice(np.arange(pick.shape[0]),1)

            ii=pick[a[0]][0]
            jj=pick[a[0]][1]
    
            # Initiate the object count and recording
            rcount=rcount+1
            objects['obj_labels'][time_idx,m,ii,jj]=rcount
            data_work[ii,jj]=0
            iter_list=[]
            iter_list.append((ii,jj))
                
            # The loop to search the adjacent gridpoints until a single object is formed
            dec=0
            while dec==0:
                declist=[]
                iter_list_new=[]
                for idx in iter_list:
                    for i,j in iterator:
                        if idx[0]-i>0 and idx[0]+i<data_th.shape[0] and idx[1]-j>0 and idx[1]+j<data_th.shape[1]:
                            if objects['obj_labels'][time_idx,m,idx[0]+i,idx[1]+j]==0: # If the gridpoint is not labeled yet
        
                                if data_th[idx[0]+i,idx[1]+j]==1:
                                    objects['obj_labels'][time_idx,m,idx[0]+i,idx[1]+j]=rcount
                                    data_work[idx[0]+i,idx[1]+j]=0
                                    declist.append(0)
                                    iter_list_new.append((idx[0]+i,idx[1]+j))
                                else:    
                                    declist.append(1)
                                
                
                iter_list=iter_list_new
                if np.unique(np.asarray(declist)).shape[0]>1:
                    dec=0
                elif np.unique(np.asarray(declist))==1:
                    dec=1
                elif np.unique(np.asarray(declist))==0:
                    dec=0        
                
            if np.unique(data_work).shape[0]>1:
                bigdec=0
            else:
                bigdec=1
            
        for i in range(objects['obj_labels'].shape[2]):
            for j in range(objects['obj_labels'].shape[3]):
                if objects['obj_labels'][time_idx,m,i,j]!=0:
                    objects['obj_Var'][time_idx,m,i,j]=data[i,j]
    
    
    
    ##############################################################
    ##                    OBJECT ATTRIBUTES                     ##
    ##############################################################
    
    print "--------------------"
    print "Computing Attributes"
    print "--------------------"
    
    # Initiate the attribute array
    maxnum=np.max(objects['obj_labels']) #determine the maximum number of objects to be able to form the array
    
    adim1=str(len(members))
    adim2=str(maxnum)
    
    attrib=np.zeros(objects.shape[0], dtype=[('obj_num','('+adim1+','+adim2+')int'),
                                            ('area','('+adim1+','+adim2+')int'),
                                            ('cmass','('+adim1+','+adim2+',2)int'),
                                            ('maxVar','('+adim1+','+adim2+')float'),
                                            ('meanVar','('+adim1+','+adim2+')float')])
    
    # For each timestep do
    for i in range(objects.shape[0]):
        for m in range(len(members)):
            print 'member=',members[m]
            
            objnums=np.unique(objects['obj_labels'][i,m,:,:]) # Get the number of identifed objects (for each timestep) 
            objnums=np.delete(objnums,0) # Delete the initial number, which is zero
            
            # For each object do
            for j in range(len(objnums)):
    
                # Get the gridpoints that are labeled with the corresponding object number
                count=np.argwhere(objects['obj_labels'][i,m,:,:]==objnums[j])
                
                # Calculate the center of mass and mean/max VIL of the corresponding object
                mass=[]
                mass_x=[]
                mass_y=[]
                for k in range(len(count)):
                    mass.append(objects['obj_Var'][i,m,count[k][0],count[k][1]])
                    mass_x.append(count[k][0]*objects['obj_Var'][i,m,count[k][0],count[k][1]])
                    mass_y.append(count[k][1]*objects['obj_Var'][i,m,count[k][0],count[k][1]])
                
                cmass_x=round(sum(mass_x)/sum(mass))
                cmass_y=round(sum(mass_y)/sum(mass))
                
                meanPrecip=sum(mass)/len(mass)
                maxPrecip=max(mass)
    
                
                # Populate the attribute array
                attrib['obj_num'][i][m][j]=objnums[j]
                attrib['area'][i][m][j]=len(count)
                attrib['cmass'][i][m][j][0]=cmass_x
                attrib['cmass'][i][m][j][1]=cmass_y
                attrib['meanVar'][i][m][j]=meanPrecip
                attrib['maxVar'][i][m][j]=maxPrecip
    
    
    np.save(pth_array+'Objects_hrrre_{0}th_{1}' .format(th,timeW),objects)
    np.save(pth_array+'Attrib_hrrre_{0}th_{1}' .format(th,timeW),attrib)
    