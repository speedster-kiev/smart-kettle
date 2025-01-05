import uasyncio as asyncio
from umqtt.robust import MQTTClient


class IOTController:
    
    # AWS IoT Core details
    AWS_ENDPOINT = "aang9bs8ofn7g-ats.iot.us-east-1.amazonaws.com"  # Replace with your AWS IoT endpoint
    CLIENT_ID = "KettleController"
    TOPIC_START = "kettle/start"
    TOPIC_STOP = "kettle/stop"
    TOPIC_TEMP = "kettle/temperature"

    # Certificate file paths
    CERT_FILE = "6ed5633c15881ce7707c3ce23dcf67e53eafee1cf7c08470bb363b7928507acf-certificate.pem.crt"   # Device certificate
    KEY_FILE = "6ed5633c15881ce7707c3ce23dcf67e53eafee1cf7c08470bb363b7928507acf-private.pem.key" # Private key
    CA_FILE = "AmazonRootCA1.pem"  # Root CA file

    # Kettle control logic
    def start_kettle(self):
        print("Kettle started!")
        # Add GPIO code to start the kettle.

    def stop_kettle(self):
        print("Kettle stopped!")
        # Add GPIO code to stop the kettle.

    def heat_kettle_to(self, temp):
        print(f"Heating kettle to {temp}°C")
        # Add GPIO code to set the kettle's temperature.

    # Handle incoming MQTT messages
    def handle_message(self, topic, msg):
        print(f"Received message on {topic}: {msg}")
        if topic == self.TOPIC_START.encode():
            self.start_kettle()
        elif topic == self.TOPIC_STOP.encode():
            self.stop_kettle()
        elif topic == self.TOPIC_TEMP.encode():
            try:
                temperature = int(msg)
                self.heat_kettle_to(temperature)
            except ValueError:
                print("Invalid temperature value")

    # MQTT connection setup
    async def mqtt_connect(self):
        try:
            # Load certificates
            with open(self.CERT_FILE, "r") as f:
                cert = f.read()
            with open(self.KEY_FILE, "r") as f:
                key = f.read()
            with open(self.CA_FILE, "r") as f:
                ca = f.read()

            # Create MQTT client
            client = MQTTClient(
                client_id=self.CLIENT_ID,
                server=self.AWS_ENDPOINT,
                port=8883,
                ssl=True,
                ssl_params={"cert": cert, "key": key, "ca_certs": ca}
            )

            # Connect to AWS IoT Core
            client.set_callback(self.handle_message)
            client.connect()
            print("Connected to AWS IoT Core")

            # Subscribe to topics
            client.subscribe(self.TOPIC_START)
            client.subscribe(self.TOPIC_STOP)
            client.subscribe(self.TOPIC_TEMP)

            # Handle messages asynchronously
            async def mqtt_handler():
                while True:
                    client.wait_msg()
                    await asyncio.sleep(0.1)

            asyncio.create_task(mqtt_handler())

        except Exception as e:
            print(f"Error during MQTT connection: {e}")
