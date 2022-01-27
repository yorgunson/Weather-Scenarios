# import matplotlib.pyplot as plt
import scipy.cluster
import numpy as np
import pylab
import pygrib
import matplotlib.pyplot as plt
import os
import scenario_db
from netCDF4 import Dataset
import gzip
import tempfile
from subprocess import call
from scipy.linalg import svd
from datetime import datetime, timedelta
import pygrib as pgrb

def get_netcdf_file(filename) :
    lfn = filename
    if lfn.endswith('gz') :
        # Make sure the file actually exists....
        # Unzip, open, read, and write to tmp.
        f = gzip.open(lfn, 'rb')
        file_content = f.read()
        f.close()

        # Create a temp file...    
        tmp = tempfile.NamedTemporaryFile()  
        tmp.write(file_content)
        tmp.flush()
        lfn = tmp.name
        
    # Open and return the netcdf file...
    return Dataset(lfn, 'r')

def readHRRRE(dt, lead, clCutoff, th, sizeTH, cltype, value):
    
    pth_hrrre='/vol/project/nevs/hrrre/'
    imgs = []
    members=[]
    
    for i in range(1,19):
        members.append('postprd_mem00'+str(i).zfill(2))
    
    timeW=str(dt.year)+str(dt.month).zfill(2)+str(dt.day).zfill(2)+'_'+str(dt.hour).zfill(2)+'_'+str(lead).zfill(2)
    cl=clCutoff[0];cutoff=clCutoff[1]
    
    labels=np.load('/mnt/user/soner.yorgun/SCENARIOS/ObjDetectCluster/HRRRE/ClusterEOF/ClusterGrids/Data/ClusterGrids_th{0}_cutoff{1}_cl{2}_{3}_size{4}.npy' .format(th,cutoff,cl,timeW,sizeTH))
    labels = labels[1:-1,1:-1]
    
    # JUST FOR SUB 4 CLUSTER
    labels[:110,:]=0
    
    # Create MBR
    
    for m in range(len(members)):
        
        path=pth_hrrre+str(dt.year)+str(dt.month).zfill(2)+str(dt.day).zfill(2)+str(dt.hour).zfill(2)+'/'
        fname=path+members[m]+'/wrftwo_mem00'+members[m][13:15]+'_'+str(lead).zfill(2)+'.grb2'
        
        dr = pgrb.open(fname)
        d=dr.select(name='Vertically-integrated liquid')[0]
        data=d.values
        data_values=np.empty_like(data)
        data_values.fill(9999)
        
        if cltype=='th':
            indices_data = np.where((labels[:,:] == value) & (data[:,:]>=th))
            indices_nodata= np.where((labels[:,:] == value) & (data[:,:]<th))
            data_values[indices_data]=data[indices_data]
            data_values[indices_nodata]=0
            data_values_ma=np.ma.masked_where(data_values==9999,data_values)
            values=data_values_ma.compressed()
            
        elif cltype=='bin':
            indices_data = np.where((labels[:,:] == value) & (data[:,:]>=th))
            indices_nodata= np.where((labels[:,:] == value) & (data[:,:]<th))
            data_values[indices_data]=1
            data_values[indices_nodata]=0
            data_values_ma=np.ma.masked_where(data_values==9999,data_values)
            
            plt.contourf(data_values_ma)
            plt.colorbar()
            plt.show()
            values=data_values_ma.compressed()
            
        elif cltype=='norm':
            indices_data = np.where((labels[:,:] == value) & (data[:,:]>=0))
            #indices_nodata= np.where((labels[:,:] == value) & (data[:,:]<th))
            data_values[indices_data]=data[indices_data]
            #data_values[indices_nodata]=0
            data_values_ma=np.ma.masked_where(data_values==9999,data_values)
            values=data_values_ma.compressed()
            
        
        #data_values=data_values.flatten()
        #print data_values.shape
        imgs.append(values)
        print len(imgs)
        dr.close()
    
    return imgs

def rankClusters(clustering, assignments):
    scale = clustering[-1][2] 
    inconsistency =  scipy.cluster.hierarchy.inconsistent(clustering)

    clusters = dict()
    for idx in set(assignments):
        clusters[idx] =  set([i for i,x in enumerate(assignments) if x==idx])
  
    ans = list()
    nodes = set()
    keys = clusters.keys()
    for i, row in enumerate(clustering):
        nodes.update(int(x) for x in row[0:2])
        for idx in keys:
            if clusters[idx].issubset(nodes):
                if len(clusters[idx]) == 1:
                    ans.append((idx, list(clusters[idx]), 0, 0))
                else:
                    ans.append((idx, list(clusters[idx]), inconsistency[i][0]/scale, inconsistency[i][1]/scale))
                keys.remove(idx)
    
    return ans

def run(product, strDt, endDt, leads, clCutoff, th, sizeTH, cltype, value=1):
    
    cl=clCutoff[0];cutoff=clCutoff[1]
    
    conn = scenario_db.get_conn()
    dt = strDt
    deltaDt = timedelta(hours=1)
    
    read = {'hrrre' : readHRRRE}
    
    while dt < endDt:
        for lead in leads:
            M = read[product](dt, lead, clCutoff, th, sizeTH, cltype, 1)
            print len(M),len(M[0])
            timeW=str(strDt.year)+str(strDt.month).zfill(2)+str(strDt.day).zfill(2)+'_'+str(strDt.hour).zfill(2)+'_'+str(lead).zfill(2)
            print timeW
            if M is not None:
                print dt, "  Lead: ", lead
                U1,S1,V1 = svd(M, full_matrices=False)
                d1=len(M); d2=len(S1)
                for i in range(d1):
                    print np.sum(M[i])
        
                x = np.array([[np.dot(M[i],V1[j]) for j in range(d2)] for i in range(d1)])
        
                clustering = scipy.cluster.hierarchy.ward(x)
                
                fig=plt.figure()
                scipy.cluster.hierarchy.dendrogram(clustering,color_threshold=0)
                plt.title('Dendrogram for Cluster {0}/{1} - {2}' .format(cl,cutoff,cltype))
                plt.savefig( "/mnt/user/soner.yorgun/SCENARIOS/ObjDetectCluster/HRRRE/Objectify/Plots/{0}/{1}/Dendogram2_cl{2}_cutoff{3}_{4}_size{5}_{6}_sub.png" .format(timeW,cltype,cl,cutoff,timeW,sizeTH,cltype))
                plt.close()
                assignments = scipy.cluster.hierarchy.fcluster(clustering, 0.8)
                ranks = rankClusters(clustering, assignments)
             
                scenario_db.test_write(conn, product, dt, lead, ranks, clCutoff, sizeTH, cltype)
        
        dt = dt + deltaDt
            
    conn.close()


