#!/usr/bin/python3
#new version 10.1.6
import os
import time
import threading
import sys
import binascii
import pymysql
import argparse
from bluepy import btle
from bluepy.btle import Scanner,DefaultDelegate
#import mysql.connector
#from mysql.connector import Error
from datetime import datetime
import time
import math
import RPi.GPIO as GPIO
import requests
import json
import urllib
import requests
import shutil
import os.path
import urllib.request
from subprocess import check_output

GPIO.setmode(GPIO.BCM)
GPIO.setup(10, GPIO.OUT)

    
BBpin =27
GPIO.setup(BBpin,GPIO.OUT,initial=0)
#WFpin = 10
#GPIO.setup(BBpin,GPIO.OUT,initial =0)


def check_internet():
 while(1):
     
    url='http://www.google.com/'
    timeout=10
    GPIO.output(10,1)
    try:
        _ = requests.get(url, timeout=timeout)
        status = 1
    except requests.ConnectionError:
        print("İnternet not connected.")
        status = 0
    if(status == 1):
            print("net connected")
            for i in range(4):
                GPIO.output(10,1) 
                time.sleep(1)
                GPIO.output(10,0)        
                time.sleep(1)
            GPIO.output(10,0)
            
            
    else:
            print("not connected")
            #time.sleep(10)
            
                                    
urliThingsSenTrig = "http://178.128.165.237/php/api/createSensorTrigEvent.php"
tempUrl = "http://192.168.43.4:9090"
hotspotCon = ""
hotspotPass= ""
lastCmd = 0



def my_function(version):
        print(version)
        print(time.ctime())
        x = {"deviceId":dev.addr,
             "CurVersion":version,
             "LastTriggeredDevID": "MEuu3046"
            }

        y = json.dumps(x)
        print (y)
        r = requests.post("http://178.128.165.237/php/blehub/api/checkUpdateAvailable.php",y)
        print(r.text)
        wr = r.text
        w = json.loads(wr)
        #url =  (w[0]['FileList'][0]['url'])
        if(w[0]['UpdateAvailable']=="Yes"):
                for item in w[0]['FileList']:
                        #print(item['url'])
                        update_url = item['url']
                        print(update_url)
                        #response = urllib2.urlopen(update_url)
                        response = urllib.request.urlopen(update_url)
                        data = response.read()
                        # Write data to file
                        #data_folder = os.path.join('Documents/app')
                        save_path = '/home/pi/'
                        filename = item['filename']
                        completeName = os.path.join(save_path, filename) 
                        print(filename)
                        print(completeName)
                        file_ = open(completeName, 'wb')
                        file_.write(data)
                        file_.close()
                        file_size = item['size']
                        print(file_size)
                version = w[0]['VersionName']
                #print(x['CurVersion'])
                #file_path = filename
                s = os.path.getsize(completeName)
                #statinfo = os.stat(filename)
                #s=statinfo.st_size
                #print(filename)
                print(s)
                #print(file_size)
                a = int(s)
                b= int(file_size)
                print(a)
                print(b)
                if a==b:
                        print(filename)
                        print("File Downloaded")
                        
                        shutil.copy(completeName, '/home/pi/ithings') #path to be changed according to raspberry
                        os.system('sudo shutdown -r now')
                else:
                         print("File not Downloaded properly")

        else:
                print("no update available")

        #return version
        threading.Timer(60, my_function, (version,)).start() #to check for update every 2 hr 
        








def taskledoff():
    print("led timer expires")
    if(GPIO.input(BBpin)!=0):
        GPIO.output(BBpin,False)

def taskledWifi():
    print("led wifihot expires")
    for x in range(6):
        GPIO.output(BBpin,True)
        time.sleep(0.5)
        GPIO.output(BBpin,False)
        time.sleep(0.5)
    GPIO.output(BBpin,False)
    #ledtimer1.kill()  


        
def LogWrite(message):
    try:
        f= open("/home/pi/ithings/beaconlog1.txt","a+")
        datetimestr = time.strftime("%Y-%m-%d %H:%M:%S")
        #strmes = '\n'.join(map(str, message))
        strmes = datetimestr +"--"+str(message)
        f.write(strmes+"\r\n")
        f.close()
    except:
        print("Exception log writer->")
        print(sys.exc_info()[0])

def SendToiThings(devID):
      payload = {
            'deviceId': devID,
            'timeStamp': 'NA',
            'actionTypeId': 'Motion',
            'actionTypeDesc': 'Motion detected',
            'actionValue':'na',
            'subscriber':'santa@clara',
            'facilityName':'iorbit'
            }
      LogWrite("Send to server");
      payloadJson = json.dumps(payload)
      response = requests.put(urliThingsSenTrig, data=payloadJson)
      LogWrite(payloadJson)
      
def confWiFi(hotspot, passwd):
    
        print(hotspot)
        print(passwd)
        hp = ("network={\r\n\tssid=\"%s\"\r\n\tpsk=\"%s\"\r\n\tkey_mgmt=WPA-PSK\r\n}" % (hotspot, passwd))
        print(hp)
        with open('/home/pi/ithings/wpa_supplicant.conf', "r") as myf:
            data = myf.read();
            data = data+hp
            print(data)
        f = open('/etc/wpa_supplicant/wpa_supplicant.conf', "w+")
        f.write(data)


