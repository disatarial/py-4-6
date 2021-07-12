from tkinter import *
from tkinter import ttk, Toplevel
from tkinter import filedialog as fd

import tkinter.messagebox as mb

import os.path
from threading import Thread
import socket
import configparser  # импортируем библиотеку работы с INI-шками
from time import sleep
import lib_kalibrovka
import generator
import fieldmeter


wdBeginFreq=0
wdEndFreq=1
wdStepFreq=2
wdStepType=3
wdMaxGendelta=4
wddeltaLevel=5
wdMaxNumSter=6
wdid_gen=7         #настройки генератора [0-ident, 1-typeinterface, 2-adr, 3-data(port,speed),4-name_pribora]
wdid_powmet=8
wdid_kalmet=9
wdfile_name_amplifier=10
wdfile_name_otvetvitel=11
wdfile_koef_kallibrovochnogo_us=12
wdkal_otvetvitel=13
wdkal_kalprobe=14
wdkal_usilitel=15
wderror=16
wdfreq=17
wdfasttimepause=18
wdlevel=19

workdata=[ # ] # все характеристики, которые требуются для запуска цикла испытаний/калибровки
 0.0, #BeginFreq 
 1.0, #EndFreq  
 2.0, #StepFreq
 3.0, #StepType=0  # тип  0 - линейный шаг, 1 - процентный,  2 - по таблице
 4.0, #MaxGendelta =10  #ограничение на  прибавление в можности
 5.0, #deltaLevel=1    # точность установки
 6.0, #MaxNumSter=30  # макс кол-во шагов при настройка ( в случае внезапной нелинейности схемы)
 7, #id_gen=1  настройки оборудования [0-ident, 1-typeinterface, 2-adr, 3-data(port,speed),4-name_pribora]
 8, #id_powmet=1
 9, #id_curmet=0 
 "10",   # file_name_amplifier
 "11",   # file_name_otvetvitel
 "12",   #  file_koef_kallibrovochnogo_us-va
 13, #
 14, #
 15, #
 16, #
 17, #
 18, # 
 19, # 
 20, #
 21, # 
 22  #  
 ]
Kal_Table=[] #  [freqbegin, freqend, freqstep, levelbegin,levelend, minGenlevel ]
Work_Table=[] # табличка для настройки оборудованияя [freq,level, minGenlevel, powerlevel,currentlevel,genlevel,mingenlevel]

def FastPause( time): # пауза которая может быстро закончиться
   for i in range (int(time/50)):
      sleep(0.05)
      if workdata[wdfasttimepause]:
         break
      
def LoadTable():
   global workdata
   file_name_amplifier=workdata[wdfile_name_amplifier]
   file_name_otvetvitel=workdata[wdfile_name_otvetvitel]
   file_name_kalprobe=workdata[wdfile_koef_kallibrovochnogo_us]
   #print("LoadTable\r\n")
   # усилитель   загружаем  калибровочную таблицу
   #print(file_name_amplifier)
   FilePribor = open("./pribor/"+file_name_amplifier)
   kal_amplifier = FilePribor.read()
   FilePribor.close()
   data=[]
   kal_amplifier=(kal_amplifier.split())
   for i in range(len(kal_amplifier)):
      data.append(float(kal_amplifier[i]))
   data.insert(0,2)  
   kal_amplifier=data;
   #print("kal_amplifier\r\n",kal_amplifier)
   # ответвитель   загружаем  калибровочную таблицу
   #print(file_name_otvetvitel)
   FilePribor = open("./pribor/"+file_name_otvetvitel)
   kal_otvetvitel = FilePribor.read()
   FilePribor.close()
   data=[]
   kal_otvetvitel=(kal_otvetvitel.split())
   for i in range(len(kal_otvetvitel)):
      data.append(float(kal_otvetvitel[i]))
   data.insert(0,2)  
   kal_otvetvitel=data
   #print("kal_otvetvitel\r\n",kal_otvetvitel)
   #  коэф калибровочоного уст-ва
   #print(file_name_kalprobe)
   FilePribor = open("./pribor/"+file_name_kalprobe)#   kal_kalprobe = FilePribor.read()
   kal_kalprobe = FilePribor.read()
   FilePribor.close()
   data=[]
   kal_kalprobe=(kal_kalprobe.split())
   for i in range(len(kal_kalprobe)):
      data.append(float(kal_kalprobe[i]))
   data.insert(0,2)  
   kal_kalprobe=data
   #print("kal_kalprobe\r\n",kal_kalprobe)
   #Work_Table =lib_kalibrovka.CreateFreqTable (Kal_Table)   
   workdata[wdkal_usilitel]=kal_amplifier
   workdata[wdkal_otvetvitel]=kal_otvetvitel
   workdata[wdkal_kalprobe]=kal_kalprobe
   
   
