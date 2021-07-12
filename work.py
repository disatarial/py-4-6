#Основной цикл программы
#import configparser  # импортируем библиотеку работы с INI-шками
#config = configparser.ConfigParser()  # создаём объекта парсера
import serial
from time import sleep
import math
import struct

file_name_amplifier= "./pribor/amplifier.kal"
file_name_otvetvitel="./pribor/otvetvitel.kal"
file_name_kalprobe="./pribor/kallprobe.kal"

# оборудование
tabl_pribors=[0,0,0,0,0];  # генератор, измеритель мощности,  измеритель калибровки (ток, поле)
#generator=""
#usilitel
#otvetvitel
#powermetr
#injector
#currentmeter
import lib_kalibrovka
import generator
import fieldmeter
# калибровочные таблички
#Kal_Table=[] # табличка для настройки оборудованияя [freqmin,freqmax,step,type_step, level, genlevel]
Kal_Table=[7 , 1,10,1,1,3,4,-10 ,  10,100,10,1,5,6, -10]     

Work_Table=[] # табличка для настройки оборудованияя [freq,level, minGenlevel, powerlevel,currentlevel,genlevel,mingenlevel]
kal_otvetvitel=[]	# характеристика ответвителя  [Freq db]
kal_kalprobe=[]	# характеристика  токосъемника [Freq db]
kal_usilitel=[]    # для усилителей  максимальный сигнал которых   зависит от частоты [Freq db]

# все оборудование обрабатывается ИФАМИ 
# т.е. есть герераторы RS smb100,keysighte37243..  команды записи данных в них отличаются
# и в зависимости от того каким генератором работаем "If-ом" выбираем команды 
# по этим идентификаторам
id_gen=1
id_powmet=1
id_curmet=0

Freq=0
NumberFreq=0
# начальные данные
BeginFreq=5
EndFreq=50
StepFreq=-1
StepType=0  # тип  0 - линейный шаг, 1 - процентный,  2 - по таблице
MaxGendelta =10  #ограничение на  прибавление в можности
deltaLevel=1    # точность установки
MaxNumSter=30  # макс кол-во шагов при настройка ( в случае внезапной нелинейности схемы)

def LoadTable():
   global Work_Table
   print("LoadTable\r\n")
   # усилитель
   FilePribor = open(file_name_amplifier)
   kal_amplifier = FilePribor.read()
   FilePribor.close()
   print("kal_amplifier\r\n",kal_amplifier)
   # ответвитель
   FilePribor = open(file_name_otvetvitel)
   kal_otvetvitel = FilePribor.read()
   FilePribor.close()
   print("kal_otvetvitel\r\n",kal_otvetvitel)
   # ответвитель
   FilePribor = open(file_name_kalprobe)
   kal_kalprobe = FilePribor.read()
   FilePribor.close()
   print("kal_kalprobe\r\n",kal_kalprobe)
   
   Work_Table =lib_kalibrovka.CreateFreqTable (Kal_Table)   
   
def OpenPribors():
   global tabl_pribors
   print("OpenPribors\r\n")
#   genport=6
#   nameport = "\\\\.\\COM"+ str(genport)	
#   Interfaces = serial.Serial(nameport)
#   Interfaces.baudrate = 115200
#   Interfaces.timeout=0
#   tabl_pribors[0]=Interfaces
   tabl_pribors[0]=generator.Open(id_gen,17,115200)

#   meterport=36
#   nameport = "\\\\.\\COM"+ str(meterport)	
#   Interfaces = serial.Serial(nameport)
#   Interfaces.baudrate = 9600
#   Interfaces.timeout=0
#   tabl_pribors[2]=Interfaces
   tabl_pribors[2]=fieldmeter.Open(id_curmet,37,115200)

#   GenInterfaces .close()

def ClosePribor():
   global tabl_pribors
   generator.Close(id_gen,tabl_pribors[0])
   fieldmeter.Close(id_curmet,tabl_pribors[2])

#   tabl_pribors[0].close()
#   tabl_pribors[2].close()   


def WriteBeginData():
   global Freq, BeginFreq, EndFreq, StepFreq,NumberFreq
   print("WriteBeginData\r\n")
   if (StepFreq > 0): #при положительной виличине - идем вверх,иначе -вниз по частоте 
      Freq=BeginFreq  # устанавливаем "начальную"  частоту 
   else: 
      Freq=EndFreq  # устанавливаем "конечную" частоту 
   NumberFreq=lib_kalibrovka.FindFreqNum(Freq,Work_Table)


def FastPause( time): # пауза которая может быстро закончиться
   for i in range (int(time/50)):
      sleep(0.05) 

          
