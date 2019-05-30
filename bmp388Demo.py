#This code uses GPIO 17 and 27 As SDA and SCL for i2c bus 3
#add this line to config.txt
#dtoverlay=i2c-gpio,bus=3,i2c_gpio_delay_us=1,i2c_gpio_sda=17,i2c_gpio_scl=27
#Restart your raspberry pi
#Connect your adafruit BMP388 sensors to i2c bus 1 and 3
import time
import smbus
import math

# define BMP388 Device I2C address
I2C_ADD_BMP388_AD0_LOW	=	0x76
I2C_ADD_BMP388_AD0_HIGH	=   0x77
I2C_ADD_BMP388    =		I2C_ADD_BMP388_AD0_LOW

BMP388_REG_ADD_WIA	=	0x00
BMP388_REG_VAL_WIA		=	0x50

BMP388_REG_ADD_ERR	=	0x02
BMP388_REG_VAL_FATAL_ERR	=	0x01
BMP388_REG_VAL_CMD_ERR		=	0x02
BMP388_REG_VAL_CONF_ERR		=	0x04

BMP388_REG_ADD_STATUS	=	0x03
BMP388_REG_VAL_CMD_RDY		=	0x10
BMP388_REG_VAL_DRDY_PRESS	=	0x20
BMP388_REG_VAL_DRDY_TEMP	=	0x40

BMP388_REG_ADD_CMD	=	0x7E
BMP388_REG_VAL_EXTMODE_EN	=	0x34
BMP388_REG_VAL_FIFI_FLUSH	=	0xB0
BMP388_REG_VAL_SOFT_RESET	=	0xB6

BMP388_REG_ADD_PWR_CTRL	=	0x1B
BMP388_REG_VAL_PRESS_EN		=	0x01
BMP388_REG_VAL_TEMP_EN		=	0x02
BMP388_REG_VAL_NORMAL_MODE	=	0x30

BMP388_REG_ADD_PRESS_XLSB	=	0x04
BMP388_REG_ADD_PRESS_LSB	=	0x05
BMP388_REG_ADD_PRESS_MSB	=	0x06
BMP388_REG_ADD_TEMP_XLSB	=	0x07
BMP388_REG_ADD_TEMP_LSB		=	0x08
BMP388_REG_ADD_TEMP_MSB		=	0x09

BMP388_REG_ADD_T1_LSB	=	0x31
BMP388_REG_ADD_T1_MSB	=	0x32
BMP388_REG_ADD_T2_LSB	=	0x33
BMP388_REG_ADD_T2_MSB	=	0x34
BMP388_REG_ADD_T3		=	0x35
BMP388_REG_ADD_P1_LSB	=	0x36
BMP388_REG_ADD_P1_MSB	=	0x37
BMP388_REG_ADD_P2_LSB	=	0x38
BMP388_REG_ADD_P2_MSB	=	0x39
BMP388_REG_ADD_P3		=	0x3A
BMP388_REG_ADD_P4		=	0x3B
BMP388_REG_ADD_P5_LSB	=	0x3C
BMP388_REG_ADD_P5_MSB	=	0x3D
BMP388_REG_ADD_P6_LSB	=	0x3E
BMP388_REG_ADD_P6_MSB	=	0x3F
BMP388_REG_ADD_P7		=	0x40
BMP388_REG_ADD_P8		=	0x41
BMP388_REG_ADD_P9_LSB	=	0x42
BMP388_REG_ADD_P9_MSB	=	0x43
BMP388_REG_ADD_P10		=	0x44
BMP388_REG_ADD_P11		=	0x45

