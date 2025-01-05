import uasyncio as asyncio
import aiorepl

from ichaynyk import iChaynyk
import wifi
from iot_controller import IOTController

def set_global_exception():
    def handle_exception(loop, context):
        import sys
        sys.print_exception(context["exception"])
        sys.exit()
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)

async def startIOT():
    await wifi.connectToWifi()
    #iot_controller = IOTController()
    #await iot_controller.mqtt_connect()

async def main():
    set_global_exception()  # Debug aid
    
    kettle = iChaynyk()
    mainApp = asyncio.create_task(kettle.run_forever())  # Non-terminating method
    # Start the aiorepl task.
    repl = asyncio.create_task(aiorepl.task())

    #Start 
    iot = asyncio.create_task(startIOT())

    await asyncio.gather(mainApp, repl)

try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()  # Clear retained state