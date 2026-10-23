# KDM GitHub release 17 / 1.0.10
# KDM GitHub release 8 / 1.0.8
from RotEncoder import ROTENC
from Potentiometer import POTENTIOMTER
OTA_APP_API = 1
from ota_boot import wdt, healthy_pass
from machine import I2C,Pin,Timer,PWM
import time
import Addresses
from lcdutil_optimized import LCDUTIL
from mcp import MCP
import settings
import ModbusRTU


# The stable supervisor owns the 8-second watchdog.


def feed_watchdog():
    if wdt is not None:
        wdt.feed()


# Normal-mode link supervision. No PLC CPU-state writes are performed.
PLC_RETRY_MS = 1000
PLC_HEARTBEAT_MS = 2000
PLC_last_attempt = None


def plc_exchange(desired):
    global Old_PLC_data, Modbus_err, PLC_last_attempt
    now = time.ticks_ms()
    dirty = desired != Old_PLC_data
    # A failed write/heartbeat must be retried even with unchanged setpoints.
    recovering = Modbus_err == 1002
    interval = PLC_RETRY_MS if recovering else PLC_HEARTBEAT_MS
    if PLC_last_attempt is not None:
        elapsed = time.ticks_diff(now, PLC_last_attempt)
        if elapsed < interval and (recovering or not dirty):
            return None
    PLC_last_attempt = now
    try:
        if dirty or recovering:
            acknowledged = host.write_multiple_registers(
                slave_addr=slave_addr_PLC,
                starting_address=0x1198,  # Existing D408/D409 destination.
                register_values=desired,
                signed=False,
            )
            if acknowledged is not True:
                raise OSError("PLC write not acknowledged")
            # Only a successful, validated response advances this cache.
            Old_PLC_data = list(desired)
        else:
            # Read-only heartbeat: no repeated writes just to check the link.
            values = host.read_holding_registers(
                slave_addr=slave_addr_PLC,
                starting_addr=0x1198,
                register_qty=2,
            )
            if (not isinstance(values, (list, tuple)) or len(values) != 2
                    or any(type(v) is not int or not 0 <= v <= 65535
                           for v in values)):
                raise ValueError("Unexpected PLC heartbeat response")
    except Exception as error:
        if Modbus_err != 1002:
            print("PLC communication lost:", repr(error))
        Modbus_err = 1002
        return False
    if Modbus_err == 1002:
        print("PLC communication restored: write acknowledged")
        Modbus_err = 0
    return True


def getPin(port,pin):
    return ((port >> pin) & 1)

def speed_update(data):
        pwm.duty_u16 (int(data["enc3"] *65535 * data["max_trech"]/10000))
        pwm2.duty_u16 (int(data["enc1"] * 65535 * data["max_speed"]/10000))
        pwm3.duty_u16 (int(data["enc1"] * 65535 * data["max_speed"]/10000))
# get data from settings
settings = settings.SETTINGS("settings.json")
data = settings.read()
#update pwm settings
led = Pin(25,Pin.OUT)
pwm = PWM ( Pin ( 8 ) ) # GP8
pwm2 = PWM ( Pin ( 7 ) ) # GP7
pwm3 = PWM ( Pin ( 6 ) ) # GP6
pwm.freq ( 1000 ) # 1kHz
pwm2.freq(1000) # 1kHz
pwm3.freq(1000) # 1kHz
# send saved values from memory to pwm pins
speed_update(data)


print ("Ok IO")
# initialize communication
i2c= I2C(0,sda=Pin(16), scl=Pin(17),freq=400000)
print (i2c.scan())
enc3 = ROTENC(i2c,0x0F,Addresses.Enc3,1)
enc2 = ROTENC(i2c,0x0F,Addresses.Enc2,1)
enc1 = ROTENC(i2c,0x0F,Addresses.Enc1,1)
mcp = MCP(i2c,0x20,Addresses.MCP,2)

print("Ok I2C")