class BMP388_rain(object):
	"""docstring for BMP388"""
	def __init__(self, address=I2C_ADD_BMP388):
		self._address = address
		self._bus = smbus.SMBus(1)
		# Load calibration values.
		if self._read_byte(BMP388_REG_ADD_WIA) == BMP388_REG_VAL_WIA:
			print("Pressure sersor is BMP388!\r\n")	
			u8RegData = self._read_byte(BMP388_REG_ADD_STATUS)
			if ( u8RegData & BMP388_REG_VAL_CMD_RDY ):
				self._write_byte(BMP388_REG_ADD_CMD, BMP388_REG_VAL_SOFT_RESET) 
				time.sleep(0.01)
		else:
			print("Pressure sersor NULL!\r\n")
		self._write_byte( BMP388_REG_ADD_PWR_CTRL,BMP388_REG_VAL_PRESS_EN | BMP388_REG_VAL_TEMP_EN | BMP388_REG_VAL_NORMAL_MODE)
		self._load_calibration()

	def _read_byte(self,cmd):
		return self._bus.read_byte_data(self._address,cmd)

	def _read_s8(self,cmd):
		result = self._read_byte(cmd)
		if result > 128:result -= 256
		return result	

	def _read_u16(self,cmd):
		LSB = self._bus.read_byte_data(self._address,cmd)
		MSB = self._bus.read_byte_data(self._address,cmd+1)
		return (MSB	<< 8) + LSB

	def _read_s16(self,cmd):
		result = self._read_u16(cmd)
		if result > 32767:result -= 65536
		return result

	def _write_byte(self,cmd,val):
		self._bus.write_byte_data(self._address,cmd,val)

	def _load_calibration(self):
		print("_load_calibration\r\n")
		"load calibration"
		""" read the temperature calibration parameters """
		self.T1 =self._read_u16(BMP388_REG_ADD_T1_LSB)
		self.T2 =self._read_u16(BMP388_REG_ADD_T2_LSB)
		self.T3 =self._read_s8(BMP388_REG_ADD_T3)
		""" read the pressure calibration parameters """
		self.P1 =self._read_s16(BMP388_REG_ADD_P1_LSB)
		self.P2 =self._read_s16(BMP388_REG_ADD_P2_LSB)
		self.P3 =self._read_s8(BMP388_REG_ADD_P3)
		self.P4 =self._read_s8(BMP388_REG_ADD_P4)
		self.P5 =self._read_u16(BMP388_REG_ADD_P5_LSB)
		self.P6 =self._read_u16(BMP388_REG_ADD_P6_LSB)
		self.P7 =self._read_s8(BMP388_REG_ADD_P7)
		self.P8 =self._read_s8(BMP388_REG_ADD_P8)
		self.P9 =self._read_s16(BMP388_REG_ADD_P9_LSB)	
		self.P10 =self._read_s8(BMP388_REG_ADD_P10)
		self.P11=self._read_s8(BMP388_REG_ADD_P11)
		#print(self.T1)
		#print(self.T2)
		#print(self.T3)
		#print(self.P1)
		#print(self.P2)
		#print(self.P3)
		#print(self.P4)
		#print(self.P5)
		#print(self.P6)
		#print(self.P7)
		#print(self.P8)
		#print(self.P9)
		#print(self.P10)
		#print(self.P11)
	def compensate_temperature(self,adc_T):
		partial_data1 =  (adc_T - (256 *  (self.T1)))
		partial_data2 =  (self.T2 * partial_data1)
		partial_data3 =  (partial_data1 * partial_data1)
		partial_data4 =  (( partial_data3) * ( self.T3))
		partial_data5 = ( (( partial_data2) * 262144) +  partial_data4)
		partial_data6 =  (( partial_data5) / 4294967296)
		self.T_fine = partial_data6
		comp_temp =  ((partial_data6 * 25)  / 16384)
		return comp_temp;   
			
	def compensate_pressure(self,adc_P):
		partial_data1 = self.T_fine * self.T_fine
		partial_data2 = partial_data1 / 64
		partial_data3 = (partial_data2 * self.T_fine) / 256
		partial_data4 = (self.P8 * partial_data3) / 32
		partial_data5 = (self.P7 * partial_data1) * 16
		partial_data6 = (self.P6 * self.T_fine) * 4194304;
		offset =  ( (self.P5) *  140737488355328) + partial_data4 + partial_data5 + partial_data6

		partial_data2 = (( self.P4) * partial_data3) / 32
		partial_data4 = (self.P3 * partial_data1) * 4
		partial_data5 = ( (self.P2) - 16384) * ( self.T_fine) * 2097152
		sensitivity = (( (self.P1) - 16384) *  70368744177664) + partial_data2 + partial_data4 + partial_data5

		partial_data1 = (sensitivity / 16777216) * adc_P
		partial_data2 =  (self.P10) *  (self.T_fine)
		partial_data3 = partial_data2 + (65536 *  (self.P9))
		partial_data4 = (partial_data3 * adc_P) / 8192
		partial_data5 = (partial_data4 * adc_P) / 512
		partial_data6 =  ( adc_P *  adc_P)
		partial_data2 = ( (self.P11) *  (partial_data6)) / 65536
		partial_data3 = (partial_data2 * adc_P) / 128
		partial_data4 = (offset / 4) + partial_data1 + partial_data5 + partial_data3
		comp_press = (( partial_data4 * 25) /  1099511627776)
		return comp_press;

	def get_temperature_and_pressure_and_altitude(self):
		"""Returns pressure in Pa as double. Output value of "6386.2"equals 96386.2 Pa = 963.862 hPa."""
		xlsb = self._read_byte(BMP388_REG_ADD_TEMP_XLSB)
		lsb =  self._read_byte(BMP388_REG_ADD_TEMP_LSB)
		msb =  self._read_byte(BMP388_REG_ADD_TEMP_MSB)
		adc_T = (msb << 16) + (lsb << 8) + (xlsb)
		temperature = self.compensate_temperature(adc_T)
		xlsb = self._read_byte(BMP388_REG_ADD_PRESS_XLSB)
		lsb =  self._read_byte(BMP388_REG_ADD_PRESS_LSB) 
		msb =  self._read_byte(BMP388_REG_ADD_PRESS_MSB) 

		adc_P = (msb << 16) + (lsb << 8) + (xlsb)
		pressure = self.compensate_pressure(adc_P)
		altitude  = 4433000 * (1 - pow(((pressure/100.0) / 101325.0), 0.1903)) 

		return temperature,pressure,altitude