threadcommand=0

def workcicle(s):
  global threadcommand
  while (1):
    print (s)
    sleep(1)
    if (threadcommand!=0):
      break
      
def OpenPribors():
   inst=workdata[wdid_gen]  # скопировали настройки
   #print(inst)
   workdata[wdid_gen][0]=generator.Open(inst[1],inst[2],inst[3])
#   inst=workdata[19]  # скопировали настройки
   #8, #id_powmet=1
#   workdata[wdid_powmet]=generator.Open(inst[0],inst[1],inst[2])
   inst=workdata[wdid_kalmet]  # скопировали настройки
   workdata[wdid_kalmet][0]=fieldmeter.Open(inst[1],inst[2],inst[3])

def ClosePribor():
   generator.Close( workdata[wdid_gen][0]   ,workdata[wdid_gen][1])
   fieldmeter.Close(workdata[wdid_kalmet][0],workdata[wdid_kalmet][1])


def kallcicle():
  global workdata
  global threadcommand
  global Work_Table
  #LoadTable()
  print("start kallcicle \r\n",workdata)
  cicle=1 # переменная окончания цикла передора по частоте
  try:
    OpenPribors()
  except:
     msg = "Порты приборов установленф не  правильно!"
     mb.showerror("Ошибка", msg)
     ClosePribor()
     return
  Freq=workdata[wdBeginFreq]
  number=lib_kalibrovka.FindFreqNum(Work_Table,Freq,1)
  print("lib_kalibrovka.FindFreqNum=",number,Freq)
  while (cicle ): 
     # подаем частоту с генератора
     try:
        generator.WriteFreq(workdata[wdid_gen][0],workdata[wdid_gen][4],Freq)    #handle_gen,id_gen,Freq
     except:
       msg = "нет связи с генератором!"
       mb.showerror("Ошибка", msg)
       ClosePribor()
       return

     # =========================================================================================================================
     # подаем мощность с генератора
     genlevel=lib_kalibrovka.datakaltabl(Work_Table,2,number)
     generator.WriteLevel(workdata[wdid_gen][0],workdata[wdid_gen][4],genlevel)    #handle_gen,id_gen,Freq
     FastPause(300)
     try:
        Ures=fieldmeter.ReadLevel(workdata[wdid_kalmet][0],workdata[wdid_kalmet][4]) # ...read....
     except:
       msg = "нет связи с измерителем!"
       mb.showerror("Ошибка", msg)
       ClosePribor()
       return
     flag=(abs(lib_kalibrovka.datakaltabl(Work_Table,3,number)+workdata[wddeltaLevel]-Ures)> workdata[wddeltaLevel])
     NumSter=0
     while flag: 
         try:
            generator.WriteFreq(workdata[wdid_gen][0],workdata[wdid_gen][4],Freq)    #handle_gen,id_gen,Freq
         except:
            msg = "нет связи с генератором!"
            mb.showerror("Ошибка", msg)
            ClosePribor()
            return
         workdata[wdlevel]=Ures
#         print("while:")
         NumSter=NumSter+1
#	 # подаем мощность с генератора
         generator.WriteLevel(workdata[wdid_gen][0],workdata[wdid_gen][4],genlevel)    #handle_gen,id_gen,Freq
#         # измеряем сигнал на измерителе, добавляем его коэффициент из таблички
         try:
            Ures=fieldmeter.ReadLevel(workdata[wdid_kalmet][0],workdata[wdid_kalmet][4]) # ...read....
         except:
            ClosePribor()
            return
 
         delta=lib_kalibrovka.NewAmplituda(lib_kalibrovka.datakaltabl(Work_Table,3,number)+workdata[wddeltaLevel],genlevel,Ures)
         print(number,Freq,delta,Ures,genlevel,lib_kalibrovka.datakaltabl(Work_Table,3,number))
	 # требуется прибачить очень много? тогда ограничиваем прибавление значением MaxGendelta
         if (delta > workdata[wdMaxGendelta]):
            genlevel=genlevel+workdata[wdMaxGendelta]
         else:
            genlevel=genlevel+delta

