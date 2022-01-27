import sys
sys.path.append('/mnt/user/soner.yorgun/utils/Scenarios/Execute')
from datetime import datetime, timedelta

from ObjDetectAtt_HRRRE import ObjDetectAtt
from Linkage import link
from Plot_Members import VARplot, OBJplot, OBJplot_bound, OBJplot_bound_sub
from ScreePlot import scree
from ClusterPlot import MultipleClust, SingleClust
from ClusterPlot_Members_Cmass import DecBound_Cmass
from cluster_eof_wholefield import run as clust_wf
from cluster_eof import run as clust_rg
from ClusterGrids import clGrids
from ObjCluster_SAL_v3 import exec_sal

#----------------------#
src='hrrre'
year='2016'
month='06'
day='04'#'16'
issue='15'
lead='12'#'04'
timeW=year+month+day+'_'+issue+'_'+lead
time=0 # The index of the time dimension of the object array. 0 if dealing with only one time
th=3.5 # Value Threshold to be used in defining objects
sizeTH=0 # Size Threshold to be used in deciding to keep or discard an object (<sizeTH discarded)
#----------------------#

##########################################
### INITIAL LOOK / REGIONAL CLUSTERING ###
##########################################

### First Objectize the field using the Region Growing Algorithm and Create the Atrribute Array
ObjDetectAtt(year,month,day,issue,lead,th)

### Create the lonkage matrix for the object (this is the preparation step for the clustering)
### This is where the size TH gets in, so each change in size threshold must start with this step
link(src,th,time,timeW,sizeTH)

### See how the full variable (without objectizing) looks like for all the members
VARplot(year,month,day,issue,lead,show='yes')

### See the screeplot to decide the total number of clusters
cutoff=input("Enter the Cluster Cutoff: ")
scree(src,th,time,timeW,sizeTH,cutoff,show='yes')

### See the Cmass plot of the resulting clusters for the given cutoff
### MultipleClust(src,th,timeW,sizeTH,cutoff,show='yes')
SingleClust(src,th,timeW,sizeTH,cutoff,show='yes')

### See the Cmass plot for each member overlaid on the decision boundary
DecBound_Cmass(src,th,timeW,sizeTH,cutoff,show='yes')

# Maybe see the Objects in each cluster?
ans=input("Wanna plot the cluster objects? (1:yes 0:no): ")

if ans==1:
    for i in range(4,5):#1,cutoff+1):
        print '*** Plotting Objects in Regional Cluster ', i,' ***'
        #OBJplot(src,th,(i,cutoff),timeW,sizeTH,gl='l',show='yes')
        #OBJplot_bound(src,th,(i,cutoff),timeW,sizeTH,gl='l',binary='no',show='yes')
        OBJplot_bound_sub(src,th,(i,cutoff),timeW,sizeTH,gl='l',binary='no',show='yes')
        
######################
### EOF CLUSTERING ###
######################

# First be a good boy and ask if they want this
ans=input("Wanna move on with the EOF Clustering? (1:yes 0:no): ")

if ans==1:
    
    dt=datetime(int(year),int(month),int(day),int(issue))
    enddt=datetime(int(year),int(month),int(day),int(issue)+1)
    
    # First EOF Clustering to the whole field
    #clust_wf(src, dt, enddt, [int(lead)], (99,99), th,0)
    
    # Then the regional clustering
    cutoff=input("Enter the Cluster Cutoff for EOF Clustering: ")
    clGrids(src,th,cutoff,timeW,sizeTH)
    
    for i in range(4,5):#1,cutoff+1)
        clust_rg(src, dt, enddt, [int(lead)], (i,cutoff), th, sizeTH, cltype='bin')
        
######################
###      SAL       ###
######################

# First be a good boy and ask if they want this
ans=input("Wanna move on with the SAL? (1:yes 0:no): ")

if ans==1:
    
    exec_sal(src,th,cutoff,time,timeW,sizeTH,show='yes')