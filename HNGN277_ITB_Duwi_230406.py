import os
import time
import sys
import serial
import syslog
import matplotlib.pyplot as plt
import numpy as np
import RPi.GPIO as GPIO
import datetime
from read_shield_class import Shield  #{211128} chiba
import ADS1256                        #{211128} chiba
# import pigpio


""" HNGN001 Created on Tue Jun 11 08:34:11 2019
(two days before 190613) (1month before 190711)
This program was copied from HNGN277_220402C.py 
on 230322 for Duwi san of ITB"""

from ast import literal_eval
with open("HNGN277_cntl.txt", "r") as f:
    #text = f.readlines()
    text = f.read()
d= literal_eval(text)[0]

d_copy={"00":[
"""
Three cycles are set;
"i" cycle  0-9
"j" cycle  0-99
"k" cycle  0-999
>>
ON interval is set as follows:
("j",0,30) is "j" cycle of every 0-99, start on at 0 and off at cycle 30. 
>>
(This input is written as follows:)
GPIO[i]
[1]=heater1 = Heating bottom_drain_tank (bottom of bottom)
[2]=Valve_1 = inlet to Capasiter tank
[3]=Valve_2 = evacuation 
[4]=Heating pipe (core simulation)
[5]=#Cooling air blower
[6]=#not used
[7]=#not used
>>
Operation mode is in dababase dictionary as follows:
mode_1 = salt into loop from drain tank
mode_2 = drain salt to bottom tank evacuating gas from loop system
(End of Input ex@lanation)
"""
],

    "01":["heater1", "valve1", "valve2",  "heater2", "heater3", "heater4", "heater5"],
    "mode_1":[("i",0,0),  ("j",0,30),  ("i",0,0),    ("i",0,0),   ("i",0,0),   ("i",0,0),   ("i",0,0)],
    "mode_2":[("i",0,0),  ("i",0,0),  ("j",0,30),    ("i",0,0),   ("i",0,0),   ("i",0,0),   ("i",0,0)]
}

def GPIO_onuse_list(d):
	# インプットからオンにするGPIO番号だけぬきだして、情報を整理する
	# d=input, GPIO_onuse_list=output
    j=1
    GPIO_onu_list=[]
    for i in d["mode_2"]:
        if not(i[2]==0): 
            cycle=i[0]
            n_IO=j      #使っているGPIO
            i_end=i[2]  #リスト（0,40）の２番めの40が停止するサイクル番目。
            GPIO_onu_list.append((cycle,n_IO,i_end)) #タプルにしてONOFFスイッチに渡す
            #print(i[0],j,i[2])
        j+=1
    #print("GPIO_onuse_list=",GPIO_onu_list)
    return GPIO_onu_list

def OffGPIO(j):
    """
    （機能の説明）   {220402}
    GPIOをを止めるスイッチ。
    ループにセットしたGPIOと同じ数のコマンドをプログラムに並べて、
    j にセットした GPIOに信号を送る。
    機能は、ここで、単純にGPIOストップするだけにする。
    """
    #OBS! here we have set of numbers of GPIO's in the MS_loop  OBS!
    for i in range(1,7):
        if (i==1)and(i==j):GPIO.output(SSR1_GPIO_n, False)
        if (i==2)and(i==j):GPIO.output(SSR2_GPIO_n, False)
        if (i==3)and(i==j):GPIO.output(SSR3_GPIO_n, False)
        if (i==4)and(i==j):GPIO.output(SSR4_GPIO_n, False)
        if (i==5)and(i==j):GPIO.output(SSR5_GPIO_n, False)
        if (i==6)and(i==j):GPIO.output(SSR6_GPIO_n, False)
        if (i==7)and(i==j):GPIO.output(SSR7_GPIO_n, False)
    return