#         # ограничиваем максимальный сигнал.(данные должны братся из таблице усилителя
#         numfrequs=lib_kalibrovka.FindFreqNum(Freq, workdata[wdkal_usilitel])
#	 #maxgen=lib_kalibrovka.datakaltabl(workdata[wdkal_usilitel],1,numfrequs)
#	# print(genlevel,numfrequs,maxgen)
#	 #if (genlevel>maxgen): 
#           # genlevel=maxgen
         workdata[wdfreq]=Freq
         FastPause(1000)
   
         if (threadcommand!=0): 
           cicle=0
           flag=0   
           print("cicle==0",threadcommand)
         else:   # break
           flag=(abs(lib_kalibrovka.datakaltabl(Work_Table,3,number)+workdata[wddeltaLevel]-Ures)> workdata[wddeltaLevel])

     Work_Table[lib_kalibrovka.adrkaltabl(Work_Table,5,number)]=genlevel
     Work_Table[lib_kalibrovka.adrkaltabl(Work_Table,6,number)]=Ures
     number=number+1
     if (number>=(lib_kalibrovka.lenkaltabl(Work_Table))): 
        cicle =0	 
     else:
        Freq=lib_kalibrovka.datakaltabl(Work_Table,1,number)

     # условие окончания цикла по частотам
     if ((workdata[wdStepFreq] > 0)and (Freq > workdata[wdEndFreq])):  # цикл вверх по частоте
        cicle =0
     if ((workdata[wdStepFreq] < 0)and (Freq <workdata[wdBeginFreq])):  # цикл вниз по частоте
        cicle =0	      
     
     #измеряем сигнал на ответвителе, добавляем его коэффициент из таблички
     Uotv=0 # ...read....
  lib_kalibrovka.printkaltabl(Work_Table)
  ClosePribor()
  