class BMP388_ambient(object):
	"""docstring for BMP388"""
	def __init__(self, address=I2C_ADD_BMP388):
		self._address = address
		self._bus = smbus.SMBus(3)
		# Load calibration values.
		if self._read_byte(BMP388_REG_ADD_WIA) == BMP388_REG_VAL_WIA:
			print("Pressure sersor is BMP388!\r\n")	
			u8RegData = self._read_byte(BMP388_REG_ADD_STATUS)
			if ( u8RegData & BMP388_REG_VAL_CMD_RDY ):
				self._write_byte(BMP388_REG_ADD_CMD, BMP388_REG_VAL_SOFT_RESET) 
				time.sleep(0.01)
		else:
			print("Pressure sersor NULL!\r\n")
		self._write_byte( BMP388_REG_ADD_PWR_CTRL,BMP388_REG_VAL_PRESS_EN | BMP388_REG_VAL_TEMP_EN | BMP388_REG_VAL_NORMAL_MODE)
		self._load_calibration()

	def _read_byte(self,cmd):
		return self._bus.read_byte_data(self._address,cmd)

	def _read_s8(self,cmd):
		result = self._read_byte(cmd)
		if result > 128:result -= 256
		return result	

	def _read_u16(self,cmd):
		LSB = self._bus.read_byte_data(self._address,cmd)
		MSB = self._bus.read_byte_data(self._address,cmd+1)
		return (MSB	<< 8) + LSB

	def _read_s16(self,cmd):
		result = self._read_u16(cmd)
		if result > 32767:result -= 65536
		return result

	def _write_byte(self,cmd,val):
		self._bus.write_byte_data(self._address,cmd,val)

	def _load_calibration(self):
		print("_load_calibration\r\n")
		"load calibration"
		""" read the temperature calibration parameters """
		self.T1 =self._read_u16(BMP388_REG_ADD_T1_LSB)
		self.T2 =self._read_u16(BMP388_REG_ADD_T2_LSB)
		self.T3 =self._read_s8(BMP388_REG_ADD_T3)
		""" read the pressure calibration parameters """
		self.P1 =self._read_s16(BMP388_REG_ADD_P1_LSB)
		self.P2 =self._read_s16(BMP388_REG_ADD_P2_LSB)
		self.P3 =self._read_s8(BMP388_REG_ADD_P3)
		self.P4 =self._read_s8(BMP388_REG_ADD_P4)
		self.P5 =self._read_u16(BMP388_REG_ADD_P5_LSB)
		self.P6 =self._read_u16(BMP388_REG_ADD_P6_LSB)
		self.P7 =self._read_s8(BMP388_REG_ADD_P7)
		self.P8 =self._read_s8(BMP388_REG_ADD_P8)
		self.P9 =self._read_s16(BMP388_REG_ADD_P9_LSB)	
		self.P10 =self._read_s8(BMP388_REG_ADD_P10)
		self.P11=self._read_s8(BMP388_REG_ADD_P11)
		#print(self.T1)
		#print(self.T2)
		#print(self.T3)
		#print(self.P1)
		#print(self.P2)
		#print(self.P3)
		#print(self.P4)
		#print(self.P5)
		#print(self.P6)
		#print(self.P7)
		#print(self.P8)
		#print(self.P9)
		#print(self.P10)
		#print(self.P11)
	def compensate_temperature(self,adc_T):
		partial_data1 =  (adc_T - (256 *  (self.T1)))
		partial_data2 =  (self.T2 * partial_data1)
		partial_data3 =  (partial_data1 * partial_data1)
		partial_data4 =  (( partial_data3) * ( self.T3))
		partial_data5 = ( (( partial_data2) * 262144) +  partial_data4)
		partial_data6 =  (( partial_data5) / 4294967296)
		self.T_fine = partial_data6
		comp_temp =  ((partial_data6 * 25)  / 16384)
		return comp_temp;   
			
	def compensate_pressure(self,adc_P):
		partial_data1 = self.T_fine * self.T_fine
		partial_data2 = partial_data1 / 64
		partial_data3 = (partial_data2 * self.T_fine) / 256
		partial_data4 = (self.P8 * partial_data3) / 32
		partial_data5 = (self.P7 * partial_data1) * 16
		partial_data6 = (self.P6 * self.T_fine) * 4194304;
		offset =  ( (self.P5) *  140737488355328) + partial_data4 + partial_data5 + partial_data6

		partial_data2 = (( self.P4) * partial_data3) / 32
		partial_data4 = (self.P3 * partial_data1) * 4
		partial_data5 = ( (self.P2) - 16384) * ( self.T_fine) * 2097152
		sensitivity = (( (self.P1) - 16384) *  70368744177664) + partial_data2 + partial_data4 + partial_data5

		partial_data1 = (sensitivity / 16777216) * adc_P
		partial_data2 =  (self.P10) *  (self.T_fine)
		partial_data3 = partial_data2 + (65536 *  (self.P9))
		partial_data4 = (partial_data3 * adc_P) / 8192
		partial_data5 = (partial_data4 * adc_P) / 512
		partial_data6 =  ( adc_P *  adc_P)
		partial_data2 = ( (self.P11) *  (partial_data6)) / 65536
		partial_data3 = (partial_data2 * adc_P) / 128
		partial_data4 = (offset / 4) + partial_data1 + partial_data5 + partial_data3
		comp_press = (( partial_data4 * 25) /  1099511627776)
		return comp_press;

	def get_temperature_and_pressure_and_altitude(self):
		"""Returns pressure in Pa as double. Output value of "6386.2"equals 96386.2 Pa = 963.862 hPa."""
		xlsb = self._read_byte(BMP388_REG_ADD_TEMP_XLSB)
		lsb =  self._read_byte(BMP388_REG_ADD_TEMP_LSB)
		msb =  self._read_byte(BMP388_REG_ADD_TEMP_MSB)
		adc_T = (msb << 16) + (lsb << 8) + (xlsb)
		temperature = self.compensate_temperature(adc_T)
		xlsb = self._read_byte(BMP388_REG_ADD_PRESS_XLSB)
		lsb =  self._read_byte(BMP388_REG_ADD_PRESS_LSB) 
		msb =  self._read_byte(BMP388_REG_ADD_PRESS_MSB) 

		adc_P = (msb << 16) + (lsb << 8) + (xlsb)
		pressure = self.compensate_pressure(adc_P)
		altitude  = 4433000 * (1 - pow(((pressure/100.0) / 101325.0), 0.1903)) 

		return temperature,pressure,altitude

if __name__ == '__main__':

	import time
	
	print("BMP388 Test Program ...\n")
	
	bmp388rain = BMP388_rain()
	bmp388ambient=BMP388_ambient()
	arainpressure=0
	aambientpressure=0
	while True:
		time.sleep(0.5)
		temperature, rainpressure, altitude = bmp388rain.get_temperature_and_pressure_and_altitude()
		if arainpressure==0:
			arainpressure=rainpressure
		else:
			arainpressure=(arainpressure*9/10)+(rainpressure*1/10)
		


		temperature, ambientpressure, altitude = bmp388ambient.get_temperature_and_pressure_and_altitude()
		if aambientpressure==0:
			aambientpressure=ambientpressure
		else:
			aambientpressure=(aambientpressure*9/10)+(ambientpressure*1/10)
			
		print arainpressure, aambientpressure, float(arainpressure-aambientpressure)