lcd = LCDUTIL(
    i2c,
    lcd3 = Addresses.Lcd3,
    lcd2 = Addresses.Lcd2,
    lcd1 = Addresses.Lcd1,
    halt_on_error=False,
    )        
if lcd.failed:
    for name, error in lcd.failed:
        print(name, error)
        
enc3.maxval = 100
enc3.steps_per_rev = 100
enc3.counter = int(data["enc3"])
enc3.set_color("#FF0000")
# enc3.fixedcolor = False
enc3.step = 2
enc2.maxval = 30
enc2.steps_per_rev = 30
enc2.counter = int(data["enc2"])
enc2.set_color("#FFAA00")
enc1.maxval = 100
enc1.steps_per_rev = 100
enc1.counter = int(data["enc1"])
enc1.set_color("#00FFAA")
enc1.step = 2
oldstr1 = oldstr2 = oldstr3 = ""

# ModeBus Section
# WRITE COILS
new_coil_val = 0
coil_address = 1
err_counter = 0
startreg = 0
slave_addr_INV = 1
slave_addr_PLC = 2
host = ModbusRTU.init_ModBus()
Modbus_err = 0
Old_PLC_data = None
# Read Stop signal at start up 
port = mcp.readporta() # read port from PCB2
dCounter = 5000 #dummy value
if not(getPin(port,7)): # pin 7 is the Stop button
    enc3 = None
    enc2 = None
    enc1 = None
    enc3_service = ROTENC(i2c,0x0F,Addresses.Enc3,1)
    enc2_service = ROTENC(i2c,0x0F,Addresses.Enc2,1)
    enc1_service = ROTENC(i2c,0x0F,Addresses.Enc1,1)
    enc3_service.maxval = 100
    enc3_service.steps_per_rev = 100
    enc3_service.counter = int(data["max_trech"])
    enc3_service.set_color("#FF00FF")
    # enc3.fixedcolor = False
    enc3_service.step = 1
#     enc2_service.maxval = 30
#     enc2_service.steps_per_rev = 30
#     enc2_service.counter = int(data["enc2"])
    enc2_service.set_color("#FFFFFF")
    enc1_service.maxval = 100
    enc1_service.steps_per_rev = 100
    enc1_service.counter = int(data["max_speed"])
    enc1_service.set_color("#00FF00")
    enc1_service.step = 1
    old_val1 = enc1_service.counter
    old_val3 = enc3_service.counter
    while True :
        val1_s = enc1_service.counter
        val3_s = enc3_service.counter
#         str1_S = "{}".format(int(val1)) 
#         str3_S = "{}".format(int(val3))
        lcd.show_items(
            "lcd3",
            ([
                ("Deeg teller",0,0,24),
                (str(dCounter),0,33,24),
            ] if dCounter is not None else [
                ("PLC",40,0,24),
                ("Communication",10,30,16),
            ]))
        lcd.show_items(
            "lcd2",
            [
                ("KALMEIJER",0,8,24),
                ("Rev: {}".format(data["Ver"]),0,33,16),
                ])
        lcd.show_items(
            "lcd1",
            [
                ("Band    Trech.",0,0,16),
                ("{}      {}".format(val1_s,val3_s),0,20,16),
                
                ])
        # Save only when the encoder values change
        if val1_s != old_val1 or val3_s != old_val3:

            data["max_speed"] = val1_s
            data["max_trech"] = val3_s

            settings.data = data
            settings.update = True

            old_val1 = val1_s
            old_val3 = val3_s

            print("Settings changed:", val1_s, val3_s)

        # Check save timer on every loop
        settings.update_calc()

            
        try:
            registers = host.read_holding_registers(
                slave_addr=slave_addr_PLC,
                starting_addr=0x0EE0,  # C224
                register_qty=2
            )

            # Delta 32-bit counter: low word first
            low_word = registers[1]
            high_word = registers[0]

            # Combine into 32-bit value
            dCounter = (high_word << 16) | low_word

            # Convert to signed 32-bit integer
