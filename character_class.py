
import numpy as np


class EventInfo:
    def __init__(self, data, dt = 0.004):
        self._data = data
        self._dt = dt
    
    def badchannel(self, minVar = 1000, nmax = 250):

        self._size = np.shape(self._data)
    
        if self._size[0] >= 1:
            # set the minimum value of the variance of the signal
            #minVar  = 1000  
            V1  = list((self._data.var(axis = 0) <= minVar).nonzero()[0])
            # count peak numbers for each column, if peak number is very large, the data is not good
            peaknum = [len(np.where(np.absolute(val) >= 32000)[0]) for key, val in self._data.items()]
            V2 = [i for i, v in enumerate(peaknum) if v > nmax]
            # list the bad data channel  index
            V = V1 + V2
            if V:
                V = list(set(V))
            else: V = []
            # AICPicker to get the onset time
        else: V = [i for i in range(self._size[1])]
        return V 


    def Onset_time(self):
        V = self.badchannel()
        if len(V) <= 2:
            Temp_addrowTem = [float(format(self._AICPicker(val2),'.3f')) for key2, val2 in self._data.items()]
                
            # get the index of the time threshold
            time_threshold_index  = [i for i,j in enumerate(Temp_addrowTem) if (6 <= j or j <= 3)]
            for t in time_threshold_index: Temp_addrowTem[t] = 100
            
            if len(time_threshold_index) <= 2:
                addToRow = Temp_addrowTem
                #print(addToRow)
                #Common.printl(self.fatherPath, addToRow)
            else: 
                print('more than 2 signals have onset time out of range 3-6ms')
                addToRow = [i*5+10 for i in range(len(Temp_addrowTem))]
        else: 
            print('event has more than 2 bad signals')
            addToRow = [i*10+40 for i in range(self._size[1])]
            
        return addToRow

    def short_time_ch_info(self):
        picktime = self.Onset_time()
        min_t = min(picktime)
         
        if 3 <= min_t <= 6:
            mint = min_t
            ind_ch = picktime.index(min_t)
        else: 
            mint = 100
            ind_ch = 100
            print('signal with shortest onset time is bad')
            
        shorttimech = dict(min_time = mint, min_ind_ch = ind_ch)
        
        return shorttimech    


#===================================================================================================
        # private function
#======================================================================================================
    def _AICPicker(self,chdata):
    # set the parameters
        #self.dt = 0.004 # time step (unit:ms)
        data = chdata - np.mean(chdata)
        ind_peak = list(np.where(np.absolute(data) == np.max(np.absolute(data)))[0])
        k0 = ind_peak[0]
        # calculate the onset time with AIC Algorithm in window[0,k0]
        x = data[:k0+1]
        aicP1 = []
        if len(x):
           num = len(x)
           if num > 1:
               k = 1
               while k < num:
                   # calculate variance in first part
                   xLogVar1 = np.var(x[:k])
                   if xLogVar1 <= 0: xLogVar1 = 0
                   else: xLogVar1 = np.log(xLogVar1)
                   
                   # calculate variance in second part 
                   xLogVar2 = np.var(x[k:])
                   if xLogVar2 <= 0: xLogVar2 = 0
                   else: xLogVar2 = np.log(xLogVar2)
                   temp_aick = (k)*(xLogVar1) + (num-k-1)*(xLogVar2) 
                   aicP1.append(temp_aick)
                   k += 1
                   
           else: aicP1 = []
        else: aicP1 = []
        
        # find the position of the minimum
        if len(aicP1)>1:
            indlist = list(np.where(aicP1 == np.min(aicP1))[0])
            ind = indlist[0]+1
        else:
            ind = 0
            
        if ind:
            loc = (ind)*self._dt
        else:
            loc = 0
            
        return loc


#======================================================================================================
        #
#========================================================================================================

class Character(EventInfo):
           
    
    def AmpFre_FFT(self, data):
        
        Fs = 1000/self._dt
        #FFT
        N = len(data)
        Y = np.absolute(np.fft.fft(data))
        Amp = list(Y/(N/2))[:int(N/2)]
        Amp[0] = 0
        freq = list(np.fft.fftfreq(N, d=1/Fs))[:int(N/2)]
        
        return dict(freq = freq, Amp = Amp)
    
    def Amp_Fre_Character(self, Amp, freq):
        # calculate fre_peak, fre_centroid; fre_wpeak
        Amp_max = max(Amp)
        indfre = Amp.index(Amp_max)
        fre_peak_0 = freq[indfre] # unit: Hz
        fre_peak = fre_peak_0/1000 # unit: kHz
        inte1 = np.array(Amp)*np.array(freq)
        fre_centroid_0 = np.trapz(inte1)/np.trapz(np.array(Amp))
        fre_centroid = fre_centroid_0/1000 # unit: kHz
        fre_wpeak_0 = np.sqrt(fre_peak_0*fre_centroid_0)
        fre_wpeak = fre_wpeak_0/1000 # unit: kHz
        #outfre = [fre_peak, fre_centroid, fre_wpeak]
        
        # calculate the partial power in the frequency range
        # frequency range (0,5k),(5,10k),(10,15k),(15,20k),(20,125k)
        frerange = [0, 5, 10, 15, 20, 125]
        PartialPower = []
        partfre = np.ceil(np.array(frerange)*2*len(freq)*self._dt).astype(int)
        
        for ploop in range(len(frerange)-1):
            ppower = np.trapz(np.power(np.array(Amp[partfre[ploop]:partfre[ploop+1]]),2))
            PartialPower.append(ppower)
        Power = np.trapz(np.power(np.array(Amp),2))
            
        pppc = np.array(PartialPower)*100/Power
        
        outampfre = {'maxAmp_f': Amp_max, 
                     'fre_peak' :fre_peak, 'fre_centroid' : fre_centroid, 'fre_wpeak' : fre_wpeak,
                     'Power' : Power, 'PartialPower' : pppc}

        return outampfre
    
    def Amp_Time_Character(self, dmincol):
#        Fs = 1000/self._dt
        index = np.abs(dmincol).idxmax()
        AmpMax = dmincol[index]
        time_AmpMax = index*self._dt # unit ms
        Energy = np.trapz(dmincol**2) #original energy
        #[fre_peak,fre_centroid,fre_weak,Ampf_max,Power,pppc] = AmpFre2(col_loop, Fs)
        
        loc = self._AICPicker(dmincol)
        ind_loc = int(loc/self._dt)
        ind_end = int((2.5+loc)/self._dt + 1)
        d = np.array(list(dmincol)[ind_loc:ind_end])
        Energy25 = np.trapz(d**2) # energy in 2.5 ms
        zcx = (np.diff(np.sign(d)) != 0).sum() # zero crossing in 2.5 ms
        zcf = (zcx-1)/2.5 # zero crossing frequency (unit: kHz)
        
        time_rise  = (time_AmpMax - loc)*1000 # unit us
        RA = time_rise*1000/AmpMax  # unit us/V assume amplitude is mV in unit
        
        outamptime = {'maxAmp_t': AmpMax , 'time_peak': time_AmpMax,
                      'Energy':Energy, 'Energy25':Energy25, 'ZeroCrossf': zcf ,
                      'rise_time':time_rise, 'RA': RA}

        return outamptime




