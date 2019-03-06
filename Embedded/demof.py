# -*- coding: utf-8 -*-
"""
Created on Tue Feb 26 16:24:35 2019

@author: HP
"""

import socketio
import serial
import time
import random
import os

hosts = '120.79.148.35'
port = 7001
sio = socketio.Client()
serial = serial.Serial('COM6', 250000,timeout=0.5)
printing = 0
endprint =0 
startprint = 0

def read_gcode(filename):
    #读取gcode文件，读到list
    gcodelist=[]
    with open(filename,'r') as gcodefile:
        temp_gcodelist = gcodefile.readlines()
    for line in temp_gcodelist:
            gcodelist.append(line)
    return gcodelist

def print_model(gcodelist,ser,sio,printing,endprint,startprint):
    print("正在打印")
    global printing
    global endprint
    global startprint
    for line in gcodelist:
        line =str.encode(line)
        if line == ";End of Gcode":
            printing = 0
            endprint = 1
        else : 
            printing = 1        
        print(line)
        ser. write(str.encode("M105\n"))
        while True:
            read_order = ser.readline()
            if( "ok" in bytes.decode(read_order) or "done" in bytes.decode(read_order)):
                serial.write("M105\n".encode('ascii') )
                time.sleep(0.5)
                tem_message=serial.readline()  
                time.sleep(0.5)
                payload_json = {
                            'id': 1,
                            'statue': {
                                'chambertemperature':random.randint(1,20),
                                'bedtemperature': random.randint(1,20)

                            },
                            'on_off': 1,
                            'printing':printing,
                            'endprint':endprint,
                            'startprint':startprint
                            }
                sio.emit('state', payload_json)
                print(payload_json)
                print(">>>")
                break
    endprint = 0
    print("打印结束")
    os.remove("printfile")
    
@sio.on('connect')#连接成功触发汇报树莓派与打印机连接状态
def on_connect():
    global printing
    global endprint
    global startprint
    print('connection established')
    if serial.isOpen():  
        time.sleep(8)
        serial.readlines()
        serial.flushOutput()
        serial.write("M105\n".encode('ascii') )
        time.sleep(0.5)
        tem_message=serial.readline()  
        time.sleep(0.5)
        printmessage_json = {
                    'id': 1,
                    'on_off': 1,
                    'statue': {
                    'chambertemperature':random.randint(1,20),
                    'bedtemperature': random.randint(1,20)
                    },
                    'printing':printing,
                    'endprint':endprint,
                    'startprint':startprint
                    }
        sio.emit('state', printmessage_json)
        print("打印机上线")
        print(printmessage_json)
    else:
        printmessage_json = {
                    'id': 1,
                    'on_off': 0,
                    'statue': {
                    'chambertemperature':'',
                    'bedtemperature': '',
                    },
                    'printing':printing,
                    'endprint':endprint,
                    'startprint':startprint
                    }
        sio.emit('state', printmessage_json)
        print("打印机连接失败")
        print(printmessage_json)

@sio.on('file')#
def on_file(file):
    global printing
    global endprint
    global startprint
    print("接收到打印文件")
    sio.emit('file','getting' )
    fp = open("printfile.gcode",'w') 
    fp.writelines(file) 
    fp.close() 
    sio.emit('file','got' )
    filename = "printfile.gcode"
    gcodelist = read_gcode(filename)
    startprint = 1
    printing = 1
    receiving = 0
    serial.write("M105\n".encode('ascii') )
    time.sleep(0.5)
    tem_message=serial.readline()  
    time.sleep(0.5)
    payload_json = {
                    'id': 1,
                    'statue': {
                        'chambertemperature':random.randint(1,20),
                        'bedtemperature':random.randint(1,20)
                    },
                    'on_off': 1,
                    'printing':printing,
                    'endprint':endprint,
                    'startprint':startprint,
                    'receiving':receiving
                    }
    sio.emit('state', payload_json)
    startprint = 0
    print("开始打印")
    print(payload_json)
    print_model(gcodelist,serial,sio,printing,endprint,startprint)
    
   
@sio.on('state')
def on_state():
    global printing
    global endprint
    global startprint
    serial.write("M105\n".encode('ascii') )
    time.sleep(0.5)
    tem_message=serial.readline()  
    time.sleep(0.5)
    payload_json = {
                'id': 1,
                'statue': {
                        'chambertemperature':random.randint(1,20),
                        'bedtemperature': random.randint(1,20)
                },
                'on_off': 1,
                'printing':printing,
                'endprint':endprint,
                'startprint':startprint
                }            
    sio.emit('state', payload_json)
    print("打印机状态发送")
    
@sio.on('disconnect')#只要在disconnect下发送消息即刻断开连接
def on_disconnect():
    print('reconnecting')


sio.connect('http://120.79.148.35:7001')
sio.wait()