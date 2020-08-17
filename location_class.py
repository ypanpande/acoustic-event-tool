
from character_class import EventInfo
import numpy as np


class Location(EventInfo):
    SX = [5, 0, 505, 550, -1650, -1650]
    SY = [1555,0, 1482.5,82.5,1552.5, -2.5]
    
    V0 = [4000, 2500]
    V45 = [4000, 2900]
    V01 = [4000, 2650]
    V23 = [4000, 2000]
    
    MAXRES = 0.05
    
#================================================================================================
# Sequential 6 sensors
#==================================================================================================

    def Sequential6s(self, block = 10):
        ##set parameters
        dobs = self.Onset_time()
        
        # sensor coordinates (xi, yi)
        #sx = [5, 0, 505, 550, -1650, -1650];
        #sy = [1555,0, 1482.5,82.5,1552.5, -2.5];
        sx = self.SX
        sy = self.SY
        #velocity component
        #v0 = [4000, 2500];
        v0 = self.V0
        
        N = len(sx); # number of sensor
        M = 3; # number of model parameter [dx,dy,dt]
        
        # stop criterion res < epsilon = 1.0e-2;
        #epsilon=1.0e-2;

        # delta time to channel 1
    #    delta = []
    #    for dt_loop in dobs:
    #        delta_temp = dt_loop - dobs[1]
    #        delta.append(delta_temp)
    #        
    #    # get the indexs of deltaT threshold
    #    threshold_index = [i for i, value in enumerate(delta) if (value <= -1.2 or value >= 1.2)]
        threshold_index = self._deltaT(dobs)
        if not len(threshold_index):
            #searching area from (-2000,2000) to (1200,-400) and the block is 20mm*20mm
            #block = 10;
            #areatop = [-2000,2000]; areabottom = [1200,-400];
            if index == 0:
                areatop = [-850,2000]
                areabottom = [280,740]
            elif index == 1:
                areatop = [-850,800]
                areabottom =  [280,-400]
            elif index == 2:
                areatop = [220,2000]
                areabottom = [1200,740]
            elif index == 3:
                areatop = [220,800]
                areabottom = [1200,-400]
            elif index == 4:
                areatop = [-2000,2000]
                areabottom = [-800,740]
            else:
                areatop = [-2000,800]
                areabottom = [-800,-400]
            
            hornum = int(np.round((areabottom[0] - areatop[0])/block))
            vernum = int(np.round((areatop[1] - areabottom[1])/block))
                


                        # calculate time to sensors
                        dcal[sensornum] = distance/vel
                        
                    #calculate the time difference between calculation and observation using r_i = (t_oi - sum(t_oi)/n)
                    dd = [0]*N
                    for sensornum2 in range(N):
                        dd[sensornum2] = (dobs[sensornum2] - sum(dobs)/N) - (dcal[sensornum2] - sum(dcal)/N)
                        
                        # calculate the event rms
                    rmsdd[j][i] = np.sqrt(np.dot(np.array(dd),np.array(dd).T)/(N-M))
                    t0[j][i] = sum(dobs)/N - sum(dcal)/N
            
            # find the index and value of the mininum rms of delta time
            vmin = rmsdd.min()
            minindex = np.unravel_index(rmsdd.argmin(),rmsdd.shape)
            # calculate the position
            xmin = areatop[0] + block/2 + minindex[0]*block
            ymin = areabottom[1] + block/2 + minindex[1]*block
            t0min = t0[minindex[0]][minindex[1]]
            aver_dd = np.sqrt((N-M)*(vmin**2)/N)
            addToRow = [xmin, ymin, t0min, vmin, aver_dd, t_ini, index]
            # check whether the result is bad
            if vmin > self.MAXRES:
                print('Seq6s: the minimum RES is {}, the result is bad'.format(vmin))
                addToRow = [None, None, None, vmin, aver_dd, t_ini, index]
    

            
        else: 
            print('Seq6s: not all {} sensor are working.'.format(N))
            addToRow = [None, None, None, None, None, None, None]
            
        keys = ['x','y','t0','res','aver_res','tmin','ch_index']
        
        outSeq6s = {item: addToRow[i] for i, item in enumerate(keys)}
        
        return  outSeq6s