class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)


    def handleDiscovery(self,dev,isNewDev,isNewData):
        if isNewDev:
            print ("Discovered new Device %s" %(dev.addr))
        elif isNewData:
            print("Discovered new Data %s" %(dev.addr))

def check_size():


 b = os.path.getsize("/home/pi/ithings/beaconlog1.txt")
 if (b>5242880):
     f.truncate()
 print(b)

def GetManfacData(dev):
      for (adtype,desc,value) in dev.getScanData():
          if(desc.find("Manufacturer")!= -1):
              print(desc + ":" + value)
              return value


def BitCheck(bytearr):
    print("bit check")
    l = bytearray.fromhex(bytearr)
    print("converted")
    k=4
    new_num = l[5] >> (k - 1)
    if((new_num & 1)==1):
         #LogWrite("heartbeat occurs")
         print("heartbeat occurs")
         return 1
    else :     
         #LogWrite("no heartbeat")
         print(" no heartbeat occurs")
         return 0
         
print ("Starting check")

internet = threading.Thread(target = check_internet)
internet.start()

version = '10.1.6'
#dev_id = adress()


scanner = Scanner()

#main loop----
LogWrite("Starting...")
while True:
    try:
        
        devices = scanner.scan(2.0)
        for dev in devices:
            for (adtype,desc,value) in dev.getScanData():
                #print("helooooo")
                #print(desc.find("Name"))
                if (desc.find("Name") != -1):
                    if(value.find("iSensor")!=-1):
                        print(desc + ":" + value)
                        print("valu-e>"+value);
                        print(dev.getScanData())
                        print(dev.addr)
                       
                        LogWrite(dev.addr)
                        GPIO.output(BBpin,True)
                        ledtimer = threading.Timer(2.0,taskledoff)
                        ledtimer.start()
                        
                        my_function(version)
                        
                        bytearr =  GetManfacData(dev)
                        x=BitCheck(bytearr)
                        print (bytearr)
                        
                        if (x==1):
                           LogWrite("heartbeat occurs")
                        else :
                            SendToiThings(dev.addr)
                            LogWrite(" no heartbeat occurs")
                                
                        #SendToiThings(dev.addr)
                        LogWrite(dev.getScanData())
                        check_size() 
                                              
                        
                if value.find("546f6b2d") != -1: #looking for Tok- in payload
                    try:
                        bytearr = bytes.fromhex(value)
                        token = bytearr[11:19]#6:19
                        tokenStr = token.decode("utf-8")
                        print("token arr",token)
                        #print(bytearr)
                        print("token Str",tokenStr)
                        

                    except ValueError:
                        print("value error")

                if value.find("5749482d") != -1: #looking for WIH- in payload
                    try:
                        bytearr = bytes.fromhex(value)
                        token = bytearr[6:19]#6:19
                        tokenStr = token.decode("utf-8")
                        tokenStr=tokenStr.strip(' \t\r\n\0')
                        LogWrite(value)
                        print("Wifi HP",token)
                        LogWrite("wifi Name"+tokenStr)
                        print("WIFI HP Str",tokenStr)
                        hotspotCon = tokenStr
                        lastCmd=100
                    except ValueError:
                        print("value error")
                if value.find("5749502d") != -1:
                    try:
                         bytearr = bytes.fromhex(value)
                         token = bytearr[6:19]#6:19
                         tokenStr = token.decode("utf-8")
                         tokenStr=tokenStr.strip(' \t\r\n\0')
                         print("Wifi PASS",token)
                         print(value)
                         
                         LogWrite("wifi Pass"+tokenStr)
                         print("WIFI HP Pass",tokenStr)
                         hotspotPass = tokenStr
                         if(lastCmd != 200):
                             LogWrite("Creating hotspot in conf file->"+hotspotCon +" Pass->"+hotspotPass)
                             confWiFi(hotspotCon,hotspotPass)
                             GPIO.output(BBpin,True)
                             ledtimer1 = threading.Timer(1.0,taskledWifi)
                             ledtimer1.start()
                         lastCmd=200
                    except ValueError:
                        print("value error")
                
    except:
        print("Exception")
        # LogWrite("Exception")
        print(sys.exc_info()[0])
        #LogWrite(sys.exc_info()[0])
    time.sleep(0.2)
    #DT = datetime.now()
    #millisec = DT.timestamp() * 1000
    #checkdate = "select AT_StartTime,AT_EndTime from plt_accesstokens where AT_Token = '%"+tokenStr+"%'"; ";
    #mycursor.execute(checkdate)
    #result1 = mycursor.fetchone()
    #tupletime = datetime.strptime(result1[0],"%Y-%m-%dT%H:%M:%S.%fZ")
    #mills = tupletime.timestamp() * 1000
    #print(mills)
    #print(millisec)
    print ("waiting.....")
   

    
                    
                    