config_file ="setting.ini"
def NastrPribor():
   Nastrwindow = Toplevel( )
   labelKotv   = Label(Nastrwindow,text=config.get('workdata','fileotvet'), font="Arial 12")
   labelCurrent= Label(Nastrwindow,text=config.get('workdata','filecurrent'), font="Arial 12")
   labelkkal=Label(Nastrwindow,text=config.get('workdata','filekkal'), font="Arial 12")
   labelAmplifier=Label(Nastrwindow,text=config.get('workdata','amplifier'), font="Arial 12")

   def btnKotv_clik():
       file_name = fd.askopenfilename(initialdir='./pribor',filetypes=[('kal_types','*.kal')])
       fileotvet = open(file_name)
       otvetvitel = fileotvet.read()
       fileotvet.close()
       f=os.path.relpath(file_name , start='./pribor')
       config.set('workdata','fileotvet',f)
       labelKotv.config(text = f)

       print('otvetvitel = \r\n',otvetvitel,f)

   def btnCurrent_clik():
       file_name = fd.askopenfilename(initialdir='./pribor',filetypes=[('kal_types','*.kal')])
       FileCurrent = open(file_name)
       currentprobe = FileCurrent.read()
       FileCurrent.close()
       f=os.path.relpath(file_name , start='./pribor')
       config.set('workdata','filecurrent',f)
       labelCurrent.config(text = f)
       print(' Current = \r\n',currentprobe)

   def btnkkal_clik():
       file_name = fd.askopenfilename(initialdir='./pribor',filetypes=[('kal_types','*.kal')])
       Filekkal = open(file_name)
       probe = Filekkal.read()
       Filekkal.close()
       f=os.path.relpath(file_name , start='./pribor')
       config.set('workdata','filekkal',f)
       labelkkal.config(text = f)
       print(' k Kall = \r\n',probe)

   def btnamplifier_clik():
       file_name = fd.askopenfilename(initialdir='./pribor',filetypes=[('kal_types','*.kal')])
       FileAmp = open(file_name)
       probe = FileAmp.read()
       FileAmp.close()
       f=os.path.relpath(file_name , start='./pribor')
       config.set('workdata','fileamplifier',f)
       labeAmplifier.config(text = f)
       print(' amplifier = \r\n',probe)

   def btnotmena_clik():
       Nastrwindow.destroy()
       Nastrwindow.update()
       print(' btnotmena_clik = \r\n')

   def btnnorma_clik():
       print(' btnnorma_clik = \r\n',)
       #config.write(config_file)
       config.set('workdata','typegenport',str(combogenerator.current()))
       config.set('workdata','genport',label_generator.get())
       config.set('workdata','genportdata',label_generatordata.get())
       config.set('workdata','gentype',str(namegenerator.current()))
       
       config.set('workdata','typepowermeterport',str(combopowermeter.current()))
       config.set('workdata','powermeterport',label_powermeter.get())
       config.set('workdata','typekalmeterport',label_powermeterdata.get())
       config.set('workdata','powermetertype',str(namepowermeter.current()))

       config.set('workdata','typekalmeterport',str(combokalmeter.current()))
       config.set('workdata','kalmeterport',label_kalmeter.get())
       config.set('workdata','kalmeterdata',label_kalmeterdata.get())
       config.set('workdata','kalmetertype',str(namekalmeter.current()))

       config.set('workdata','maxgendelta',label_MaxGendelta.get())
       config.set('workdata','deltalevel',label_deltaLevel.get())
       config.set('workdata','maxnumster',label_MaxNumSter.get())
       
       Nastrwindow.destroy()
       Nastrwindow.update()
       f = open(config_file, 'w')
       config.write(f)
       f.close()

   print("NastrPribor")
     
   Nastrwindow_label_0_0="Настройка оборудования"
   Nastrwindow_l0 = Label(Nastrwindow,text=Nastrwindow_label_0_0, font="Arial 20")
   Nastrwindow_l0.grid(row=0, column=0,columnspan =4)



   namelabel5="Генератор:"
   l5 = Label(Nastrwindow,text=namelabel5, font="Arial 12")
   l5.grid(row=9, column=0)
   namegenerator = ttk.Combobox(Nastrwindow, 
                            values=["Нет",
                                    "JDS6600", 
                                    "SMB100"])
   namegenerator .grid(row=9, column=1,sticky=N+S+W+E)
   namegenerator .current(config.get('workdata','gentype'))

   combogenerator = ttk.Combobox(Nastrwindow, 
                            values=[
                                    "Нет", 
                                    "COM PORT",
                                    "TCP/IP"])
   combogenerator.grid(row=9, column=2,sticky=N+S+W+E)
   combogenerator.current(config.get('workdata','typegenport'))
   
   label_generator=Entry(Nastrwindow, width=10)
   label_generator.grid(row=9, column=3,sticky=N+S+W+E)
   label_generator.insert(0, config.get('workdata','genport'))

   label_generatordata=Entry(Nastrwindow, width=10)
   label_generatordata.grid(row=9, column=4,sticky=N+S+W+E)
   label_generatordata.insert(0, config.get('workdata','genportdata'))

   namelabel6="Измеритель мощности:"
   l6 = Label(Nastrwindow,text=namelabel6, font="Arial 12")
   l6.grid(row=10, column=0,)
   #label_generator.insert(0, config.get('workdata','powermeterport'))
   namepowermeter = ttk.Combobox(Nastrwindow, 
                            values=["Нет",])
   namepowermeter.grid(row=10, column=1,sticky=N+S+W+E)
   namepowermeter.current(config.get('workdata','powermetertype'))


   combopowermeter = ttk.Combobox(Nastrwindow, 
                            values=[
                                    "Нет", 
                                    "COM PORT",
                                    "TCP/IP"])
   combopowermeter.grid(row=10, column=2,sticky=N+S+W+E)
   combopowermeter.current(config.get('workdata','typepowermeterport'))

   label_powermeter=Entry(Nastrwindow, width=10)
   label_powermeter.grid(row=10, column=3,sticky=N+S+W+E)
   label_powermeter.insert(0, config.get('workdata','powermeterport'))

   label_powermeterdata=Entry(Nastrwindow, width=10)
   label_powermeterdata.grid(row=10, column=4,sticky=N+S+W+E)
   label_powermeterdata.insert(0, config.get('workdata','powermeterdata'))

   namelabel7="Измеритель :"
   l7 = Label(Nastrwindow,text=namelabel7, font="Arial 12")
   l7.grid(row=11, column=0)
   namekalmeter = ttk.Combobox(Nastrwindow, 
                            values=["Нет",
			            "narda ep60x" ])
   namekalmeter.grid(row=11, column=1,sticky=N+S+W+E)
   namekalmeter.current(config.get('workdata','kalmetertype'))



   combokalmeter = ttk.Combobox(Nastrwindow, 
                            values=[
                                    "Нет", 
                                    "COM PORT",
                                    "TCP/IP"])
   combokalmeter.grid(row=11, column=2,sticky=N+S+W+E)
   combokalmeter.current(config.get('workdata','typekalmeterport'))

   label_kalmeter=Entry(Nastrwindow, width=10)
   label_kalmeter.grid(row=11, column=3,sticky=N+S+W+E)
   label_kalmeter.insert(0, config.get('workdata','kalmeterport'))

   label_kalmeterdata=Entry(Nastrwindow, width=10)
   label_kalmeterdata.grid(row=11, column=4,sticky=N+S+W+E)
   label_kalmeterdata.insert(0, config.get('workdata','kalmeterdata'))


   namelabel8="Коэф. ответвителя:"
   l8 = Label(Nastrwindow,text=namelabel8, font="Arial 12")
   l8.grid(row=12, column=0,columnspan =2)

   #labelKotv= Label(Nastrwindow,text=config.get('workdata','fileotvet'), font="Arial 12")
   labelKotv.grid(row=12, column=2,sticky=N+S+W+E)

   btnKotv = Button(Nastrwindow,text=" kotv",command=btnKotv_clik)
   btnKotv.grid(row=12, column=3,sticky=N+S+W+E,columnspan =2)

   namelabel9="Коэф. токосьемника:"
   l9 = Label(Nastrwindow,text=namelabel9, font="Arial 12")
   l9.grid(row=13, column=0,columnspan =2)

   labelCurrent.grid(row=13, column=2)

   btnCurren = Button(Nastrwindow,text=" kcurrent",command=btnCurrent_clik)
   btnCurren.grid(row=13, column=3,sticky=N+S+W+E,columnspan =2)
   
   namelabel10="Коэф. калибровочного устройства:"
   l10 = Label(Nastrwindow,text=namelabel10, font="Arial 12")
   l10.grid(row=14, column=0,columnspan =2)
   labelkkal.grid(row=14, column=2)

   btnkkal = Button(Nastrwindow,text=" kkal",command=btnkkal_clik)
   btnkkal.grid(row=14, column=3,sticky=N+S+W+E,columnspan =2)

   namelabel11="параметры усилителя:"
   l11 = Label(Nastrwindow,text=namelabel11, font="Arial 12")
   l11.grid(row=15, column=0,columnspan =2)
   labelAmplifier.grid(row=15, column=2)

   btnAmplifier = Button(Nastrwindow,text=" amplifier",command=btnamplifier_clik)
   btnAmplifier.grid(row=15, column=3,sticky=N+S+W+E,columnspan =2)

   namelabel12="Прибавление мощности, дБ:"
   l12 = Label(Nastrwindow,text=namelabel12, font="Arial 12")
   l12.grid(row=16, column=0,columnspan =2)
   label_MaxGendelta=Entry(Nastrwindow, width=10)
   label_MaxGendelta.grid(row=16, column=2,sticky=N+S+W+E)
   label_MaxGendelta.insert(0, config.get('workdata','maxgendelta'))

   namelabel13="Точность установки уровня, дБ:"
   l13 = Label(Nastrwindow,text=namelabel13, font="Arial 12")
   l13.grid(row=17, column=0,columnspan =2)
   label_deltaLevel=Entry(Nastrwindow, width=10)
   label_deltaLevel.grid(row=17, column=2,sticky=N+S+W+E)
   label_deltaLevel.insert(0, config.get('workdata','deltalevel'))

   namelabel14="макс. кол-во шагов:"
   l14 = Label(Nastrwindow,text=namelabel14, font="Arial 12")
   l14.grid(row=18, column=0,columnspan =2)
   label_MaxNumSter=Entry(Nastrwindow, width=10)
   label_MaxNumSter.grid(row=18, column=2,sticky=N+S+W+E)
   label_MaxNumSter.insert(0, config.get('workdata','maxnumster'))


   btnnorma = Button(Nastrwindow,text=" Принять ",command=btnnorma_clik)
   btnnorma.grid(row=20, column=1,sticky=N+S+W+E)

   btnotmena = Button(Nastrwindow,text=" Отменить ",command=btnotmena_clik)
   btnotmena.grid(row=20, column=2,sticky=N+S+W+E)

   Nastrwindow.transient(root)
   Nastrwindow.grab_set()
   Nastrwindow.focus_set()   
   Nastrwindow.wait_window()   
