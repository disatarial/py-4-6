from threading import Thread
from time import sleep

def cicle(s):
  global threadcommand
  while (1):
    print (s)
    sleep(1)
    if (threadcommand!=0):
      break
