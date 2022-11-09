
import os
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from readrcfd_t2 import Read_rcfd
from acc_class import ACC
from character_class import EventInfo, Character
from location_class import Location

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
#import matplotlib.pyplot as plt

import pandas as pd
import numpy as np
import datetime

def main():
    root = tk.Tk()
    RcfdViewer(root)
    root.mainloop()
    
    
class RcfdViewer:
    def __init__(self, root):

#==============================================================================        

    def create_top_menu_bar(self):
        self.topbar_frame = tk.Frame(self.root, height = 60 , width  = 1630, relief = 'ridge', borderwidth = 1)
        self.topbar_frame.place(x = 5, y = 5, width = 1630, height = 60)
        
        ttk.Button(self.topbar_frame, text = "FFT", command = self.event_fft).place(x = 5, y = 10, width = 90, height = 30)	

        ttk.Button(self.topbar_frame, text = "Acc Info", command = self.event_acc_info).place(x = 105, y = 10, width = 90, height = 30)	

        ttk.Button(self.topbar_frame, text = "Loc Info", command = self.event_loc_info).place(x = 205, y = 10, width = 90, height = 30)	
        
        ttk.Button(self.topbar_frame, text = "Character", command = self.event_character).place(x = 305, y = 10, width = 90, height = 30)	

        ttk.Button(self.topbar_frame, text = "Convert AES data", command = self.convert_AES_data).place(x = 405, y = 10, width = 120, height = 30)	
        
        ttk.Button(self.topbar_frame, text = "Convert ACC data", command = self.convert_ACC_data).place(x = 535, y = 10, width = 120, height = 30)	
        
#        self.prog = ttk.Progressbar(self.topbar_frame, orient = 'horizontal', mode='determinate', length = 200, maximum = 100)
#        self.prog.place(x = 665, y = 10, width = 200, height = 30)
        
    def create_sourcefile_display(self):
        self.source_display_frame = tk.Frame(self.root, height = 820 , width  = 430, relief = 'ridge', borderwidth = 1)
        self.source_display_frame.place(x = 5, y = 70, width = 430, height = 820)
        
        bsource = ttk.Button(self.source_display_frame, text = "Source folder", command = self.rcdf_input)
        bsource.place(x = 5, y = 5, width = 90, height = 25)		

        self.lsource = ttk.Label(self.source_display_frame, text = self.default_source_folder, background = "white")
        self.lsource.place(x = 100, y = 5, width = 325, height = 25)
        
        ttk.Label(self.source_display_frame, text = "Rcdf files:").place(x = 5, y = 40,  width = 420, height = 25)		
        self.sdisplay = tk.scrolledtext.ScrolledText(master = self.source_display_frame, 
                                                     wrap =tk.WORD, font=("Helvetica", 10),
                                                     state = 'disabled')
        self.sdisplay.place(x = 5, y = 70,  width = 420, height = 750)
        
        self.sdisplay.bind('<Double-Button-1>', self.rcdf_event_input)
        
    def create_eventfile_display(self):
        event_display_frame = tk.Frame(self.root, height = 820 , width  = 270, relief = 'ridge', borderwidth = 1)
        event_display_frame.place(x = 445, y = 70, width = 270, height = 820)
        
        ttk.Label(event_display_frame, text = "Event files:").place(x = 5, y = 5,  width = 260, height = 25)		
        self.edisplay = tk.scrolledtext.ScrolledText(master = event_display_frame, 
                                                     wrap =tk.WORD, font=("Helvetica", 10),
                                                     state = 'disabled')
        self.edisplay.place(x = 5, y = 35,  width = 260, height = 785)
        
        self.edisplay.bind('<Double-Button-1>', self.show_event_plot)

    def create_event_figure_display(self):
        self.event_figure_display_frame = tk.Frame(self.root, height = 400 , width  = 910, relief = 'ridge', borderwidth = 1)
        self.event_figure_display_frame.place(x = 725, y = 70, width = 910, height = 400)


    def create_acc_figure_display(self):
        self.acc_figure_display_frame = tk.Frame(self.root, height = 400 , width  = 910, relief = 'ridge', borderwidth = 1)
        self.acc_figure_display_frame.place(x = 725, y = 490, width = 910, height = 400)