# -------------------------------------------------------------------------------

def Kalibrovka():
   def save():
      config.set('workdata','BeginFreq',str(label_begin_freq.get()))
      config.set('workdata','EndFreq',str(label_end_freq.get()))
      config.set('workdata','stepfreq',str(label_step_freq.get()))
      config.set('workdata','steptype',str(combosteptype.current()))
      file_name=labelkalltable['text']
      #f=os.path.relpath(file_name , start='./kal')
      #print(f)
      config.set('workdata','kaltable',file_name)
      labelkalltable.config(text = file_name)

   def StartProdKal():
      workdata[wdBeginFreq]= workdata[wdfreq]
      StartKal()
      
   def StartBeginKal():
      workdata[wdBeginFreq]=float(config.get('workdata','beginfreq'))
      StartKal()
   
   def StartKal():
      print("StartKal")
      global threadcommand
      global Work_Table
      global Kal_Table
      save()
      
      BeginFreq=float(label_begin_freq.get())
      EndFreq=float(label_end_freq.get())
      print('\r\nstartkall:\r\n',BeginFreq,EndFreq,'\r\n')
      #workdata[wdBeginFreq]=float(config.get('workdata','beginfreq'))
      workdata[wdEndFreq]=float(config.get('workdata','endfreq'))
      workdata[wdStepFreq]=float(config.get('workdata','stepfreq'))
      workdata[wdStepType]=int(config.get('workdata','steptype'))
      workdata[wdMaxGendelta]=int(config.get('workdata','maxgendelta')) #MaxGendelta =10  #ограничение на  прибавление в можности
      workdata[wddeltaLevel]=int(config.get('workdata','deltalevel'))#    #deltaLevel=1    # точность установки
      workdata[wdMaxNumSter]=int(config.get('workdata','maxnumster')) #     #MaxNumSter=30  # макс кол-во шагов при настройка ( в случае внезапной нелинейности схемы)
      workdata[wdfile_name_amplifier]=config.get('workdata','amplifier')#file_name_amplifier
      workdata[wdfile_name_otvetvitel ]=config.get('workdata','fileotvet')#file_name_otvetvitel
      workdata[wdfile_koef_kallibrovochnogo_us ]=config.get('workdata','filekkal')#kal_otvetvitel



      # загружаем  калибровочную таблицу
      file_name=config.get('workdata','kaltable')# kal table
      data=[]
      File  = open("./kaltable/"+file_name)
      strdata= File.read()
      File .close()	    
      strdata=(strdata.split())
      for i in range(len(strdata)):
         data.append(float(strdata[i]))
      data.insert(0,7)

      Kal_Table=data
      
      
      LoadTable()
      Work_Table=lib_kalibrovka.CreateFreqTable (data,workdata[wdBeginFreq],workdata[wdEndFreq])
      lib_kalibrovka.printkaltabl(Work_Table)
      
      workdata[wdid_gen]    = [0,int(config.get('workdata','typegenport')),        int(config.get('workdata','genport')),        int(config.get('workdata','genportdata')),    int(config.get('workdata','gentype'))]
      workdata[wdid_powmet] = [0,int(config.get('workdata','typepowermeterport')), int(config.get('workdata','powermeterport')), int(config.get('workdata','powermeterdata')), int(config.get('workdata','powermetertype'))]
      workdata[wdid_kalmet] = [0,int(config.get('workdata','typekalmeterport')),   int(config.get('workdata','kalmeterport')),   int(config.get('workdata','kalmeterdata')),   int(config.get('workdata','kalmetertype'))]

      #print(workdata)

      # проверка параметров запуска по частотам применяемого оборудованрия
      start=0
      if ((start==0) & (workdata[wdBeginFreq]<lib_kalibrovka.datakaltabl(workdata[wdkal_otvetvitel],0,0))): # начальная частота меньше частоты ответвителя
         #  13, #kal_otvetvitel=[]   
         print(lib_kalibrovka.datakaltabl(workdata[wdkal_otvetvitel],0,0))
         start=131   

      if ((start==0) & (workdata[wdBeginFreq]<lib_kalibrovka.datakaltabl(workdata[wdkal_kalprobe],0,0))): # начальная частота меньше частоты пробника
      	 # 14, #kal_kalprobe=[]
         print(lib_kalibrovka.datakaltabl(workdata[wdkal_kalprobe],0,0))   
         start=141   

      if ((start==0) & (workdata[wdBeginFreq]<lib_kalibrovka.datakaltabl(workdata[wdkal_usilitel],0,0))):  # начальная частота меньше частоты усилителя
         # 15, #kal_usilitel=[]
         print(lib_kalibrovka.datakaltabl(workdata[wdkal_usilitel],0,0))   
         start=151   

      if ((start==0) & (workdata[wdEndFreq]>lib_kalibrovka.datakaltabl(workdata[wdkal_otvetvitel],0,lib_kalibrovka.lenkaltabl(workdata[wdkal_otvetvitel])-1 ))): # конечная частота больще частоты ответвителя
         #  13, #kal_otvetvitel=[]   
         print(lib_kalibrovka.datakaltabl(workdata[wdkal_otvetvitel],0,lib_kalibrovka.lenkaltabl(workdata[wdkal_otvetvitel])-1))
         start=132   

      if ((start==0) & (workdata[wdEndFreq]>lib_kalibrovka.datakaltabl(workdata[wdkal_kalprobe],0,lib_kalibrovka.lenkaltabl(workdata[wdkal_kalprobe])-1))): # конечная частота больще  частоты пробника
      	 # 14, #kal_kalprobe=[]
         print(lib_kalibrovka.datakaltabl(workdata[wdkal_kalprobe],0,lib_kalibrovka.lenkaltabl(workdata[wdkal_kalprobe])-1))   
         start=142   

      if ((start==0) & (workdata[wdEndFreq]>lib_kalibrovka.datakaltabl(workdata[wdkal_usilitel],0,lib_kalibrovka.lenkaltabl(workdata[wdkal_usilitel])-1))):  # конечная частота больще  частоты усилителя
         # 15, #kal_usilitel=[]
         print(lib_kalibrovka.datakaltabl(workdata[wdkal_usilitel],0,lib_kalibrovka.lenkaltabl(workdata[wdkal_usilitel])-1))   
         start=152   



      workdata[wdfasttimepause]=0
      print("\r\nstart=",start)
      #print("\r\n", data)
      if (start==0):
        thread1 = Thread(target= kallcicle)  
        threadcommand=0
        thread1.start()
      
   def StopKal():
     global threadcommand
     global workdata
     threadcommand=1
     workdata[wdfasttimepause]=1
     print("StopKal")  
         
   def btnkallTabl_clik():
      print("tabbl _ kall")
      file_name = fd.askopenfilename(initialdir='./kaltable',filetypes=[('kal_types','*.kal')])
      File = open(file_name)
      kal_tabl = File.read()
      File.close()
      f=os.path.relpath(file_name , start='./kaltable')
      config.set('workdata','kaltable',f)
      labelkalltable.config(text = f)
     # files = file_name




      
   def savexit():
      print("savexit")
      save()
      f = open(config_file, 'w')
      config.write(f)
      f.close() #     config.set('workdata','kalltable',f)
      #labelKotv.config(text = f)
      Kallwindow.destroy()
      Kallwindow.update() 

   def timing():
      while (1):
        label_tek_freq.delete(0,last=END)
        label_tek_freq.insert(0,str(workdata[wdfreq] ))
        label_tek_kal.delete(0,last=END)
        label_tek_kal.insert (0,str(workdata[wdlevel]))
        #print("time")
        sleep(0.3)
        #if (threadcommand!=0):
           #break
       
   print("Kalibrovka")
   workdata[wdfreq] =0
   workdata[wdlevel]=0
   Kallwindow = Toplevel( )
   Kallwindow_label_0_0="Режим калибровки"
   Kallwindow_l0 = Label(Kallwindow,text=Kallwindow_label_0_0, font="Arial 20")
   Kallwindow_l0.grid(row=0, column=0,columnspan =4)

   labelkalltable=Label(Kallwindow,text=config.get('workdata','kaltable'), font="Arial 12")


   namelabel1="Частота,МГц,уровень:"
   l1 = Label(Kallwindow,text=namelabel1, font="Arial 12")
   l1.grid(row=2, column=0)

   label_tek_freq=Entry(Kallwindow, width=10)
   label_tek_freq.grid(row=2, column=2,sticky=N+S+W+E)

   label_tek_kal=Entry(Kallwindow, width=10)
   label_tek_kal.grid(row=2, column=3,sticky=N+S+W+E)

   #label_tek_freq.insert(str(workdata[wdlevel]))
   #label_tek_kal.insert(str( workdata[wdlevel]))

   btnStart = Button(Kallwindow,text=" СТАРТ",command= StartBeginKal)
   btnStart.grid(row=3, column=0,columnspan =2,sticky=N+S+W+E)

   btnPause = Button(Kallwindow,text=" Повторить",command=StartProdKal)
   btnPause.grid(row=3, column=2,sticky=N+S+W+E)

   btnStop = Button(Kallwindow,text=" СТОП",command=StopKal)
   btnStop.grid(row=3, column=3,sticky=N+S+W+E)


   namelabel9="Калибровочная таблица:"
   l9 = Label(Kallwindow,text=namelabel9, font="Arial 12")
   l9.grid(row=4, column=0,columnspan =2)

   labelkalltable.grid(row=4, column=2)
   btnkalltable = Button(Kallwindow,text=" Выбрать",command=btnkallTabl_clik)
   btnkalltable.grid(row=4, column=3,sticky=N+S+W+E)

   namelabel1="Нач.Частота, МГц:"
   l1 = Label(Kallwindow,text=namelabel1, font="Arial 12")
   l1.grid(row=5, column=0,columnspan =2)
   label_begin_freq=Entry(Kallwindow, width=10)
   label_begin_freq.grid(row=5, column=2,sticky=N+S+W+E)
   label_begin_freq.insert(0, config.get('workdata','BeginFreq'))

   namelabel2="Кон. Частота, МГц:"
   l2 = Label(Kallwindow,text=namelabel2, font="Arial 12")
   l2.grid(row=6, column=0,columnspan =2)
   label_end_freq=Entry(Kallwindow, width=10)
   label_end_freq.grid(row=6, column=2,sticky=N+S+W+E)
   label_end_freq.insert(0, config.get('workdata','EndFreq'))

   namelabel3="Шаг Частоты:"
   l3 = Label(Kallwindow,text=namelabel3, font="Arial 12")
   l3.grid(row=7, column=0,columnspan =2)
   label_step_freq=Entry(Kallwindow, width=10)
   label_step_freq.grid(row=7, column=2,sticky=N+S+W+E)
   label_step_freq.insert(0, config.get('workdata','stepfreq'))

   combosteptype = ttk.Combobox(Kallwindow, 
                            values=[
                                    "%", 
                                    "кГц",
                                    "MГц"])
   combosteptype.grid(row=7, column=3,sticky=N+S+W+E)
   combosteptype.current(config.get('workdata','steptype'))

   btnexit = Button(Kallwindow,text=" Сохранить и выйти",command=savexit)
   btnexit.grid(row=8,column=0,columnspan =4,sticky=N+S+W+E)
   threadcommand=0
   t=Thread(target=timing)
   t.start()
   
   