# РЕЖИМ калибровки
def Kall():
   global Freq
   global tabl_pribors, NumberFreq
   #   global Work_Table
   Ures=1
   cicle=1 # переменная окончания цикла передора по частоте
   #готовим таблицы  для оборудования, загружаем их.
   LoadTable()
   # готовим приборы, открываем  порты, настраиваем и проверяем связь
   OpenPribors()
   # устанавливаем начальные данные  проверяем их правильность
   WriteBeginData()   
   #подаем генератору команду  подачи мощности 
#   generator.powerOn()

   while (cicle ): 
      print(NumberFreq)
#      genlevel=-120
      NumSter=0
      Freq=Work_Table[NumberFreq,0]
      # подаем частоту с генератора
      generator.WriteFreq(id_gen,tabl_pribors[0],Freq)    #handle_gen,id_gen,Freq
      # =========================================================================================================================
      # подаем мощность с генератора
      genlevel=Work_Table[NumberFreq,5]
      generator.Write_Level(id_gen,tabl_pribors[0],genlevel)    #handle_gen,id_gen,Freq
      
      
      # измеряем сигнал на измерителе, добавляем его коэффициент из таблички
      Ures=fieldmeter.ReadLevel(id_curmet,tabl_pribors[2]) # ...read....
 #     str1="#00?T*\r\n"
 #     tabl_pribors[2].write(str1.encode())
 #     FastPause(300)
 #     str1=(tabl_pribors[2].readline())
 #     str2=str1[1 : 5]
 #     print(math.sqrt(struct.unpack("<f",str2)[0]))
      
      # MaxNumSter < NumSter # добавить еще одно условие на вызод из цикла 
      flag=(abs(Work_Table[NumberFreq,1]+deltaLevel-Ures)> deltaLevel)
      print("flag=",flag,Work_Table[NumberFreq,1],deltaLevel,Ures)
      while flag: 
         print("while:")
         FastPause(1000)
         NumSter=NumSter+1
#	 # подаем мощность с генератора
         generator.Write_Level(id_gen,tabl_pribors[0],genlevel)    #handle_gen,id_gen,Freq
#       
#         # измеряем сигнал на измерителе, добавляем его коэффициент из таблички
#         Ures=1 # ...read....
#         delta=0
#         # вычисляем новое значение генератора, считая что все линейно!
         delta=lib_kalibrovka.NewAmplituda(Work_Table[NumberFreq,1]+deltaLevel,genlevel,Ures)
#         print(delta,genlevel,Ures)
#         # требуется прибачить очень много? тогда ограничиваем прибавление значением MaxGendelta
         if (delta > MaxGendelta):
            genlevel=genlevel+MaxGendelta
         else:
            genlevel=genlevel+delta
         # ограничиваем максимальный сигнал.(данные должны братся из таблице усилителя
         if (genlevel>30): 
            genlevel=30
         Ures=fieldmeter.ReadLevel(id_curmet,tabl_pribors[2]) # ...read....	 
         flag=(abs(Work_Table[NumberFreq,1]+deltaLevel-Ures)> deltaLevel)
         print("flag=",flag,Work_Table[NumberFreq,1],Ures)

      NumberFreq=NumberFreq+1
      if (NumberFreq>(len(Work_Table)-1)): 
         cicle =0	 
      else:
         Freq=Work_Table[NumberFreq,0]

      # условие окончания цикла по частотам
      if ((StepFreq > 0)and (Freq > EndFreq)):  # цикл вверх по частоте
         cicle =0
      if ((StepFreq < 0)and (Freq < BeginFreq)):  # цикл вниз по частоте
         cicle =0	 
      FastPause(1000)
#      NumberFreq=NumberFreq+1
   #измеряем сигнал на ответвителе, добавляем его коэффициент из таблички
   Uotv=0 # ...read....

   ClosePribor()
   # сохраняем полученную табличку ( во временный файл?): частота, уровень, мощность, ток, уровень генератора, мин уровень генератора
   
"""   
   while cicle : 
      if (StepFreq > 0)and (Freq > EndFreq):  # цикл вверх по частоте
	  cicle =false
      if (StepFreq < 0)and (Freq < BeginFreq):  # цикл вниз по частоте
	  cicle =false

      if StepType = 1:
         Freq=Freq*(1+StepFreq)
      else if   StepType =2:
	  Freq=Freq+StepFreq   # тутдолжна быть табличные данные для которых  пересчета нет пока
      else 
	  Freq=Freq+StepFreq   # просто прибавляем частоту
"""

#print (lib_kalibrovka.dBuVtoV(120))   

Kall()