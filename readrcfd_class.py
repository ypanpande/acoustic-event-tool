import struct
#import codecs
from binascii import hexlify
#from codecs import encode  # alternative
#import sys
import os, ntpath
import pandas as pd
import datetime

import collections
import numpy as np
# Blocktag:start 
# BlockIdentifier: start + 2
# BlockVersion:    start + 4
# ParameterLength: start + 6 
# DataLength:      start + 8


# Channel:         
# RmainChannelCount:6
# ChannelTriggerBit:0000
## FiberOK:0000
# MeasurementCount:990
## TimeStamp:1516812224
# MilliSec:172

def main():
    f = "D://Pywork//Pytest_1//Test files//ROSEM-B_01_20180608_072329_000000001.rcfd"

    rcfd = Read_rcfd(f)
#    rcfd.write_to_csvs("C://Users//Teletronic//Desktop")

    data = rcfd.get_all_data_ODT()
    print(data.values)
    rcfd.ODT_write_to_csv(folder_path = "D://Pywork//Pytest_1//Test files//")
#    print(data.keys())
	# print(data["990"]["CH:0"])

class Read_rcfd():
    def __init__(self, f):
        with open(f, mode='rb') as file: # b is important -> binary
            self.fileContent = file.read()			

        self.start = 64
        self.filesize = os.path.getsize(f)
        self.savef = ntpath.basename(f)[0: -5]
        
#==============================================================================
    # AES block output
#==============================================================================
# get output fold name
    def get_outputfolder_name(self):
        return self.savef 

# get time for filename
    def get_filename(self):
        return "[" + str(self.get_MeasurementCount(self.start + 24)) + "]_" + str(self.get_Time(self.start + 28).strftime('%d_%m_%Y_%H_%M_%S_%f'))


# get all the data in dictionary{main_key: {CH0: data}}
    def get_all_data(self):
        rcfd_data = dict()
        while self.start < self.filesize:
            if (self.get_Block_header(self.start) == "5aa5") & (self.get_Block_header(self.start +2) == "0001"):
                main_key = self.get_filename()
                main_value = self.get_channel_data()
                rcfd_data[main_key] = main_value
            else: self.start = self.get_next_block_position(self.start)	
        self.start = 64
        return rcfd_data



    def write_to_csvs(self, folder_path = ""):
        path1 = os.path.join(folder_path, self.savef)
        if not os.path.exists(path1): os.makedirs(path1)
        while self.start < self.filesize:
            if (self.get_Block_header(self.start) == "5aa5") & (self.get_Block_header(self.start +2) == "0001"):
                filename = self.get_filename()
                csvfile = self.get_channel_data()
                self.write_to_csv(csvfile, filename, folder_path)
            else: self.start = self.get_next_block_position(self.start)	
        self.start = 64

    def write_to_csv(self,csvfile, filename, folder_path = ""):
        df = pd.DataFrame(csvfile, columns = csvfile.keys())
        df.to_csv(os.path.join(folder_path, self.savef, str(filename) + '.csv'), decimal = ',', sep = ';', index = False)	
        
# =============================================================================
#   ODA block output
# =============================================================================
        
# get all the acceleration data in pd.DataFrame 
    def get_all_data_ODA(self):
        rcfd_data_A = pd.DataFrame()
        while self.start < self.filesize:
            if (self.get_Block_header(self.start) == "5aa5") & (self.get_Block_header(self.start +2) == "0002"):
                #rcfd_data_A.extend(self.get_ODA_data())
                rcfd_data_A = rcfd_data_A.append(self.get_ODA_data(), ignore_index = True)
#                print(rcfd_data_A.shape)
            else: 
                self.start = self.get_next_block_position(self.start)
                
        self.start = 64
        return rcfd_data_A
    
    def ODA_write_to_csv(self,folder_path = ""):
        path1 = os.path.join(folder_path, 'Acceleration')
        if not os.path.exists(path1): os.makedirs(path1)
        #csvfile = self.get_all_data_ODA()
        df = self.get_all_data_ODA()
        #df = pd.DataFrame(csvfile, columns = ['time', 'ax', 'ay', 'az'])
        df.to_csv(os.path.join(folder_path, 'Acceleration', 'Acc_'+ self.savef + '.csv'), decimal = ',', sep = ';', index = False)