#==============================================================================
#===================================================================================
#       topmenu_bar functions
#================================================================================
    def event_fft(self):
        self.t = tk.Toplevel(self.topbar_frame, height = 800, width = 1300)
        self.t.title('FFT Plot Window for Event {}'.format(self.current_efile))
        self.show_event_fft()
    def show_event_fft(self):
        self.create_event_fft()
        self.embed_event_fft()
    def create_event_fft(self):
        ef = self.get_event_data(self.file_path, self.current_efile) # data form dict
        efd = Character(ef,0.004)
        self.af2 = Figure(figsize=(16, 8), dpi=100)
        self.af2.suptitle('FFT of event: {}'.format(self.current_efile), fontsize = 12)

        for i, k in enumerate(sorted(efd._data.keys())):
            f = efd.AmpFre_FFT(efd._data[k])
            aa = self.af2.add_subplot(2,3,i+1)
            aa.plot(np.array(f['freq'])/1000,f['Amp'], color = 'b', linewidth=1, label = k)

            aa.set_xlabel('Frequency (kHz)',fontsize = 10)
            aa.set_ylabel('Amplitude (a.u.)', fontsize = 10)
#            aa.set_xlim([0, 125000])
            aa.legend(loc = 'upper right')
            aa.grid(True)
        
    def embed_event_fft(self):
        self.event_fft_canvas_frame = tk.Frame(self.t )
        self.event_fft_canvas_frame.pack(side=tk.TOP,fill=tk.BOTH, expand=1)
        canvas = FigureCanvasTkAgg(self.af2, master=self.event_fft_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.event_fft_toolbar_frame = tk.Frame(self.t)
        self.event_fft_toolbar_frame.pack(fill=tk.BOTH, expand=1)
        toolbar = NavigationToolbar2Tk(canvas, self.event_fft_toolbar_frame)
        toolbar.update()
        
#========================================================================================
    def event_acc_info(self):
        acc = tk.Toplevel(self.topbar_frame, height = 300, width = 380)
        acc.title('Acceleration info Window for Event {}'.format(self.current_efile))
        #acc_data = self.get_acc_data()
        event_time = datetime.datetime.strptime(self.current_efile[-26:], '%d_%m_%Y_%H_%M_%S_%f')
        ad = ACC(self.df_acc, event_time)
        acc_info = ad.get_sub_acc_value()
        
        ttk.Label(acc, text = 'Event: {}'.format(self.current_efile), font = ('Helvetica', 13)).place(x = 10, y = 10, width = 370, height = 40)
        ttk.Label(acc, text = 'Time = {}'.format(acc_info[2]), font = ('Helvetica', 12)).place(x = 8, y = 55, width = 370, height = 30)
        
        ttk.Label(acc, text = 'Angle = {:3.0f}'.format(acc_info[0]), font = ('Helvetica', 12)).place(x = 8, y = 90, width = 370, height = 30)
        ttk.Label(acc, text = 'Rotate = {}'.format(acc_info[1]), font = ('Helvetica', 12)).place(x = 8, y = 125, width = 370, height = 30)
        ttk.Label(acc, text = 'a_r = {}'.format(acc_info[3]), font = ('Helvetica', 12)).place(x = 8, y = 160, width = 370, height = 30)

        ttk.Label(acc, text = 'a_x = {}'.format(acc_info[4]), font = ('Helvetica', 12)).place(x = 8, y = 195, width = 370, height = 30)
        ttk.Label(acc, text = 'a_y = {}'.format(acc_info[5]), font = ('Helvetica', 12)).place(x = 8, y = 230, width = 370, height = 30)
        ttk.Label(acc, text = 'a_z = {}'.format(acc_info[6]), font = ('Helvetica', 12)).place(x = 8, y = 265, width = 370, height = 30)

#===========================================================================================
    def event_loc_info(self):
        locw = tk.Toplevel(self.topbar_frame, height = 280, width = 500)
        locw.title('Location info Window for Event {}'.format(self.current_efile))

        df = Location(pd.DataFrame(self.ef))
        seq6s = df.Sequential6s()
        seq4s = df.Sequential4s()
        geiger6s = df.Geiger6s()
        geiger4s = df.Geiger4s()
        
        ttk.Label(locw, text = 'Event: {}'.format(self.current_efile), font = ('Helvetica', 13)).place(x = 10, y = 10, width = 490, height = 40)
        if seq6s['x'] == None:
            ttk.Label(locw, text = 'Sequential6s: None Results', font = ('Helvetica', 12)).place(x = 8, y = 55, width = 490, height = 30)
        else:    
            ttk.Label(locw, text = 'Sequential6s: x = {0:5.0f}, y = {1:5.0f}, res = {2:5.3f}'.format(seq6s['x'],seq6s['y'],seq6s['res']), font = ('Helvetica', 12)).place(x = 8, y = 55, width = 490, height = 30)
        
        if seq4s['x'] == None:
            ttk.Label(locw, text = 'Sequential4s: None Results', font = ('Helvetica', 12)).place(x = 8, y = 90, width = 490, height = 30)
        else:
            ttk.Label(locw, text = 'Sequential4s: x = {0:5.0f}, y = {1:5.0f}, res = {2:5.3f}'.format(seq4s['x'],seq4s['y'],seq4s['res']), font = ('Helvetica', 12)).place(x = 8, y = 90, width = 490, height = 30)

        if geiger6s['x'] == None:
            ttk.Label(locw, text = 'Geiger6s: None Results', font = ('Helvetica', 12)).place(x = 8, y = 130, width = 490, height = 30)
        else:    
            ttk.Label(locw, text = 'Geiger6s: x = {0:5.0f}, y = {1:5.0f}, res = {2:5.3f}'.format(geiger6s['x'],geiger6s['y'],geiger6s['res']), font = ('Helvetica', 12)).place(x = 8, y = 130, width = 490, height = 30)

        if geiger4s['x'] == None:
            ttk.Label(locw, text = 'Geiger4s: None Results', font = ('Helvetica', 12)).place(x = 8, y = 165, width = 490, height = 30)
        else:
            ttk.Label(locw, text = 'Geiger4s: x = {0:5.0f}, y = {1:5.0f}, res = {2:5.3f}'.format(geiger4s['x'],geiger4s['y'],geiger4s['res']), font = ('Helvetica', 12)).place(x = 8, y = 165, width = 490, height = 30)
    
    
    
    
    
#========================================================================================
        
    def event_character(self):
        chw = tk.Toplevel(self.topbar_frame, height = 600, width = 1200)
        chw.title('Character Info Window for Event {}'.format(self.current_efile))
        
        df = Character(pd.DataFrame(self.ef))
        onset = df.Onset_time()
        ttk.Label(chw, text = 'Event: {}'.format(self.current_efile), font = ('Helvetica', 15)).place(x = 80, y = 10, width = 1200, height = 40)
        ttk.Label(chw, text = 'Onset time: {}'.format(onset), font = ('Helvetica', 12)).place(x = 8, y = 55, width = 1200, height = 30)
        ttk.Label(chw, text = 'Time domain:', font = ('Helvetica', 12)).place(x = 8, y = 95, width = 1200, height = 30)

        for k, v in enumerate(list(df._data)): 
            d = df.Amp_Time_Character(df._data[v])
            ttk.Label(chw, text = '{0}:  Max_Amp(t) = {1:5.0f}, time(max) = {2:5.3f}, Energy = {3:.2e}, Energy(2.5ms) = {4:.2e}, ZeroCrossf(2.5ms) = {5:5.1f}, rise_time = {6:5.0f}, RA = {7:5.0f}'.format(v, d['maxAmp_t'], d['time_peak'], d['Energy'], d['Energy25'], d['ZeroCrossf'], d['rise_time'], d['RA']), font = ('Helvetica', 11)).place(x = 8, y = 135+35*k, width = 1200, height = 30)

        ttk.Label(chw, text = 'Frequency domain:', font = ('Helvetica', 12)).place(x = 8, y = 350, width = 1200, height = 30)
        for key, val in enumerate(list(df._data)): 
            dd = df.AmpFre_FFT(df._data[val])
            e = df.Amp_Fre_Character(dd['Amp'], dd['freq'])
            ttk.Label(chw, text = '{0}:  Max_Amp(f) = {1:5.0f}, fre_peak = {2:5.3f}, fre_centroid = {3:5.1f}, fre_wpeak = {4:5.1f}, Power = {5:.2e}, PartialPower(%) = [{6:.1f}, {7:.1f}, {8:.1f}, {9:.1f}, {10:.1f}]'.format(val, e['maxAmp_f'], e['fre_peak'], e['fre_centroid'], e['fre_wpeak'], e['Power'], *e['PartialPower']), font = ('Helvetica', 11)).place(x = 8, y = 385+35*key, width = 1200, height = 30)
            
#=====================================================================================================
    def convert_AES_data(self):
#        self.prog['value'] = 0
        save_folder_path = filedialog.askdirectory(parent = self.topbar_frame, 
                                                     initialdir = 'D:',
                                                     title = 'Select SAVE AES File Folder')
        f = Read_rcfd(self.file_path)
        f.write_to_csvs(save_folder_path)
        
        messagebox.showinfo('AES Data Converted','AES Data Converted')
#        path1 = os.path.join(save_folder_path, self.current_sfile)
#        if not os.path.exists(path1): 
#            os.makedirs(path1)
#            
#        event_list = self.get_listOfEvent(self.file_path)
#        value = len(event_list)
#        for k, v in enumerate(event_list):
#            csvfile = self.get_event_data(self.current_sfile, v)
#            df = pd.DataFrame(csvfile, columns = csvfile.keys())
#            df.to_csv(os.path.join(save_folder_path, self.current_sfile, v + '.csv'), decimal = ',', sep = ';', index = False)	
#
#            self.prog['value'] = int((k+1)*100/value)

    
#=================================================================================================    
    def convert_ACC_data(self):
        save_folder_path = filedialog.askdirectory(parent = self.topbar_frame, 
                                                     initialdir = 'D:',
                                                     title = 'Select SAVE ACC File Folder')
        f = Read_rcfd(self.file_path)
        f.ODA_write_to_csv(save_folder_path)
        messagebox.showinfo('ACC Data Converted','ACC Data Converted')

#        self.df_acc.to_csv(os.path.join(save_folder_path, 'Acc_'+self.current_sfile + '.csv'), decimal = ',', sep = ';', index = False)
    
#==============================================================================
#        create_sourcefile_display   && create_eventfile_display   
#==============================================================================        
    def rcdf_input(self):
        self.source_folder_path = filedialog.askdirectory(parent = self.source_display_frame, 
                                                     initialdir = self.default_source_folder,
                                                     title = 'Select Rcdf Source Folder')
        source_file_list = self.get_listOfFiles(self.source_folder_path)
        self.sdisplay.config(state = 'normal')
        self.sdisplay.delete(1.0, 'end')
        for k, i in enumerate(source_file_list):
            self.sdisplay.insert('{}.0'.format(k+1), i+'\n')
        self.sdisplay.config(state = 'disabled')
        
        self.lsource.config(text = self.source_folder_path)
        
    def rcdf_event_input(self, event):
        self.current_sfile = self.sdisplay.get("insert linestart", "insert lineend")
        self.file_path = os.path.join(self.source_folder_path, self.current_sfile)
        event_list = self.get_listOfEvent(self.file_path)
        self.edisplay.config(state = 'normal')
        self.edisplay.delete(1.0, 'end')
        for k, i in enumerate(event_list):
            self.edisplay.insert('{}.0'.format(k+1), i+'\n')
        self.edisplay.config(state = 'disabled')
        
        self.show_acc_plot()
        
    def get_listOfFiles(self, path):
        listOfFiles_0 = os.listdir(path)
        listOfFiles = [f for f in listOfFiles_0 if f.endswith('.rcfd')]
        return listOfFiles
    
    def get_listOfEvent(self, file):
        f = Read_rcfd(file)
        AES_data = f.get_all_data()
#        print(AES_data.keys())
        return AES_data.keys()
    
    def get_event_time(self, file):
        key = self.get_listOfEvent(file)
        time = [i[-26:] for i in key]
        df = pd.DataFrame(time, columns = ['time0'])
        df['event'] = [0]*len(time)
        df['time'] = pd.to_datetime(df['time0'], format = '%d_%m_%Y_%H_%M_%S_%f')
        return df
    def get_acc_data(self, file):
        f = Read_rcfd(file)
        df = f.get_all_data_ODA()
        #df = pd.DataFrame(Acc_data, columns = ['time0', 'ax', 'ay', 'az'])
        df['time'] = pd.to_datetime(df['time'], format = '%d.%m.%Y %H:%M:%S.%f')
        #df.to_csv('Acc_{}.csv'.format(self.current_sfile ), decimal = ',', sep = ';', index = False)
        return df
#===================================================================================
#        create_acc_figure_display
# ======================================================================================   
  
    def show_acc_plot(self):
        try:
#            self.acc_canvas_frame.winfo_exists():
            self.acc_canvas_frame.destroy()
            self.acc_toolbar_frame.destroy()
            
            self.create_acc_plot()
            self.embed_acc_plot()

        except:
            self.create_acc_plot()
            self.embed_acc_plot()
        
    def create_acc_plot(self):
#        df_acc = self.get_acc_data(self.file_path).iloc[::10] # pd.DataFrame
        self.df_acc = self.get_acc_data(self.file_path) # pd.DataFrame 
        df_AES = self.get_event_time(self.file_path) # pd.DataFrame
        
        self.af1 = Figure(figsize=(7.4, 3.6), dpi=100)
        a = self.af1.add_subplot(111)
        a.plot(self.df_acc['time'], self.df_acc['ax'], 'b-', label = 'ax') 
        a.plot(self.df_acc['time'], self.df_acc['ay'], 'g-', label = 'ay')
        a.plot(self.df_acc['time'], self.df_acc['az'], 'r-', label = 'az')
        a.plot(df_AES['time'], df_AES['event'], 'ko', linewidth = 1, markersize = 3, label = 'event')
        a.set_title('3 axis Acceleration of file: {}'.format(self.current_sfile), fontsize = 12)
        a.set_xlabel('Time',fontsize = 10)
        a.set_ylabel('Acceleration (/g(m*s-2))', fontsize = 10)
        a.set_ylim([-1.5, 1.5])
        a.legend(loc = 'upper right')
        a.grid(True)
        
    def embed_acc_plot(self):
        self.acc_canvas_frame = tk.Frame(self.acc_figure_display_frame )
        self.acc_canvas_frame.pack(side=tk.TOP,fill=tk.BOTH, expand=1)
        canvas = FigureCanvasTkAgg(self.af1, master=self.acc_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.acc_toolbar_frame = tk.Frame(self.acc_figure_display_frame)
        self.acc_toolbar_frame.pack(fill=tk.BOTH, expand=1)
        toolbar = NavigationToolbar2Tk(canvas, self.acc_toolbar_frame)
        toolbar.update()
#===============================================================================  
#      create_event_figure_display
#====================================================================================
    def show_event_plot(self, event):
        try:
#            self.event_canvas_frame.winfo_exists():
            self.event_canvas_frame.destroy()
            self.event_toolbar_frame.destroy()
            
            self.create_event_plot()
            self.embed_event_plot()

        except:
            self.create_event_plot()
            self.embed_event_plot()
        
    def create_event_plot(self):
        self.current_efile = self.edisplay.get("insert linestart", "insert lineend")
        self.ef = self.get_event_data(self.file_path, self.current_efile) # data form dict
        
        self.af = Figure(figsize=(7.4, 3.6), dpi=100)
        aa = self.af.add_subplot(111)
        time = [i*0.004 for i in range(8192)]
        color = ['b', 'g', 'r', 'c', 'm', 'y']
        offset = 2000
        for i, k in enumerate(sorted(self.ef.keys())):
            aa.plot(time, np.array(self.ef[k])+i*offset, color = color[i], linewidth=1, label = k)

        aa.set_title('event file: {}'.format(self.current_efile), fontsize = 12)
        aa.set_xlabel('Time (ms)',fontsize = 10)
        aa.set_ylabel('Amplitude (a.u.)', fontsize = 10)
        aa.set_xlim([0, 33])
        aa.legend(loc = 'center left', bbox_to_anchor=(1,0.5))
        aa.grid(True)
        
    def embed_event_plot(self):
        self.event_canvas_frame = tk.Frame(self.event_figure_display_frame )
        self.event_canvas_frame.pack(side=tk.TOP,fill=tk.BOTH, expand=1)
        canvas = FigureCanvasTkAgg(self.af, master=self.event_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.event_toolbar_frame = tk.Frame(self.event_figure_display_frame)
        self.event_toolbar_frame.pack(fill=tk.BOTH, expand=1)
        toolbar = NavigationToolbar2Tk(canvas, self.event_toolbar_frame)
        toolbar.update()
        
    def get_event_data(self, file, key):
        f = Read_rcfd(file)
        AES_data = f.get_all_data()
        return AES_data[key]

if __name__ == '__main__': main()