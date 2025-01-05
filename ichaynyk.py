from machine import Pin, ADC
from math import log
import uasyncio as asyncio
from primitives import EButton #events.py
from rgbled import RGBLed

# Steinhart-Hart coefficients for the thermistor
A = 2.180830570e-03  # Example value
B = 0.2206823156e-04  # Example value
C = 7.386689980e-07  # Example value

ADC_MAX = 1023       # Maximum ADC value (10-bit resolution)
V_REF = 3.3          # Reference voltage for ADC
R2 = 10000.0         # Known resistor in the voltage divider (10kΩ)

HEATER_PIN = 5       # Pin to control rele of the heating element
LED_PIN = 2          # Pin to control LED
START_BTN_PIN = 4     # Pin for start boil button
MODE_BTN_PIN = 0
#LED
LED_RED = 14
LED_GREEN = 12
LED_BLUE = 13


class iChaynyk():
    
    heater_pin = Pin(HEATER_PIN, Pin.OUT, value = 1)
    led_pin = Pin(LED_PIN, Pin.OUT, value = 1)
    onOffBtn = EButton(Pin(START_BTN_PIN, Pin.IN, Pin.PULL_UP))
    modeBtn = EButton(Pin(MODE_BTN_PIN, Pin.IN, Pin.PULL_UP))
    
    heatingCoro = None
    modeSelectionTimeoutCoro = None
    
    modes = [
        (100, (255,0,0)), #red
        (50, (0,0,255)), #blue
        (60, (0,255,0)), #green
        (70, (0,255,255)), #cyan
        (80, (255,255,0)), #yello
        (90, (255,80,0)), #orange
    ]
    currentMode = 0
    defaultMode = 0
    # Initialize ADC
    adc = ADC(0)
    #LED
    led = RGBLed(LED_RED,LED_GREEN,LED_BLUE,RGBLed.anode)

    def __init__(self) -> None:
        asyncio.create_task(self.initOnOffBtn()) # init on/off buttom
        asyncio.create_task(self.initModeBtn()) # init mode buttom        

    def startHeating(self, target_temp = 100):
        print("Starting heating...")
        self.heater_pin.value(0)
        self.led_pin.value(0)

    def stopHeating(self):
        print("Stopping heating...")
        self.heater_pin.value(1)
        self.led_pin.value(1)

    def isHeating(self):
        return self.heater_pin.value() == 0
    
    async def getCurrentTemp(self):
        adc_value = await asyncio.create_task(self.read_adc_average(samples=5, delay_ms=100))        # Average 10 ADC readings
        Vout = adc_value * (V_REF / ADC_MAX)            # Convert ADC value to voltage
        R1 = R2 * (V_REF / Vout - 1)                    # Calculate thermistor resistance

        # Steinhart-Hart equation to calculate temperature in Kelvin
        logR = log(R1)
        tempK = 1.0 / (A + B * logR + C * logR**3)      # Temperature in Kelvin
        tempC = tempK - 273.15                          # Convert to Celsius

        # Print results
        print("ADC Value: {}, Resistance: {:.2f} Ohms, Temperature: {:.2f} °C".format(adc_value, R1, tempC))
        return tempC

    async def read_adc_average(self, samples=10, delay_ms=10):
        """Read and average multiple ADC samples."""
        total = 0
        for _ in range(samples):
            total += self.adc.read()
            asyncio.sleep_ms(delay_ms)
        return total // samples  # Return average

    async def initOnOffBtn(self):
        while True:
            self.onOffBtn.press.clear()
            print("waiting 4 on/off")
            await self.onOffBtn.press.wait()
            print("on/off pressed")
            await self.handle_onoff_btn()

    async def initModeBtn(self):
        while True:
            self.modeBtn.press.clear()
            print("waiting 4 mode")
            await self.modeBtn.press.wait()
            print("mode pressed")
            await self.handle_mode_btn()

    async def handle_mode_btn(self):
        if self.isHeating():
            return
        else: 
            if self.currentMode == len(self.modes) - 1:
                self.currentMode = 0
            else:
                self.currentMode = self.currentMode + 1
            
            async def resetMode():
                await asyncio.sleep(5)
                if self.isHeating():
                    return
                self.currentMode = 0
                self.led.off()

            if self.modeSelectionTimeoutCoro is not None:
                self.modeSelectionTimeoutCoro.cancel()
            self.modeSelectionTimeoutCoro = asyncio.create_task(resetMode())

        self.lightLED()    
        

    def lightLED(self):
        mode = self.modes[self.currentMode]
        self.led.setColor(*mode[1])

    async def handle_onoff_btn(self):
        #Start/stop Heating
        if self.isHeating():
            self.heatingCoro.cancel()
            self.currentMode = self.defaultMode
        else:
            mode = self.modes[self.currentMode]
            self.lightLED()
            self.heatingCoro = asyncio.create_task(self.heatTo(mode[0]))
         
    async def run_forever(self):
        while True:
            await asyncio.sleep(1)

    async def heatTo(self, temp=100):
        print("Heating to: {:.2f} °C".format(temp))
        self.startHeating()
        try:
            await self.reachTemp(temp)
        finally:
            print("finally")
            self.stopHeating()
            self.led.off()

    async def reachTemp(self, target_temp):
        temp = await asyncio.create_task(self.getCurrentTemp())
        while  temp <= target_temp:
            await asyncio.sleep(2)
            temp = await asyncio.create_task(self.getCurrentTemp())