#==============================================================================
#        ODT block output
#==============================================================================
# get all the temperature data in pd.DataFrame()

    def get_all_data_ODT(self):
        rcfd_data_T = pd.DataFrame()
        while self.start < self.filesize:
            if (self.get_Block_header(self.start) == "5aa5") & (self.get_Block_header(self.start +2) == "0003"):
                rcfd_data_T = rcfd_data_T.append(self.get_ODT_data(), ignore_index = True)
            else: 
                self.start = self.get_next_block_position(self.start)
        self.start = 64
        return rcfd_data_T        
        
    def ODT_write_to_csv(self, folder_path = ""):    
        path1 = os.path.join(folder_path, 'Temperature')
        if not os.path.exists(path1): os.makedirs(path1)
#        csvfile = self.get_all_data_ODT()
        df = self.get_all_data_ODT()
#        df = pd.DataFrame(csvfile,columns = ['time', 'T1', 'T2', 'T3'])
        df.to_csv(os.path.join(folder_path, 'Temperature', 'Tc_'+ self.savef + '.csv'), decimal = ',', sep = ';', index = False)


# =============================================================================
# private methods~~~~~~~~~~~~private methods~~~~~~~~~~~~~~~~private methods~~~~~~~~~~~~~~~~~~~~private 
#==============================================================================
    def get_channel_data(self):
        channels = dict()
        MeasurementCount = self.get_MeasurementCount(self.start + 24)
        new_MeasurementCount = self.get_MeasurementCount(self.start + 24)
        while MeasurementCount == new_MeasurementCount:
            key = str(self.get_para(self.start + 10)) # get channel name
            channels["CH:" + key] = self.getdata(self.get_para(self.start + 8), self.start + 38)	

            self.start = self.get_next_block_position(self.start)
            if self.start < self.filesize:
                new_MeasurementCount = self.get_MeasurementCount(self.start + 24)			
            else: break

        return channels

        
    def get_next_block_position(self, Block_at_FilePos = 64):
       # start + header + ParameterLength + DataLength
       return Block_at_FilePos + 10 + self.get_para(Block_at_FilePos + 6) + self.get_para(Block_at_FilePos + 8)	


# Blocktag:start 
# BlockIdentifier: start + 2
# BlockVersion:    start + 4
    def get_Block_header(self, data_start = 64):   
        a = self.fileContent[data_start:data_start+2]
        b = struct.pack('<h', *struct.unpack('>h', a))
        return str(hexlify(b), 'utf-8')


# get all other parameters
    def get_para(self, data_start = 74):   
        a = self.fileContent[data_start:data_start+2]
        b = struct.pack('<h', *struct.unpack('>h', a))
        return int(str(hexlify(b), 'utf-8'), 16)


# # MeasurementCount 
    def get_MeasurementCount(self, data_start = 64 + 24):   
        a = self.fileContent[data_start:data_start+4]
        b = struct.pack('<l', *struct.unpack('>l', a))
        return int(str(hexlify(b), 'utf-8'), 16)

#TimeStamp
    def get_TimeStamp(self, data_start = 64 + 28):
        a = self.fileContent[data_start:data_start+8]
#        swap_data = bytearray(a)
#        swap_data.reverse()
        swap_data = struct.pack('<q', *struct.unpack('>q', a))
        return int(str(hexlify(swap_data), 'utf-8'), 16)
#        return datetime.datetime.utcfromtimestamp(t)

#MilliSec
    def get_MilliSec(self, data_start = 64 + 36):
        a = self.fileContent[data_start:data_start+2]
        b = struct.pack('<h', *struct.unpack('>h', a))
        return int(str(hexlify(b), 'utf-8'), 16)
    
#Time
    def get_Time(self, data_start = 64 + 28):
        t1 = self.get_TimeStamp(data_start)
        t2 = self.get_MilliSec(data_start + 8)        
        t = float(str(t1)+'.'+str(t2).zfill(3))
        return datetime.datetime.utcfromtimestamp(t)
    
#data
    def getdata(self, data_len = 16384, data_start = 64 + 38):
        a = self.fileContent[data_start: data_start + data_len]
        d_list = []
        for ele in range(int(data_len/2)):
            b = struct.pack('<h', *struct.unpack('>h', a[2*ele: 2*ele + 2]))
            x = int(str(hexlify(b), 'utf-8'), 16)
            if x > 0x8000:
                x = x - 0x10000 + 1
            d_list.append(x)
        return d_list


    def getdata_u(self, data_len = 16384, data_start = 64 + 38):
        a = self.fileContent[data_start: data_start + data_len]
        d_list = []
        for ele in range(int(data_len/2)):
            b = struct.pack('<h', *struct.unpack('>h', a[2*ele: 2*ele + 2]))
            x = int(b.hex(), 16)
            v = [ele, self.get_code_value(x), self.get_acc_value(x)]
