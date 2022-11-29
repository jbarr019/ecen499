import RPi.GPIO as GPIO
import time

#Redundant setups in the event that they are not
#run when the GUI is enabled
pin_no = 4
ADC_CS = 8
ADC_SCK = 11
ADC_MOSI = 10
ADC_MISO = 9
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(ADC_CS, GPIO.OUT)
GPIO.setup(ADC_SCK, GPIO.OUT)
GPIO.setup(ADC_MOSI, GPIO.OUT)
GPIO.setup(ADC_MISO, GPIO.IN)

#Function that reads the data in the ADC from the
#given channel(0 or 1)
def read_adc(channel):
    if ((channel >= pin_no) or (channel < 0)):
        return -1
    adc = 0
    cmd = 0b11000000
        
    cmd = cmd | (channel << 3)
        
    GPIO.output(ADC_CS, GPIO.HIGH)
    GPIO.output(ADC_CS, GPIO.LOW)
    
    loop_cnt = 0
    for x in range(7, 2, -1):
        GPIO.output(ADC_MOSI, cmd & 1 << x)
        GPIO.output(ADC_SCK, GPIO.HIGH)
        GPIO.output(ADC_SCK, GPIO.LOW)
        
    GPIO.output(ADC_SCK, GPIO.HIGH)
    GPIO.output(ADC_SCK, GPIO.LOW)
    GPIO.output(ADC_SCK, GPIO.HIGH)
    GPIO.output(ADC_SCK, GPIO.LOW)
    
    for x in range(11,-1,-1):
        adc += GPIO.input(ADC_MISO) << x
        GPIO.output(ADC_SCK, GPIO.HIGH)
        GPIO.output(ADC_SCK, GPIO.LOW)

    GPIO.output(ADC_CS, GPIO.HIGH)
    
    #Returns an int number between 0-4095
    return adc