def OnGPIO(j):
    for i in range(1,7):
        if (i==1)and(i==j):GPIO.output(SSR1_GPIO_n, True)
        if (i==2)and(i==j):GPIO.output(SSR2_GPIO_n, True)
        if (i==3)and(i==j):GPIO.output(SSR3_GPIO_n, True)
        if (i==4)and(i==j):GPIO.output(SSR4_GPIO_n, True)
        if (i==5)and(i==j):GPIO.output(SSR5_GPIO_n, True)
        if (i==6)and(i==j):GPIO.output(SSR6_GPIO_n, True)
        if (i==7)and(i==j):GPIO.output(SSR7_GPIO_n, True)
    return

# GO/STOP control of this program {220128}
if not(os.path.exists('going.txt')):
	file1 = "going.txt"
	f=open(file1,"a+")

"""
Plot, plotting, プロット
"""
xdata = []
ydata1 = [] 
ydata2= []
plt.show()

axes = plt.gca()
axes.set_xlim(0, 1000)
axes.set_ylim(2.9, 3.5)
line1, = axes.plot(xdata, ydata1, 'r-')
line2, = axes.plot(xdata, ydata2, 'b-')


#// Thermocouple reader (M5 based) of Yoshizawa of 0.1sec
def read_m5(port,speed):	
	#The following line is for serial over GPIO	
	ser = serial.Serial(port,speed)
	#>>
	# Serial read section
	line = ser.readline()
	line2=line.strip().decode('utf-8')
	data = [str(val) for val in line2.split(",")]
	return data

#// タイムスタンプの設定
#   time stamp 
def time_stamp():   #// 時刻、時間（unix time）のセットアップ
  dt_now = datetime.datetime.now()
  time_stamp_out=dt_now.strftime('%Y-%m-%d %H:%M:%S.%f')
  return time_stamp_out


# GPIOをセットアップする
GPIO.cleanup()
#
# setting_up GPIO nr, AD_DA_shield_pin_nr 
SSR1_GPIO_n = 5   #21       Heating bottom_drain_tank (bottom of bottom)
SSR2_GPIO_n = 6   #22       Valve_1 inlet to Capasiter tank 
SSR3_GPIO_n = 13  #23       Valve_2 relief/evacuation
SSR4_GPIO_n = 19  #24       Heating pipe (core simulation)
SSR5_GPIO_n = 26  #25       Cooling air blower
SSR6_GPIO_n = 20  #28       not used
SSR7_GPIO_n = 21  #29       not used

#
GPIO.setmode(GPIO.BCM)
GPIO.setup(SSR1_GPIO_n, GPIO.OUT)
GPIO.setup(SSR2_GPIO_n, GPIO.OUT)
GPIO.setup(SSR3_GPIO_n, GPIO.OUT)
GPIO.setup(SSR4_GPIO_n, GPIO.OUT)
GPIO.setup(SSR5_GPIO_n, GPIO.OUT)
GPIO.setup(SSR6_GPIO_n, GPIO.OUT)
GPIO.setup(SSR7_GPIO_n, GPIO.OUT)


def All_shutdown():
	GPIO.output(SSR1_GPIO_n, False)
	GPIO.output(SSR2_GPIO_n, False)
	GPIO.output(SSR3_GPIO_n, False)
	GPIO.output(SSR4_GPIO_n, False)
	GPIO.output(SSR5_GPIO_n, False)
	GPIO.output(SSR6_GPIO_n, False)
	GPIO.output(SSR7_GPIO_n, False)
	return

""" 
{220401} {13:53 - } 
・　インプット読込みの代わりに、インプット（d=dictonary）を設定する。
・　ループは、1-1000まで（100秒サイクル）で回る＝＞kを使えば良い
・　オンにするGPIOに信号を送る
＿＿インプットを見て、オンにするGPIOの番号を、リストにする。
＿＿回る最初に、オンにするGPIOだけを選んで、GPIOをオンにする
・　回す回数がインプットで指定された回数（従来は i1f とか）でオフにする。
"""


"""
{220401} {17:45 - 18:15}
ループする時刻カウンター（iではなくてk）のループの中で
カウンターゼロで、使っている（onuse）GPIOをオンにする
うけとったGPIOのリストをみて、当該のカウンターでGPIOをストップさせる
"""