#            if x > 0x8000:
#                x = x - 0x10000 + 1
            d_list.append(v)
        return d_list
# =============================================================================
# get ODA data from one block
    def get_ODA_data(self):
        data_list = self.getdata_u(self.get_para(self.start + 8), self.start + 10)
        group_data = collections.defaultdict(list)
        for v in data_list:
            group_data[v[1]].append([v[0],v[2]]) # group data by code_value 00, 01, 10, 11
            
        time_position = np.array([i[0] for i in group_data[0]])
        time_data_position = np.array([i[1] for i in group_data[0]])
        
        time_position_group = [i for i in np.split(time_position,np.where(np.diff(time_position) != 1)[0]+1)
                                if len(i) == 6]
        time_data_group = [i for i in np.split(time_data_position,np.where(np.diff(time_position) != 1)[0]+1)
                                if len(i) == 6]
        
        time_series = [self.get_time_value(list(i)) for i in time_data_group]
        
        a01_position, a01_series = self.get_adata_position_value(group_data[1])
        a10_position, a10_series = self.get_adata_position_value(group_data[2])
        a11_position, a11_series = self.get_adata_position_value(group_data[3])
#        print(len(a01_series),len(a10_series),len(a11_series))
        time_data = []
        index = []
        for k, v in enumerate(time_series):
            if (k==0) & (time_position_group[0][0] != 0):
                data_before_time = time_position_group[0][0]
#                print('before0:', data_before_time)
                if data_before_time % 3 == 0:
                    row_num = data_before_time//3
                    for i in range(row_num):
                        time_data.append((time_series[0] - datetime.timedelta(milliseconds = 10)*(row_num - i)).strftime('%d.%m.%Y %H:%M:%S.%f'))                
                    index.extend([j for j in range(time_position_group[0][0])])
#                    print('time length:',len(time_data))
#                    print('3data length:',len(index))
                #else:
                    
                    
            else:
                if k == (len(time_series) - 1):
                    data_dis = a11_position[-1] - time_position_group[-1][-1]
#                    print('after',k,':',data_dis)
                else:
                    data_dis = time_position_group[k+1][0]-time_position_group[k][0]-6
                if data_dis % 3 == 0:
#                    print('in',k,':',data_dis)
                    new_row_num = data_dis//3
                    for i in range(new_row_num):
                        time_data.append((v+datetime.timedelta(milliseconds = 10)*i).strftime('%d.%m.%Y %H:%M:%S.%f'))   
                    index.extend([m for m in range((time_position_group[k][-1]+1),(time_position_group[k][-1] + 1 + data_dis))])
#                    print('time length:',len(time_data))
#                    print('3data length:',len(index))

                #else:

        if not index:
#            print(len(time_data),len(a01_series),len(a10_series),len(a11_series))
            df = pd.DataFrame({'time':time_data, 'ax': a01_series, 'ay': a10_series, 'az': a11_series})
        else:
            new_a01_series = [self.get_signed_value(i[1]) for i in group_data[1] if i[0] in index]
            new_a10_series = [self.get_signed_value(i[1]) for i in group_data[2] if i[0] in index]
            new_a11_series = [self.get_signed_value(i[1]) for i in group_data[3] if i[0] in index]  
#            print(len(new_a01_series),len(new_a10_series),len(new_a11_series))
            df = pd.DataFrame({'time':time_data, 'ax': new_a01_series, 'ay': new_a10_series, 'az': new_a11_series})
        
