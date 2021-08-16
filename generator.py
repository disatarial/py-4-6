import serial
import socket
import lib_kalibrovka


def Open(interface,adress,data):
  print("Open generator")
  if (interface==1):  # КОМ -ПОРТ
    nameport = "\\\\.\\COM"+ str(adress)	
    print("interface: COM PORT",nameport, data)  #data = speed
    handle = serial.Serial(nameport)
    handle.baudrate =data # 115200
    handle.timeout=0
  elif (interface==2): # ETHERNET
    print("interface: ETHERNET",adress, data)  #data = port 
    handle= socket.socket()
    handle.connect(str(adress), data)
  else:
    handle =0
    print("no pribor")
  return handle
    
def Close(handle,interface):
    if (handle): # если ==0 то прибора не было 
      print("ClosePribors")
      handle.close()

def WriteFreq(handle,interface,ident,Freq):
  if (ident==1):
      print("write freq generator jds6600")
      str1=":w23=" + str(Freq*1e8)+".\r\n"
      print(str1)
      handle.write(str1.encode())
  elif (interface==2): # ETHERNET
      print("write freq generator smb100")
      str1="FREQ " + str(Freq)+".\r\n"
      print(str1)
      handle.send(str1.encode())
  else:
      print("no generator write  freq")

def WriteOff(handle,interface,ident):
  if (ident==1):
      print("write off")
      str1=":w25=0.\r\n"
      print(str1)
      handle.write(str1.encode())
  elif (interface==2): # ETHERNET
      print("write off")
      str1="OUTP:STAT OFF " +".\r\n"
      print(str1)
      handle.send(str1.encode())
  else:
      print("no generator write  level")

def WriteOn(handle,interface,ident):
  if (ident==1):
      print("write on") 
  elif (interface==2): # ETHERNET
      str1="OUTP:STAT ON" +".\r\n"
      print(str1)
      handle.send(str1.encode())
  else:
      print("no generator write  level")
 
def WriteLevel(handle,interface,ident,Level):
  if (ident==1):
      print("write level generator jds6600")
      WriteOn(handle,interface,ident)
      level=lib_kalibrovka.dBmtoV(Level)
      str1=":w25=" + str(level*1e3)+".\r\n"
      print(str1)
      handle.write(str1.encode())
  elif (interface==2): # ETHERNET
      print("write level generator smb100")
      str1="LEVEL" + str(Freq)+".\r\n"
      print(str1)
      handle.send(str1.encode())
  else:
      print("no generator write  level")



def PowerOn(handle,interface,ident):
     print(PowerOn)

def PowerOff(handle,interface,ident):
     print(PowerOff)

def modulationOn(handle,interface,ident):
     print(modulationOn)

def modulationOff(handle,interface,ident):
     print(modulationOff)
