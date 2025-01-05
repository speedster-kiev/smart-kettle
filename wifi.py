import network
import asyncio


async def connectToWifi():
    # Initialize the WLAN object
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # Replace with your Wi-Fi credentials
    ssid = "SlavaUkraine"
    password = "HeroyamSlava"

    try:
        # Attempt to connect
        print("Connecting to Wi-Fi...")
        wlan.connect(ssid, password)

        # Wait for connection
        for _ in range(10):  # Timeout after 10 iterations (~10 seconds)
            if wlan.isconnected():
                print("Wi-Fi connected!")
                print("IP Address:", wlan.ifconfig()[0])
                break
            await asyncio.sleep(1)
        else:
            raise RuntimeError("Wi-Fi connection timed out")

    except Exception as e:
        # Catch any exception and print an error message
        print("An error occurred:", str(e))
