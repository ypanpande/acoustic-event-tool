

import pandas as pd
import datetime
import numpy as np
import math

def main():
    filename = 'D://Pywork//Pytest_1//Test files//Acc_ROSEM-B_01_20181015_151102_000000043.rcfd.csv'
    timepoint = '15.10.2018 16:10:56.570000'
    accdata = pd.read_csv(filename ,delimiter = ';',decimal = ',')
    accdata['time'] = pd.to_datetime(accdata['time'],format = '%Y-%m-%d %H:%M:%S.%f') 
    df = ACC(accdata, datetime.datetime.strptime(timepoint,'%d.%m.%Y %H:%M:%S.%f'))
    f = df.get_sub_acc_value()
    print(f)
    
class ACC:
    def __init__(self, accdata, timepoint, timerange = 5):
        self._data = accdata
        self._timepoint = timepoint
        self._starttime = timepoint - datetime.timedelta(seconds = timerange)
        self._endtime = timepoint + datetime.timedelta(seconds = timerange) 
    def get_sub_acc(self):
        tmin = self._data['time'].min()
        tmax = self._data['time'].max()
        if tmin > self._starttime:
            dt = tmin - self._starttime
            return self._data.loc[self._data['time'] < (self._endtime + dt)]
        elif tmax < self._endtime:
            dt = self._endtime - tmax
            return self._data.loc[self._data['time'] > (self._starttime - dt)]
        else:
            return self._data.loc[(self._data['time'] > self._starttime) &  (self._data['time'] < self._endtime)]
    
    def get_sub_acc_value(self):
        subacc = self.get_sub_acc()
        if len(subacc): 
            neartime = sorted(subacc['time'], key = lambda x: abs(x - self._timepoint))[0]
            point_acc = subacc.loc[subacc['time'] == neartime]
    
            az_max = subacc['az'].max()
            az_min = subacc['az'].min()
            az0 = (az_max + az_min)/2
            g2 = az_max - az_min
            if (g2 > 1.7) & (g2 < 2.3):
                rot = 1
                if ((float(point_acc['az']) - az0) >= -1)&((float(point_acc['az']) - az0) <= 1):
                    pitch_angle0 = 180/math.pi*np.arccos(float(point_acc['az']) - az0)
                else:
                    pitch_angle0 = 180
            else:
                rot = 0
                if (float(point_acc['az']) >= -1) & (float(point_acc['az']) <= 1):
                    pitch_angle0 = 180/math.pi*np.arccos(float(point_acc['az']))
                else:
                    pitch_angle0 = 180
            
            if float(point_acc['ax']) >= float(point_acc['ay']):
                pitch_angle = pitch_angle0
            else:
                pitch_angle = 360 - pitch_angle0
        
        else:
            print('event time is out of range, cannot get acc info')
            pitch_angle = None
            rot = None
            neartime = None
            az0 = None
            point_acc= dict(ax = 2, ay = 2, az = 2)
        return pitch_angle, rot, neartime, az0, float(point_acc['ax']), float(point_acc['ay']), float(point_acc['az'])

if __name__ == '__main__': main()