def OnOff(i,j,k,i1,i2,i3,i4,i5,i6,i7,i1f,i2f,i3f,i4f,i5f,i6f,i7f): 
	"""
    version = {220104}
    Here On/Off period is set in fixed cycle (eg., 0 to 99).
	"""
	if (i==i1):GPIO.output(SSR1_GPIO_n, True)
	if (j==j2):GPIO.output(SSR2_GPIO_n, True) #set on by j
	if (i==i3):GPIO.output(SSR3_GPIO_n, True)
	if (i==i4):GPIO.output(SSR4_GPIO_n, True)
	if (i==i5):GPIO.output(SSR5_GPIO_n, True) 
	if (i==i6):GPIO.output(SSR6_GPIO_n, True) 
	if (i==i7):GPIO.output(SSR7_GPIO_n, True) 
	#
	if (i==i1f):GPIO.output(SSR1_GPIO_n, False)
	if (j==j2f):GPIO.output(SSR2_GPIO_n, False) #set off by i 
	if (i==i3f):GPIO.output(SSR3_GPIO_n, False)
	if (i==i4f):GPIO.output(SSR4_GPIO_n, False)
	if (i==i5f):GPIO.output(SSR5_GPIO_n, False)
	if (i==i6f):GPIO.output(SSR6_GPIO_n, False) 
	if (i==i7f):GPIO.output(SSR7_GPIO_n, False)
	return 


#read thermocouple and put file/recording

#set port for temperature measurements
#port = sys.argv[1]    #for manual setup then use port = sys.argv[1]
port = "/dev/ttyUSB0"  #OBS! （２台以上つないでいるので）間違えないように確認のこと
speed = 19200

timetime0=time.time() #unix-time


#   {210716}
#   read pressure change and put file/recording
#   Pressure gauge reasing プレッシャーゲージのデータを読む
shield=Shield()
def get_gas_Kpascal():
	#reading_pressure_meter
	#MPS-C35R-NCA  OBS! C35 not P35
	p_volts=shield.read_shield() #{211128} chiba {211222} kinoshita
	d1=data1=float(p_volts[2])
	d2=data2=float(p_volts[3])
	#1.4V = 0Kpascal
	tsec=time.time()-timetime0
	s2=f"""time={tsec},p_volts {d1},{d2} """
	print (s2)RPi.GPIO
	return tsec,d1,d2

# data-recording
job_subject="SN2_Blk2_Operation"
file1 = "LP_HNGN277_" + job_subject + "_P&T-220403A.txt"
f=open(file1,"a+")
s2=f"""job250_job {job_subject} start  {time_stamp()}"""
print(s2)
f.write(s2 + "\n") 


# (initial) setting parameters of ssr_contorol status
global i,j,k;i,j,k=0,0,0
global i1,i2,i3,i4,i5,i6,i7;i1,i2,i3,i4,i5,i6,i7=0,0,0,0,0,0,0
global i1f,i2f,i3f,i4f,i5f,i6f,i7f;i1f,i2f,i3f,i4f,i5f,i6f,i7f=0,0,0,0,0,0,0


# =========================================================
# OBS! ==== set power-on/off at statements below  ==== OBS!
i1=0; i1f=0; i1f_set=i1f #Heating bottom_drain_tank (bottom of bottom)
j2=0; j2f=5; j2f_set=j2f #Valve_1 inlet to Capasiter tank
i3=0; i3f=0; i3f_set=i3f #Valve_2 evacuation 
i4=0; i4f=0; i4f_set=i4f #Heating pipe (core simulation)
i5=0; i5f=0; i5f_set=i5f #Cooling air blower
i6=0; i6f=0; i6f_set=i6f #not used
i7=0; i7f=0; i7f_set=i7f #not used

# もろもろのはじまり、まず電源を落としてから始める。
All_shutdown()