#===============================================================================================
        # Sequential 4 sensor
#=============================================================================================
    def Sequential4s(self, block =10):
            ##set parameters
        # sensor coordinates (xi, yi)
        # sx=[5, 0, 505, 550];
        # sy=[1555,0, 1482.5,82.5];
        dobs_temp = self.Onset_time()
        
        #sx_all = [5, 0, 505, 550, -1650, -1650];
        #sy_all = [1555,0, 1482.5,82.5,1552.5, -2.5];
        sx_all = self.SX
        sy_all = self.SY
        #velocity component
        #v45 = [4000, 2900]
        #v01 = [4000, 2650]
        #v23 = [4000, 2000]
        v45 = self.V45
        v01 = self.V01
        v23 = self.V23
        
        N = 4; # number of sensor
        M = 3; # number of model parameter [dx,dy,dt]
        
        # stop criterion res < epsilon = 1.0e-2;
        #epsilon=1.0e-2;
        
        #clean the empty result and the bad results
        #colres = 5; # the column number of rms in the dataset
        #maxres = 0.05; # the threshold of rms
        
        # the onset time 
        #dobs = [4.032, 3.956, 4.136, 4.116, 3.864, 3.736]
        #dobs_temp =[4.204, 4.112, 4.172, 4.044, 4.52, 4.476]
        # sensor of the first arrival
        t_ini = min(dobs_temp)
        index = dobs_temp.index(t_ini)
        # select 4 sensor
        if index == 0:
            areatop = [-850,2000]
            areabottom = [280,740]
            sx = sx_all[:2] + sx_all[4:]
            sy = sy_all[:2] + sy_all[4:]
            dobs = dobs_temp[:2] + dobs_temp[4:]
            v0 = v01
        elif index == 1:
            areatop = [-850,800]
            areabottom =  [280,-400]
            sx = sx_all[:2] + sx_all[4:]
            sy = sy_all[:2] + sy_all[4:]
            dobs = dobs_temp[:2] + dobs_temp[4:]
            v0 = v01
        elif index == 2:
            areatop = [220,2000]
            areabottom = [1200,740]
            sx = sx_all[:4]
            sy = sy_all[:4]
            dobs = dobs_temp[:4]
            v0 = v23
        elif index == 3:
            areatop = [220,800]
            areabottom = [1200,-400]
            sx = sx_all[:4]
            sy = sy_all[:4]
            dobs = dobs_temp[:4]
            v0 = v23
        elif index == 4:
            areatop = [-2000,2000]
            areabottom = [-800,740]
            sx = sx_all[:2] + sx_all[4:]
            sy = sy_all[:2] + sy_all[4:]
            dobs = dobs_temp[:2] + dobs_temp[4:]
            v0 = v45
        else:
            areatop = [-2000,800]
            areabottom = [-800,-400]
            sx = sx_all[:2] + sx_all[4:]
            sy = sy_all[:2] + sy_all[4:]
            dobs = dobs_temp[:2] + dobs_temp[4:]
            v0 = v45
        
        # delta time to channel 1
    #    delta = []
    #    for dt_loop in dobs:
    #        delta_temp = dt_loop - dobs[1]
    #        delta.append(delta_temp)
    #        
    #    # get the indexs of deltaT threshold
    #    threshold_index = [i for i, value in enumerate(delta) if (value <= -1.2 or value >= 1.2)]
        threshold_index = self._deltaT(dobs)
        if not len(threshold_index):
            #searching area from (-2000,2000) to (1200,-400) and the block is 20mm*20mm
            block = 10;
            #areatop = [-2000,2000]; areabottom = [1200,-400];
        
            
            hornum = int(np.round((areabottom[0] - areatop[0])/block))
            vernum = int(np.round((areatop[1] - areabottom[1])/block))
                
            rmsdd = np.ones((hornum, vernum))
            t0 = np.zeros((hornum, vernum))
            for i in range(vernum):
                for j in range(hornum):
                    x = areatop[0] + block/2 + j*block
                    y = areabottom[1] + block/2 + i*block
                    a = [x,y]
                    
                    dcal = [0]*N
                    for sensornum in range(N):
                        dx = a[0] - sx[sensornum]
                        dy = a[1] - sy[sensornum]
                        #distance to sensors
                        distance = np.sqrt(dx**2 + dy**2)
                        weightv = np.absolute([dx,dy])
                        velweight = v0*weightv
                        vel = sum(velweight)/sum(weightv)
                        # calculate time to sensors
                        dcal[sensornum] = distance/vel
                        
                    #calculate the time difference between calculation and observation using r_i = (t_oi - sum(t_oi)/n)
                    dd = [0]*N
                    for sensornum2 in range(N):
                        dd[sensornum2] = (dobs[sensornum2] - sum(dobs)/N) - (dcal[sensornum2] - sum(dcal)/N)
                        
                        # calculate the event rms
                    rmsdd[j][i] = np.sqrt(np.dot(np.array(dd),np.array(dd).T)/(N-M))
                    t0[j][i] = sum(dobs)/N - sum(dcal)/N
            
            # find the index and value of the mininum rms of delta time
            vmin = rmsdd.min()
            minindex = np.unravel_index(rmsdd.argmin(),rmsdd.shape)
            # calculate the position
            xmin = areatop[0] + block/2 + minindex[0]*block
            ymin = areabottom[1] + block/2 + minindex[1]*block
            t0min = t0[minindex[0]][minindex[1]]
            aver_dd = np.sqrt((N-M)*(vmin**2)/N)
            addToRow = [xmin, ymin, t0min, vmin, aver_dd, t_ini, index]
            
            if vmin > self.MAXRES:
                print('Seq4s: the minimum RES is {}, the result is bad'.format(vmin))
                addToRow = [None, None, None, vmin, aver_dd, t_ini, index]
    
            else:
                print('Seq4s: the result RES is {}'.format(vmin))
                #print(addToRow)
                #Common.printl(self.fatherPath, addToRow)
            
        else: 
            print('Seq4s: not all {} sensor are working.'.format(N))
            addToRow = [None, None, None, None, None, None, None]
            
        keys = ['x','y','t0','res','aver_res','tmin','ch_index']
        
        outSeq4s = {item: addToRow[i] for i, item in enumerate(keys)}
        
        return  outSeq4s
        
