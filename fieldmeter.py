import serial
import lib_kalibrovka
from time import sleep
import math
import struct

def Open(interface,adress,data):
  print("Open fieldmeter")
  if (interface==1):  # КОМ -ПОРТ
    nameport = "\\\\.\\COM"+ str(adress)	
    print("interface: COM PORT",nameport, data)  #data = speed
    handle = serial.Serial(nameport)
    handle.baudrate =data # 115200
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
  if (ident==1):
      print("EP60x izmeritel")  
  elif (ident==2):
      print("write freq E3361c:")
      #str1="CF 5MZ\r\n\r\n\r\n "
      #str2=str1.encode()
      #print(str2)
      #handle.write(str2)
  else:
      print("no izmeritel write  freq")
      
 
 
def ReadLevel(handle,ident):
  if (ident==1): #Narda EP60X
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
  elif (ident==2):
     print("advantest read:", 0)   
     str1=" PS\r\n PS\r\n PS\r\n"
     handle.write("dass\n\r".encode())
     return 0
     
  else:
     print("no field meter command read:",)   
     return 0