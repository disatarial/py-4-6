import serial
import lib_kalibrovka
from time import sleep
import math
import struct

def Open(interface,adress,data):
  print("Open fieldmeter")
  if (interface==1):  # КОМ -ПОРТ
    print("interface: COM PORT",adress, data)  #data = speed
    nameport = "\\\\.\\COM"+ str(adress)	
    handle = serial.Serial(nameport)
    handle.baudrate = 9600
    handle.timeout=0
  elif (interface==2): # ETHERNET
    print("interface: ETHERNET",adress, data)  #data = port 
  else:
    handle =0
    print("no pribor")
  return handle
    
def Close(handle,interface):
    if (handle): # если ==0 то прибора не было 
      print("ClosePribors")
      handle.close()

def WriteFreq(handle,ident,Freq):
#  if (ident==1):
      print("no freq")
 
 
def ReadLevel(handle,ident):
  if (ident==1):
     str1="#00?T*\r\n"
     handle.write(str1.encode())
     #handle.write(str1.encode())
     sleep(0.50)
     str1=(handle.readline())
     #print(str1)
     str2=str1[1 : 5]
     #data=math.sqrt(struct.unpack("<f",str2)[0])
     data=math.sqrt(struct.unpack(" f",str2)[0])
     #print(data)
     print("ep600 read:",str2,data,lib_kalibrovka.VtodBuV(data))   
     return lib_kalibrovka.VtodBuV(data)
  else:
     print("no field meter command read:",)   
     return 0