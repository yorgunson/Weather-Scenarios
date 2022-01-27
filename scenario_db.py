import sys
import MySQLdb
import pgdb

from time import strftime
from datetime import datetime

def get_conn() :
    
    hostname = 'fvs-anb3'
    username = 'nevsoper'
    dbname = 'trial_soner'
    password = 'nevsoper'

    conn = MySQLdb.connect(hostname,username,password,dbname)
    print conn

    return conn

def test_write(conn, product, dt, lead, ranks, clCutoff, sizeTH, cltype) :
    
    timeW=str(dt.year)+str(dt.month).zfill(2)+str(dt.day).zfill(2)+'_'+str(dt.hour).zfill(2)+'_'+str(lead).zfill(2)
    
    cl=clCutoff[0];cutoff=clCutoff[1]
    cur = conn.cursor()

    '''
    print dt
    SQL = ("REPLACE INTO {}_clusters (issue, lead) VALUES ('{}', {})".format(product, dt.isoformat(), lead))
    print SQL

    try: 
        cur.execute(SQL)
    except Exception as e:
        conn.rollback()

    SQL = ("SELECT id FROM {}_clusters WHERE issue='{}' AND lead={}".format(product, dt.isoformat(), lead))
    print SQL
     
    try: 
        cur.execute(SQL)
    except Exception as e:
        conn.rollback()
    '''    
    #cluster_id = cur.fetchone()
    #cluster_id=4

    for idx, members, mean, sdev in ranks:
        
        #SQL = ("INSERT INTO {}_cluster_{} VALUES ('{}', {}, {}, {}, {}, '{}', '{}')".format(product, cltype, members, mean, sdev, cl, cutoff, timeW,sizeTH))
        SQL = ("INSERT INTO {}_cluster_sub VALUES ('{}', {}, {}, {}, {}, '{}', '{}')".format(product, members, mean, sdev, cl, cutoff, timeW,sizeTH))
        print SQL
   
        try: 
            cur.execute(SQL)
        except Exception as e:
            conn.rollback()
            print e

#         if 'duplicate key' in e.args[0]:
#                 try:
#                     SQL = ("UPDATE afwa_clusters SET issue = '2015-5-5 13:00',  lead = 3, "
#                            "WHERE station = '%s' AND "
#                            " obs_time = '%s';") % (obs_tab, db_data['windDir'][n], db_data['windSpeed'][n], gust, stn, db_data['timeObs'][n])
#                     cur.execute(SQL)
# 
#                 except Exception:
#                     conn.rollback()
         
    conn.commit()
    cur.close()
#     conn.close()

def write_obs_data(db_data, obstype) :
    conn = get_conn()
    cur = conn.cursor()

    if obstype == 'smoothed' :
        obs_tab = 'smooth_cbvt_wind_obs'
    else :
        obs_tab = 'asos_5min_wind_obs'
        
    for n, stn in enumerate(db_data['stationName']) :
        if not db_data['windDir'][n] or not db_data['windSpeed'][n] :
            continue
        gust = db_data['windGust'][n]
        if gust == '' :
            gust = 'null' 

        if isinstance(db_data['timeObs'],float) :
            db_data['timeObs'] = strftime('%Y-%m-%d %H:%M', gmtime(db_data['timeObs'][n]))

        """try to update first - sometimes there are duplicates
        in the ASOS data so assume the last one is the one to
        persist in the database """

        try: 
            SQL = ("INSERT INTO %s "
                   "(station, obs_time, direction, speed, gust) "
                   "VALUES ('%s', '%s', %s, %s, %s );") %\
                   (obs_tab, stn, db_data['timeObs'][n], db_data['windDir'][n], db_data['windSpeed'][n], gust)
            cur.execute(SQL)
    
        except Exception as e1:
            conn.rollback()
            if 'duplicate key' in e1.args[0]:
                try:
                    SQL = ("UPDATE %s "
                           "SET direction = %s, "
                           " speed = %s, "
                           " gust = %s "
                           "WHERE station = '%s' AND "
                           " obs_time = '%s';") % (obs_tab, db_data['windDir'][n], db_data['windSpeed'][n], gust, stn, db_data['timeObs'][n])
                    cur.execute(SQL)

                except Exception:
                    conn.rollback()
        conn.commit()
                
    cur.close()
    conn.close()
    return


if __name__ == '__main__':
    conn = get_conn()
#     test_write(conn)
    conn.close
