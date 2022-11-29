import gpiozero
import time

'''
Sine Wave Generator AD9833
This class accepts any GPIO pins for its MOSI, SCK, and CS pins
'''
class AD9833:
    #Initializes the pins and conditions of the generator
    def __init__(self, data, clk, fsync):
        self.dataPin = gpiozero.OutputDevice(pin = data)
        self.clkPin = gpiozero.OutputDevice(pin = clk)
        self.fsyncPin = gpiozero.OutputDevice(pin = fsync)
        
        self.fsyncPin.on()
        self.clkPin.on()
        self.dataPin.off()
        
        self.freq_ = 0
        
        self.clk_freq = 25.0e6
        
    #Function to change the frequency of the sine wave
    def set_freq(self, f):
        flag_b28 = 1 << 13
        flag_freq = 1 << 14
        
        scale = 1 << 28
        n_reg = int(f * scale / self.clk_freq)
        
        n_low = n_reg & 0x3fff
        n_hi = (n_reg >> 14) & 0x3fff
        
        self.send16(flag_b28)
        self.send16(flag_freq | n_low)
        self.send16(flag_freq | n_hi)
        self.freq_ = flag_freq
        
    #Function that sends data to the generator
    def send16(self, n):
        self.fsyncPin.off()
        
        mask = 1 << 15
        
        for i in range(0, 16):
            
            self.dataPin.value = bool(n & mask)
            self.clkPin.off()
            self.clkPin.on()
            
            mask = mask >> 1
        
        self.dataPin.off()
        self.fsyncPin.on()