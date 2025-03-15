#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Simple Offline SMS Sender via GSM Module
-------------------------------------------
Yeh script GSM module (SIM800L/SIM900A) ka use karke bina internet ke SMS bhejne ke liye hai.
Ensure karein:
- GSM module sahi tarike se connect ho (default serial port: /dev/ttyUSB0).
- GSM module ko proper power supply aur active SIM card available ho.
- pyserial module installed ho (pip install pyserial)
"""

import serial, time

def send_sms_via_gsm(phone, message, port='/dev/ttyUSB0', baudrate=115200, timeout=5):
    try:
        # Serial connection open karein
        ser = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(1)
        
        # Basic AT command check
        ser.write(b'AT\r')
        time.sleep(1)
        response = ser.read_all().decode()
        if "OK" not in response:
            print("GSM module se connection establish nahi ho raha hai.")
            ser.close()
            return

        # SMS text mode set karein
        ser.write(b'AT+CMGF=1\r')
        time.sleep(1)
        
        # SMS bhejne ka command
        cmd = f'AT+CMGS="{phone}"\r'
        ser.write(cmd.encode())
        time.sleep(1)
        
        # Message bhejein
        ser.write(message.encode() + b"\r")
        time.sleep(1)
        
        # CTRL+Z send karein taaki SMS send ho jaye
        ser.write(bytes([26]))
        time.sleep(3)
        
        # Response check karein
        response = ser.read_all().decode()
        ser.close()
        if "OK" in response:
            print("SMS successfully bhej diya gaya hai!")
        else:
            print("SMS bhejne mein dikkat aayi. Response:", response)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    phone = input("Recipient ka phone number (country code ke sath, jaise +919876543210): ").strip()
    message = input("SMS message likhe: ").strip()
    send_sms_via_gsm(phone, message)
