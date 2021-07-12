import serial
import lib_kalibrovka


def Open(interface,adress,data):
  print("Open generator")
  if (interface==1):  # КОМ -ПОРТ
    nameport = "\\\\.\\COM"+ str(adress)	
    print("interface: COM PORT",nameport, data)  #data = speed
    handle = serial.Serial(nameport)
    handle.baudrate = 115200
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
      print("write freq generator jds6600")
      str1=":w23=" + str(Freq*1e8)+".\r\n"
      print(str1)
      handle.write(str1.encode())
  else:
      print("no generator write  freq")

 
def WriteLevel(handle,ident,Level):
  if (ident==1):
      print("write level generator jds6600")
      level=lib_kalibrovka.dBmtoV(Level)
      str1=":w25=" + str(level*1e3)+".\r\n"
      print(str1)
      handle.write(str1.encode())
  else:
      print("no generator write  level")