while os.path.exists('going.txt'):
	try:
		array=read_m5(port,speed) #reading thermo_cpuple, tc_reader 
		# cycles_control, where delta_time comes from tc_reader
		# memo, explanation ==>（588d1）

		for i_cntl in GPIO_onuse_list(d):
			if(i_cntl[0]=="i" and i==0):
				print("cycle_time_step_i==",i)
				OnGPIO(i_cntl[1])
			if(i_cntl[0]=="j" and j==0):
				print("cycle_time_step_j==",j)
				OnGPIO(i_cntl[1])
			if(i_cntl[0]=="k" and k==0):
				print("cycle_time_step_k==",k)
				OnGPIO(i_cntl[1])


		if i==0: #cycle of i is shortest time period and do 
			     #pick up of temperature at each cycle
			
			#print Tc and time_stamp 
			s12=f""" {time_stamp()}, {array}"""
			print(s12)
			Tc= [float(array[1]),float(array[2]),float(array[3]),float(array[4]),float(array[5]),
			float(array[6]),float(array[7]),float(array[8]),float(array[9]),float(array[10])]
			s12b=f"""print Tc Tc={Tc}, and maxTc_meas={max(Tc)}"""
			#print(s12b)

			i_list=[i,i1,i2,i3,i4,i5,i6,i7,i1f,i2f,i3f,i4f,i5f,i6f,i7f]
			#test pressure
			tsec,d1,d2=get_gas_Kpascal()
			
			""" plotting """
			#plotting 
			xdata.append(tsec)
			ydata2.append(d2)
			line2.set_xdata(xdata)
			line2.set_ydata(ydata2)
			plt.draw()
			plt.pause(1e-17)
		
		if i==0:  #print/write when j-cycle is over, which is independent of i-cycle
			# print pressure, P is changing very fast so that every one second data is necessary
			s13=f""" {time_stamp()}, P_Volt= {d2:.6f}"""
			s13f=f""" {time_stamp()}, P_Volt= {d2:.6f}, Tc= {Tc}, maxTc_meas={max(Tc)}, iL={i_list}"""
			print(s13)
			f.write(s13f + "\n") 
			print()

		# Drain_tank Pressure control by release valve
		d2_1=3.03
		d2_2=3.1
		d2_3=3.25

		"""
		if (d2>d2_1):
			i3f=0 #OBS! drain_tank is i3
		"""

		if (d2>d2_3):
			s13=f"""job_P2 exceeds limit {d1}, {d2}, do shutdowm""";print(s13);f.write(s13 + "\n")
		

		# GPIO_switching
		# OnOff(i,j,k,i1,i2,i3,i4,i5,i6,i7,i1f,i2f,i3f,i4f,i5f,i6f,i7f)

		#{220402}
		#implemented from ProtoTyping_220401.py in HNGN277 directory.
		#BEGIN
		for i_cntl in GPIO_onuse_list(d):
			if(i_cntl[0]=="i" and i==i_cntl[2]):
				print("cycle_time_step_i==",i)
				OffGPIO(i_cntl[1])
			if(i_cntl[0]=="j" and j==i_cntl[2]):
				print("cycle_time_step_j==",j)
				OffGPIO(i_cntl[1])
			if(i_cntl[0]=="k" and k==i_cntl[2]):
				print("cycle_time_step_k==",k)
				OffGPIO(i_cntl[1])
		#END

		#set cycle time here:
		i+=1;j+=1;k+=1
		if i==9:i=0     #cycle time= 1 seconds by setting 9
		if j==99:j=0    #cycle time= 10 seconds by setting 99
		if k==999:k=0   #cycle time= 100 seconds by setting 999
	#
	except ValueError as e:
		print(e,"i=",i)
	except IndexError as e:
		print(e, "i=",i)
		s="""ファイルの最期に到達。"""
		print(s)
	except Exception as e:
		print('Exception:',i,e)
	except KeyboardInterrupt:
		print ('exiting by cntl-C')
		All_shutdown()
		GPIO.cleanup()
		break
print("job1 end of " + job_subject)
All_shutdown()
GPIO.cleanup()
f.write("job1 end of " + job_subject + "\n") 

# final process
#pi.set_mode(gpio_pin0, pigpio.INPUT)
#pi.stop()

#sys.exit()
