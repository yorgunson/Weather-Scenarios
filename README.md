# The use of weather scenarios from convective-allowing ensembles to convey forecast uncertainty

-Decision makers often use the mean value (and the spread) from an ensemble 

-Ensembles contain far more information than simply their mean and spread

-Decision makers could use this information to determine a National Air Space (NAS) ‘plan B’ that mitigates multiple weather scenarios

-A set of unique forecast solutions can be clustered into a most likely outcome, as well as second most likely outcome

Code Structure
--------------

This repository contains the pyhton codes to extract weather scenarios from weather model ensembles using two consecutive clustering applications: 
1) k-means clustering to separate weather regions
2) k-means clustering on the Principal Components to separate weather cores


The main code is Execute_Objectize.py

Below are each of these codes and their brief explanations.

ObjDetectAtt_HRRRE.py: This code does the initial work on identification of objects from the field given a threshold, and stores object information and attributes as numpy arrays. The output arrays are:

•	Objects_hrrre_{threshold value}th_{time}.npy (this one stores ensemble member name, object labels, object values, the raw field itself)
•	Attrib_hrrre_{threshold value}th_{time}.npy (this one stores object area, object center of mass, object mean value, object max value (value is VIL in this case)) 

Linkage.py: This code creates the linkage matrix for clustering using Wards method. I separated it because it can take time in case of large datasets and I wanted to do it once and then play with the results later. It outputs two arrays:

•	Linkage_{source}_{threshold value}th_{time}_size{size threshold}.npy (this one stores the linkage matrix to be used for clustering)
•	CmassMember_{source}_{threshold value}th_{time}_size{size threshold}.npy (this one stores the centers of mass of each object stratified my ensemble member. Used mainly for plotting later) 

Plot_Members.py: Contains several plotting functions.

ScreePlot.py: This code specifically plots the scree plot showing intercluster distance with respect to the partition number. The main code also asks for a cutoff value for the number of partitions, and this code shows that cutoff as a line on the plot.

ClusterPlot_Members_Cmass.py: This code plots the centers of mass of each member (on a single plot) overlaid on the decision boundary decided by the cutoff value given for the scree plot.

cluster_eof.py: The code that computes the EOF clustering

ObjCluster_SAL_v3.py: This code computes the SAL values and make comparisons between members.