#====================================================================================================
#      Geiger 6 sensors
#==================================================================================================        

    def Geiger6s(self, iter_num = 100):
        ##set parameters
        # sensor coordinates (xi, yi)
        # sx=[5, 0, 505, 550];
        # sy=[1555,0, 1482.5,82.5];
        dobs = self.Onset_time()
        #sx = [5, 0, 505, 550, -1650, -1650];
        #sy = [1555,0, 1482.5,82.5,1552.5, -2.5];
        sx = self.SX
        sy = self.SY
        #velocity component
        #v0 = [4000, 2500];
        v0 = self.V0
        
        N = len(sx); # number of sensor
        M = 3; # number of model parameter [dx,dy,dt]
        
        # stop criterion res < epsilon = 1.0e-2;
        epsilon=1.0e-2;
        
        #clean the empty result and the bad results
        #colres = 5; # the column number of rms in the dataset
        #maxres = 0.05; # the threshold of rms
        
        # the onset time 
        #dobs = [4.032, 3.956, 4.136, 4.116, 3.864, 3.736]
        #dobs =[4.204, 4.112, 4.172, 4.044, 4.52, 4.476]
        #sensor of the first arrival
        t_ini = min(dobs)
        index = dobs.index(t_ini)
        
        # initial guess
        mest = [sx[index]+np.random.randint(100), sy[index]+np.random.randint(100), t_ini-0.05]
        # delta time to channel 1
    #    delta = []
    #    for dt_loop in dobs:
    #        delta_temp = dt_loop - dobs[1]
    #        delta.append(delta_temp)
    #        
    #    # get the indexs of deltaT threshold
    #    threshold_index = [i for i, value in enumerate(delta) if (value <= -1.2 or value >= 1.2)]
        threshold_index = self._deltaT(dobs)
        if not len(threshold_index):
            iter1 = 0
            while iter1 < iter_num:
            #for iter in range(100):
                G = np.array([[0] * M] *N)
                dpre = [0]*N
                
                for j in range(N): # loop over stations
                    dx = mest[0] - sx[j]
                    dy = mest[1] - sy[j]
                    
                    r = np.sqrt(dx**2 + dy**2)
                    
                    weightv = np.absolute([dx,dy])
                    velweight = v0*weightv
                    vel = sum(velweight)/sum(weightv)
                    
                    dpre[j] = r/vel + mest[2]
                    G[j][0] = dx/(r*vel)
                    G[j][1] = dy/(r*vel)
                    G[j][2] = 1
                    
                    # solve with dampled least squares
                dd = np.subtract(dobs,dpre).T
                try:
                    #dm = np.dot(np.linalg.inv(np.dot(G.T, G)), np.dot(G.T, dd))
                    dm = np.linalg.lstsq(G, dd, rcond = None)[0]
                    
                    mest = list(np.add(mest, dm))
                    
                    res = np.sqrt(np.dot(dd.T, dd)/(N-M))
                    
                    if res <= epsilon: break
                except:
                    res = 1
                    break
                
                iter1 +=1
            aver_dd = np.sqrt((N-M)*(res**2)/N)
            addToRow = [mest[0], mest[1], mest[2], res, aver_dd, t_ini, index]
            
            # check whether the result is bad
            if res > self.MAXRES:
                print('Geiger6s: the minimum RES is {}, the result is bad'.format(res))
                addToRow = [None, None, None, res, aver_dd, t_ini, index]
    
            else:
                print('Geiger6s: the result RES is {}'.format(res))
                #print(addToRow)
                #Common.printl(self.fatherPath, addToRow)
            
        else: 
            print('Geiger6s: not all {} sensor are working.'.format(N))
            addToRow = [None, None, None, None, None, None, None]
            
        keys = ['x','y','t0','res','aver_res','tmin','ch_index']
        
        outGeige6s = {item: addToRow[i] for i, item in enumerate(keys)}
        
        return  outGeige6s

