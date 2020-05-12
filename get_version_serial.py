#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" get_version_serial.py: Use pexpect to connect to IOS devices via terminal server.
                           Get Version info and save it to versions.out csv file.
                           Prompts for input csv file, format: Hostname,IP,Port.
                           Use of functions for learning basic python.
    Version: 1.0
"""


import pexpect
import csv

#---- Get device csv file from user and read it into a list of dictionaries
def get_devices():

    device_dict = {}
    device_list = []
    filename = input('Please, type in the device csv filename: ')   
    
    try:
         file = open(filename, 'r')
    except IOError:
          print('There was an error reading the file, is it there?')
          exit()

    for line in file:
        device = line.strip().split(',')
        device_dict.update({'Host' : device[0], 'IP' : device[1], 'Port' : device[2]})
        device_list.append(dict(device_dict))
    file.close()
    
    return device_list
#----------------


#---- Print device list of dictionaries 
def print_devs(devs):
  
    print('############## Devices Dictionary is : ##############')
    for dev in devs:
        print(dev)
    
    print('#####################################################')
    return 0
#----------------

#---- Connect to a device via terminal server - send extra return
def connect(device):

    print('Establishing connection to ' + device['Host'] + ' using ' + device['IP'] + ':' + device['Port'])
    session = pexpect.spawnu('telnet ' + device['IP'] + ' ' + device['Port'], timeout=20)
    session.sendline('\r')
    session.expect([r'\S+#$', r'\S+# $', r'\S+> ', r'\S+>$', pexpect.TIMEOUT, pexpect.EOF])

    return session
#----------------

#---- Extract version number from show ver command - works for IOS
def get_version(session):

    session.sendline('show version | i Version')
# It seems for VIOS (L2/L3) the buffer is empty with just one command
# needs investigation - workaround to execute it twice
    session.sendline('show version | i Version')
    session.expect([r'\S+#$', r'\S+# $', r'\S+> ', r'\S+>$', pexpect.TIMEOUT, pexpect.EOF])
    result = session.before
    version = result.split(',')[2].strip().replace('Version ', '')
  
    return version
#----------------

#---- Dump device list into a csv file
def save_file(devs):

    try:
        with open('versions.out', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=devs[0].keys())
            for data in devs:
                writer.writerow(data)
            csvfile.close()
    except IOError:
     print("Out file I/O Error")
     return False
    return True
#----------------


# Main Program
# ---------------
devices = get_devices()
print_devs(devices)

for device in devices:
    session = connect(device)
    version = get_version(session)
    session.close()
    device.update(dict(Version=version))

print_devs(devices)
if save_file(devices):
    print('Devices written to versions.out file')
else:
    print('There was an error writing versions.out file')

# ---------------
# End Main
