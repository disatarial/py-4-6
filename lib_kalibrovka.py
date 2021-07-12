import math

def VtodBuV(v):
   data= 20*math.log10(v*1e6)
   return data
   
def dBuVtoV(db):
   data= math.pow(10,db/20)/1e6
   return data

def dBmtoV(db):
   data=math.pow(10,(db+107)/20)/1e6
   return data
   
   
# работа с калибровочными данными
# пересчитать табличный номер xy в линейный x
def numkaltabl(n,x,y):
    return y*n+x+1
    
def adrkaltabl(tabl,x,y):
    n=tabl[0]
    return numkaltabl(n,x,y)   
     
#  получить данные  таблицы по координатам х,y 
def datakaltabl(tabl,x,y): 
    n=tabl[0]
    return tabl[numkaltabl(n,x,y)]
   
# кол-во строчек в таблице
def lenkaltabl(tabl): 
   n=int((len(tabl)-1)/tabl[0])
   return n
   
# добавление строчки
def addstrkaltabl(tabl): 
   for i in range (tabl[0]):
      tabl.append(0)
   return tabl  
   
 # напечатать таблицу   
def printkaltabl(tabl):
   print("xmax=",tabl[0],"ymax=",lenkaltabl(tabl))
   for i in range(lenkaltabl(tabl)):  # построчно
      for j in range(tabl[0]):  # внутри строки
         print(datakaltabl(tabl,j,i)," ",end=''),
      print("")


# "Простая" калибровка [ freq  data ]
# передаем текущую частоту   и таблицу и получаем номер строки 
      
# n - номер столбца с которым сравниваем
def FindFreqNum ( tabl,freq,n):
   num=0
   for i in range(lenkaltabl(tabl)): # перебираем все строчки значения по порядку
      #print (i,tabl[i,0],freq)
      if freq>=datakaltabl(tabl,n,i):
         num=i
         #print ("for:",num,i,tabl[i,0])
   return num


      
# вычисляем следующую частоту  по шагу и типу шага
def NextFreq(freq,step,flag):
    if (flag):
       freq=freq+step
    else:
       freq=freq*(1+step/100)
    return freq   

def interpol(x,x1,x2,y1,y2,flag): # линейная интерполяция
   if flag:
     x=math.log10(x)
     x1=math.log10(x1)
     x2=math.log10(x2)    
   y= (y2-y1)/(x2-x1)*(x-x1)+y1  
   return  y
   
# Вычисляем ( выбираем) следующую частоту по калибровочной таблице
#def NextFreqTabl(num,tabl):
     
# создаем табличку для работы программы используя       
# "начальную" калибровочную таблицу [ freqmin,freqmax,step,type_step, levelbegin, levelend, logfreq, genlevel ]
#первые  2 строки забиты  нулями, счто бу всегда была 2-мерная матрица!!! а то numspy почему-то считает что эта штука может быть одномерной
# и начинает ругатся на то что обращаемся по 2м координатам!на не по одной

def CreateFreqTable(tabl,beginfreq,endfreq):
   number=0
   newtable=[7] # [number freq, minGenlevel, level, powerlevel,currentlevel,genlevel]
   #print(lenkaltabl(tabl))
   for i in range(lenkaltabl(tabl)):	# перебираем все строцки по порядку
      Freq=datakaltabl(tabl,0,i)		# начальная частота
      #if (Freq>=beginfreq):
      #  print("str=",i,"\r\n",number,Freq)
      while (Freq < datakaltabl(tabl,i,1)):
        print(Freq)
        if ((Freq>=beginfreq)and(Freq<=endfreq)):
           newtable.append(number)			# [number ]
           newtable.append(Freq)			 # [ freq,]
           newtable.append(datakaltabl(tabl,6,i))   # [  minGenlevel] 
           newtable.append(interpol(Freq,datakaltabl(tabl,0,i),datakaltabl(tabl,1,i),datakaltabl(tabl,4,i),datakaltabl(tabl,5,i),datakaltabl(tabl,3,i)))		#level	 # [  level]
           newtable.append(0)			 # [powerlevel]
           newtable.append(0)			 # [genlevel]
           newtable.append(0)			# [  ]
           number=number+1

	
        Freq=NextFreq(Freq,datakaltabl(tabl,2,i),datakaltabl(tabl,3,i))	   # вычисляем следующий шаг частоты
        #print(number,Freq,datakaltabl(tabl,2,i),datakaltabl(tabl,3,i))
      if ((Freq>=beginfreq)and(Freq<=endfreq)):
        # добавляем последнюю точку
        newtable.append(number)			# [number ]
        newtable.append(datakaltabl(tabl,1,i))	 # [ freq,]
        newtable.append(datakaltabl(tabl,6,i))   # [  minGenlevel] 
        newtable.append(interpol(Freq,datakaltabl(tabl,0,i),datakaltabl(tabl,1,i),datakaltabl(tabl,4,i),datakaltabl(tabl,5,i),datakaltabl(tabl,3,i)))	 #level		 # [  level]
        newtable.append(0)			 # [powerlevel]
        newtable.append(0)			 # [genlevel]
        newtable.append(0)			# [  ]
        number=number+1

      
      #newtable=np.append(newtable,[[tabl[i+2,1],tabl[i+2,4],0,0,0,0,tabl[i+2,5]]], axis = 0 )
      #newtable.append((datakaltabl(tabl,2,i),datakaltabl(tabl,5,i),datakaltabl(tabl,6,i),0,0,0,0))
   #printkaltabl(newtable)
   #print(newtable)  
   return  newtable
#def take(x,y, tabl):
#   return tabl[x,y]   
   
def NewAmplituda(kaldata,Ugen,Ures):
  # x=kaldata*Ugen/Ures         
   x= kaldata-Ures
   return x 
   

       # проверка генерации таблицы
 # "начальную" калибровочную таблицу 
 # [ 
 #freqmin, мин частота
 #freqmax, макс часота
 #step,    шагчастоты
 #type_step,   линейный .% шаг
 #levelbegin, начальный уровень ( для меняющегося  от частоты уровня) 
 #levelend,   конечный уровень ( для меняющегося  от частоты уровня) 
 #genlevel 
 #]
      
"""      
tabl=[7 , 1,10,1,1,3,4,-10 ,  10,100,10,1,5,6, -10]     
print(tabl,"\r\n")
print(lenkaltabl(tabl),"\r\n")

#addstrkaltabl(tabl)
print(tabl,"\r\n")
#print(datakaltabl(tabl,0,0))
printkaltabl(tabl)

#print(tabl[2,0])
newtable=CreateFreqTable (tabl)
#print(newtable)
#tabl=np.append(tabl,[[100,1000,1000,1,0]], axis = 0)
#print(tabl)
#"""

""" # проверка поиска частот
tabl=np.array([[1, 11],[2, 12],[3 ,13],[4, 14],[5, 15],[6, 16],[7, 17],[8, 19],[9, 19]],float) 
freq=5
print (tabl[1,0])
print (len(tabl))

num= FindFreqNum(freq,tabl)
print("num=",num)
# """     