#===============================================================================================
# Geiger 4 sensors
#====================================================================================================

    def Geiger4s(self, iter_num = 100):
            ##set parameters
        # sensor coordinates (xi, yi)
        # sx=[5, 0, 505, 550];
        # sy=[1555,0, 1482.5,82.5];
        #sx_all = [5, 0, 505, 550, -1650, -1650];
        #sy_all = [1555,0, 1482.5,82.5,1552.5, -2.5];
        dobs_temp = self.Onset_time()
        
        sx_all = self.SX
        sy_all = self.SY       
        #velocity component
        #v0 = [4000, 2500];
        #v45 = [4000, 2900];
        #v01 = [4000, 2650];
        #v23 = [4000, 2000];
        v45 = self.V45
        v01 = self.V01
        v23 = self.V23        
        
        N = 4; # number of sensor
        M = 3; # number of model parameter [dx,dy,dt]
        
        # stop criterion res < epsilon = 1.0e-2;
        epsilon=1.0e-2;
        
        #clean the empty result and the bad results
        #colres = 5; # the column number of rms in the dataset
        #maxres = 0.05; # the threshold of rms
        
        # the onset time 
        #dobs_temp = [4.032, 3.956, 4.136, 4.116, 3.864, 3.736]
        #dobs_temp =[4.204, 4.112, 4.172, 4.044, 4.52, 4.476]
        # initial guess
        t_ini = min(dobs_temp)
        index = dobs_temp.index(t_ini)
        
        mest = [sx_all[index]+np.random.randint(100), sy_all[index]+np.random.randint(100), t_ini-0.05]
        
        ### select 4 sensors
        if index == 0 or index == 1:
            sx = sx_all[:2] + sx_all[4:]
            sy = sy_all[:2] + sy_all[4:]
            dobs = dobs_temp[:2] + dobs_temp[4:]
            v0 = v01
        elif index == 2 or index == 3:
            sx = sx_all[:4]
            sy = sy_all[:4]
            dobs = dobs_temp[:4]
            v0 = v23
        else:
            sx = sx_all[:2] + sx_all[4:]
            sy = sy_all[:2] + sy_all[4:]
            dobs = dobs_temp[:2] + dobs_temp[4:]
            v0 = v45
            
            
        # delta time to channel 1
    #    delta = []
    #    for dt_loop in dobs:
    #        delta_temp = dt_loop - dobs[1]
    #        delta.append(delta_temp)
    #        
    #    # get the indexs of deltaT threshold
    #    threshold_index = [i for i, value in enumerate(delta) if (value <= -1.2 or value >= 1.2)]
        threshold_index = self._deltaT(dobs)
        if not len(threshold_index):
            iter1 = 0
            while iter1 < iter_num:
            #for iter in range(100):
                G = np.array([[0] * M] *N)
                dpre = [0]*N
                
                for j in range(N): # loop over stations
                    dx = mest[0] - sx[j]
                    dy = mest[1] - sy[j]
                    
                    r = np.sqrt(dx**2 + dy**2)
                    
                    weightv = np.absolute([dx,dy])
                    velweight = v0*weightv
                    vel = sum(velweight)/sum(weightv)
                    
                    dpre[j] = r/vel + mest[2]
                    G[j][0] = dx/(r*vel)
                    G[j][1] = dy/(r*vel)
                    G[j][2] = 1
                    
                    # solve with dampled least squares
                dd = np.subtract(dobs,dpre).T
                try:
                    #dm = np.dot(np.linalg.inv(np.dot(G.T, G)), np.dot(G.T, dd))
                    dm = np.linalg.lstsq(G, dd, rcond = None)[0]
                    
                    mest = list(np.add(mest, dm))
                    
                    res = np.sqrt(np.dot(dd.T, dd)/(N-M))
                    
                    if res <= epsilon: break
                except:
                    res = 1
                    break
                
                iter1 +=1
            aver_dd = np.sqrt((N-M)*(res**2)/N)
            addToRow = [mest[0], mest[1], mest[2], res, aver_dd, t_ini, index]
            
            # check whether the result is bad
            if res > self.MAXRES:
                print('Geiger4s: the minimum RES is {}, the result is bad'.format(res))
                addToRow = [None, None, None, res, aver_dd, t_ini, index]
    
            else:
                print('Geiger4s: the result RES is {}'.format(res))
                #print(addToRow)
                #Common.printl(self.fatherPath, addToRow)
            
        else: 
            print('Geiger4s: not all {} sensor are working.'.format(N))
            addToRow = [None, None, None, None, None, None, None]
            
        keys = ['x','y','t0','res','aver_res','tmin','ch_index']
        
        outGeige4s = {item: addToRow[i] for i, item in enumerate(keys)}
        
        return  outGeige4s
        
#==================================================================================================
# private function
#=================================================================================================
    
    def _deltaT(self, dobs):
        delta = [v - dobs[1] for v in dobs]
            # get the indexs of deltaT threshold
        threshold_index = [i for i, value in enumerate(delta) if (value <= -1.2 or value >= 1.2)]
        
        return threshold_index