def StartWork():	
  global threadcommand
  BeginFreq=float(label_begin_freq.get())
  EndFreq=float(label_end_freq.get())
  print('\r\nstartkall:\r\n',BeginFreq,EndFreq,'\r\n')
  thread1 = Thread(target= workcicle, args=('+'))  
  threadcommand=0
  thread1.start()
#  thread1.join();


def StopWork():
  global threadcommand
  threadcommand=1
  print("StopWork")
  
config = configparser.ConfigParser()  # создаём объекта парсера
config.read(config_file )  # читаем конфиг

root = Tk()
labelkalltable=Label(root,text=config.get('workdata','worktable'), font="Arial 12")


def btnkallTabl_clik():
      print("tabbl _ kall")
      file_name = fd.askopenfilename(initialdir='./worktable',filetypes=[('kal_types','*.kal')])
      File = open(file_name)
      kal_tabl = File.read()
      File.close()
      f=os.path.relpath(file_name , start='./worktable')
      config.set('workdata','worktable',f)
      labelkalltable.config(text = f)




namelabel_0_0="Испытания "
l0 = Label(text=namelabel_0_0, font="Arial 20")
l0.grid(row=0, column=0,columnspan =4)

namelabel9="Калибровочная таблица:"
l9 = Label(root,text=namelabel9, font="Arial 12")
l9.grid(row=1, column=0,columnspan =2)