#             if dCounter >= 0x80000000:
#                 dCounter -= 0x100000000

            print("PLC Counter C224:", dCounter)

        except Exception as e:
            dCounter = None
            print("Error com PLC {}".format(e))

        # Completed service pass, including the existing handled PLC error path.
        feed_watchdog()
        if dCounter is not None and not lcd.failed:
            healthy_pass()

while True:
    if Modbus_err == 0:
#         start = time.ticks_us()
        # read inputs
        val3 = enc1.counter
        val2 = enc2.counter
        val1 = enc3.counter
#         str1 = "{}".format(val3) 
        str2 = "{:.1f}".format(val2/10 )
        str3 = "{}".format(int(val1 ))
        port = mcp.readporta()
        
        # display outputs
        

        if lcd.show_items(
                "lcd3",
                [
                    (str(val3), 8, 8, 48),
                    ("%", 90, 8, 48),
                ],
            ):
            data["enc1"] = val3
            settings.update = True

        
        if not getPin(port,4):
            if lcd.show_items(
                "lcd2",
                [
                    (str2,0,8,48),
                    ("sec",80,16,32)
                    ],
                ):
                data["enc2"] = val2
                settings.update = True

        else:
            lcd.show_items(
                "lcd2",
                [("Geen", 24,0,32),
                 ("Decoratie",0,24,32)])


        if getPin(port,5):
            if lcd.show_items(
                "lcd1",
                [(str3,8,8,48),
                 ("%",90,8,48)],):
                data["enc3"] = val1
                settings.update = True
        else:
            lcd.show_items(
                "lcd1",
                [("Max", 32,0,32),
                 ("snelheid",0,24,32)],
                )

            
        settings.data = data
        settings.update_calc()

        #send outputs 
        led.value(not getPin(port,7))
#         pwm.duty_u16 (int(val1 *65535 * data["max_trech"]/10000))
#         pwm2.duty_u16 (int(val3 *65535 * data["max_speed"]/10000))
#         pwm3.duty_u16 (int(val3 *65535 * data["max_speed"]/10000))
        speed_update(data)
#         print(pwm.duty_u16(),pwm3.duty_u16() )
        
#         print(getPin(port,7),getPin(port,6),getPin(port,5),getPin(port,4),getPin(port,3),getPin(port,2),getPin(port,1),getPin(port,0))
#         print(time.ticks_diff(time.ticks_us(),start))
    else:
        #        we have a problemm in connecting to modbus display error message

        lcd.show_items("lcd1",[("",0,0,24),("",8,24,24)])
#         time.sleep_ms(5)
        lcd.show_items("lcd2",[("",0,0,24)])
#         time.sleep_ms(5)        
        error_msg= ""
        if Modbus_err == 1001:
            error_msg = "INV"
        if Modbus_err == 1002:
            error_msg = "PLC"

        lcd.show_items("lcd3",[(error_msg, 40,0,24),("Communication", 10, 30,16 )])
        time.sleep_ms(5)
#         blinking potentiometer
#         pot3.led([r,g,b])
#         pot2.led([r,g,b])
#         pot1.led([r,g,b])
        # Keep the error latched until plc_exchange gets a valid response.

            
#     try:        
#         multi_reg = [int(val3*50)]
# 
#         host.write_multiple_registers(
#         slave_addr=slave_addr_INV,
#         starting_address=int("2001",16),
#         register_values=multi_reg,
#         signed=False)
# 
#     except Exception as e: 
#         print("Error com Inverter {}".format(e)) 
#         Modbus_err= 1001
# 
    multi_reg_PLC = [int(data["Off_Delay"]), int(val2 * 10)]
    plc_exchange(multi_reg_PLC)

    # Feed only after completing the pass, never from a timer/interrupt.
    # Handled Modbus errors retain the existing retry behavior.
    feed_watchdog()
    if Modbus_err == 0 and not lcd.failed:
        healthy_pass()