#        print('block shape:', df.shape)
        self.start = self.get_next_block_position(self.start)
        return df
    
    def get_ODA_data0(self):
        data_list = self.getdata_u(self.get_para(self.start + 8), self.start + 10)
        group_data = collections.defaultdict(list)
        for v in data_list:
            group_data[v[1]].append([v[0],v[2]]) # group data by code_value 00, 01, 10, 11
            
        time_position = np.array([i[0] for i in group_data[0]])
        time_data_position = np.array([i[1] for i in group_data[0]])
        
        time_position_group = [i for i in np.split(time_position,np.where(np.diff(time_position) != 1)[0]+1)
                                if len(i) == 6]
        time_data_group = [i for i in np.split(time_data_position,np.where(np.diff(time_position) != 1)[0]+1)
                                if len(i) == 6]
        
        time_series = [self.get_time_value(list(i)) for i in time_data_group]
        
        a01_position, a01_series = self.get_adata_position_value(group_data[1])
        a10_position, a10_series = self.get_adata_position_value(group_data[2])
        a11_position, a11_series = self.get_adata_position_value(group_data[3])
        
        data = []
        if time_position_group[0][0] > a01_position[0]:
            data_before_time = time_position_group[0][0] - a01_position[0]
            if data_before_time % 3 == 0:
                row_num = data_before_time//3
                for i in range(row_num):
                    data.append([(time_series[0] - datetime.timedelta(milliseconds = 100)*(row_num - i)).strftime('%d.%m.%Y %H:%M:%S.%f'), 
                                 a01_series[i], a10_series[i], a11_series[i]])

            a01_position, a01_series = self.get_new_adata_position_value(a01_position, a01_series, time_position_group[0][5])
            a10_position, a10_series = self.get_new_adata_position_value(a10_position, a10_series, time_position_group[0][5])
            a11_position, a11_series = self.get_new_adata_position_value(a11_position, a11_series, time_position_group[0][5])
        
        for k, v in enumerate(time_series):

            if v == time_series[-1]:
                try:
                    data_dis = a11_position[-1] - time_position_group[-1][-1]
                except:
                    data_dis = 1
            else: 
                data_dis = time_position_group[k+1][0]-time_position_group[k][0]-6
                
            if data_dis % 3 == 0:
                new_row_num = data_dis//3
                for i in range(new_row_num):
                    data.append([(v+datetime.timedelta(milliseconds = 100)*i).strftime('%d.%m.%Y %H:%M:%S.%f'),
                                 a01_series[i], a10_series[i], a11_series[i]])
            
            a01_position, a01_series = self.get_new_adata_position_value(a01_position, a01_series, time_position_group[k][5]+data_dis)
            a10_position, a10_series = self.get_new_adata_position_value(a10_position, a10_series, time_position_group[k][5]+data_dis)
            a11_position, a11_series = self.get_new_adata_position_value(a11_position, a11_series, time_position_group[k][5]+data_dis)
            
 
        self.start = self.get_next_block_position(self.start)
        return data
    
    def get_code_value(self, a):
        return (a & 0xC000 ) >> 14
    
    def get_acc_value(self, a):
        return a & 0x3FFF
    
    def get_signed_value(self,a):
        if 0x2000 == (a & 0x2000):
            a = a | 0xC000
            a = a - 0x10000 + 1
        b = a/256
        return b
    
    def get_time_value(self, a):
        b = [0x3FFF, 0xFFFC000, 0x3FFF0000000,0xFFFC0000000000,0xFF00000000000000,0xFFFF]
        t = 0
        for k, v in enumerate(a):
            if k <= 3:
                c = v << k*14 & b[k]
                t = t | c
            elif k == 4:
                v0 = v & 0x00FF
                c = int(v0) << k*14 & b[k]
                t = t | c
            elif k == 5:
                mt = v
                
        tt = float(str(t)+'.'+str(mt).zfill(3))
        return datetime.datetime.utcfromtimestamp(tt)        
    
    def get_adata_position_value(self, a):
        position = [i[0] for i in a]
        data = [self.get_signed_value(i[1]) for i in a]
        
        return position, data
    
    def get_new_adata_position_value(self, position, data, start):
        new_position = []
        new_data = []
        for k, v in enumerate(position):
            if v > start:
                new_position.append(v)
                new_data.append(data[k])
        
        return new_position, new_data

#===================================================================================
# get temperature data in a block
    def get_ODT_data(self):
        time_point = self.get_Time(self.start + 10)
        data_T = self.getdata(self.get_para(self.start + 8), self.start + 20)
        data_Tc = [(i/16)-50 for i in data_T]
#        data_Tc.insert(0, time_point.strftime('%d.%m.%Y %H:%M:%S.%f'))
        df = {'time' : time_point.strftime('%d.%m.%Y %H:%M:%S.%f'), 'T1': data_Tc[0], 'T2': data_Tc[1], 'T3': data_Tc[2]}
        self.start = self.get_next_block_position(self.start)
        
        return df
            
    
    
    
    
if __name__ == "__main__":main()
