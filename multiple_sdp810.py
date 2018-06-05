# To run multiple Sensirion SDP810 flow sensors on one raspberry pi.
# IMPORTANT: Add the following 2 lines to /boot/config.txt to generate aditional i2c busses 3 and 4
# dtoverlay=i2c-gpio,bus=3,i2c_gpio_delay_us=1
# dtoverlay=i2c-gpio,bus=4,i2c_gpio_delay_us=1,i2c_gpio_sda=17,i2c_gpio_scl=27
# Dev by JJ Slabbert

import smbus
import time

bus3=smbus.SMBus(3) #Aditional 12c bus, configured in config.txt
bus4=smbus.SMBus(4) #Aditional 12c bus, configured in config.txt
address=0x25
scale_factor=255/60 #255/60 for SDP810-500 PA and 255/240 for SDP810-125 PA

bus3.write_i2c_block_data(address, 0x3F, [0xF9]) #Stop any cont measurement of the sensor
bus4.write_i2c_block_data(address, 0x3F, [0xF9]) #Stop any cont measurement of the sensor
time.sleep(0.1)
bus3.write_i2c_block_data(address, 0x36, [0X03]) #Start Continuous Measurement 
bus4.write_i2c_block_data(address, 0x36, [0X03]) #Start Continuous Measurement
time.sleep(0.1)

while True:
    time.sleep(0.05)
    #Reading Sensor on i2c bus 3
    reading3=bus3.read_i2c_block_data(address,0,9)
    pressure_value3=reading3[0]+float(reading3[1])/255
    if pressure_value3>=0 and pressure_value3<128:
        diffirential_pressure3=pressure_value3*scale_factor#scale factor adjustment
    elif pressure_value3>128 and pressure_value3<=256:
        diffirential_pressure3=-(256-pressure_value3)*scale_factor #scale factor adjustment
    elif pressure_value3==128:
        diffirential_pressure3=99999999 #Out of range
    print("Diffirential Pressure 3: "+str(diffirential_pressure3)+" PA")


    #Reading Sensor on i2c bus 4
    reading4=bus4.read_i2c_block_data(address,0,9)
    pressure_value4=reading4[0]+float(reading4[1])/255
    if pressure_value4>=0 and pressure_value4<128:
        diffirential_pressure4=pressure_value4*scale_factor #scale factor adjustment
    elif pressure_value4>128 and pressure_value4<=256:
        diffirential_pressure4=-(256-pressure_value4)*scale_factor #scale factor adjustment
    elif pressure_value4==128:
        diffirential_pressure4=99999999 #Out of range
    print("Diffirential Pressure 4: "+str(diffirential_pressure4)+" PA"+"\n")