labelkalltable.grid(row=1, column=2)
btnkalltable = Button(root,text=" Выбрать",command=btnkallTabl_clik)
btnkalltable.grid(row=1, column=3,sticky=N+S+W+E)

namelabel1="Частота, МГц:"
l1 = Label(text=namelabel1, font="Arial 12")
l1.grid(row=2, column=0)

btnNextfreq = Button(text=" << ")
btnNextfreq.grid(row=2, column=1,sticky=N+S+W+E)

label_tek_freq=Entry(root, width=10)
label_tek_freq.grid(row=2, column=2,sticky=N+S+W+E)


btnPredfreq = Button(text=" >> ")
btnPredfreq.grid(row=2, column=3,sticky=N+S+W+E)

btnStart = Button(text=" СТАРТ",command=StartWork)
btnStart.grid(row=4, column=1,sticky=N+S+W+E)

btnPause = Button(text=" ПАУЗА")
btnPause.grid(row=4, column=2,sticky=N+S+W+E)

btnStop = Button(text=" СТОП",command=StopWork)
btnStop.grid(row=4, column=3,sticky=N+S+W+E)

namelabelt1="Воздействия, мс:"
lt1 = Label(text=namelabelt1, font="Arial 12")
lt1.grid(row=5, column=0,columnspan =2)

label_time=Entry(root, width=10)
label_time.grid(row=5, column=2,sticky=N+S+W+E)
label_time.insert(0, config.get('workdata','worktime'))

namelabelt2="Пауза, мс:"
lt2 = Label(text=namelabelt2, font="Arial 12")
lt2.grid(row=6, column=0,columnspan =2)

label_pause=Entry(root, width=10)
label_pause.grid(row=6, column=2,sticky=N+S+W+E)
label_pause.insert(0, config.get('workdata','workpause'))



namelabel1="Нач.Частота, МГц:"
l1 = Label(text=namelabel1, font="Arial 12")
l1.grid(row=8, column=0,columnspan =2)

label_begin_freq=Entry(root, width=10)
label_begin_freq.grid(row=8, column=2,sticky=N+S+W+E)
label_begin_freq.insert(0, config.get('workdata','BeginFreq'))
#print (config.get('workdata','BeginFreq'))
#config.get('section_a', 'string_val')


namelabel2="Кон. Частота, МГц:"
l2 = Label(text=namelabel2, font="Arial 12")
l2.grid(row=9, column=0,columnspan =2)

label_end_freq=Entry(root, width=10)
label_end_freq.grid(row=9, column=2,sticky=N+S+W+E)
label_end_freq.insert(0, config.get('workdata','EndFreq'))



btnPribors = Button(text=" Настройка оборудования",command=NastrPribor)
btnPribors.grid(row=10, column=1,sticky=N+S+W+E)

btnKallibr = Button(text=" Режим калибровки",command=Kalibrovka)
btnKallibr.grid(row=10, column=3,sticky=N+S+W+E)

root.mainloop()