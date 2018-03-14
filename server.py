#!/usr/bin/python3
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from json import dumps
from threading import Timer
import automationhat
import RPi.GPIO as GPIO

app = Flask(__name__)
api = Api(app)

# Define some spare pins in addition to the pins used by the Automation Hat
PORCH_LIGHT_PIN = 17
# Unused pins for later use
SPARE1_PIN = 27
SPARE2_PIN = 22
# SPARE3_PIN = 23
# SPARE4_PIN = 24
# SPARE5_PIN = 25

def Setup():
    # Turn on the automation hat power light
    if automationhat.is_automation_hat():
        automationhat.light.power.write(1)
    # Automation Hat BCM pins used
    #RELAY_1 = 13 RELAY_2 = 19 RELAY_3 = 16
    #INPUT_1 = 26 INPUT_2 = 20 INPUT_3 = 21
    #OUTPUT_1 = 5 OUTPUT_2 = 12 OUTPUT_3 = 6

    GPIO.setwarnings(True)
    # Use the broadcom pin layout
    GPIO.setmode(GPIO.BCM)
    # Setup some additional pins
    GPIO.setup(PORCH_LIGHT_PIN, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(SPARE1_PIN, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(SPARE2_PIN, GPIO.OUT, initial=GPIO.LOW)

# Helper functions
# ================

# Turn's on both of the Automation Hat LED's, used to indicate a POST operaton
def turnOnLeds():
    if automationhat.is_automation_hat():
        automationhat.light.comms.on()
        automationhat.light.warn.on()

# Turn's on the Automation Hat Comms LED, used to indicate a GET operaton
def turnOnCommsLed():
    if automationhat.is_automation_hat():
        automationhat.light.comms.on()

def turnOffCommsLed():
    if automationhat.is_automation_hat():
        automationhat.light.comms.off()

def turnOffWarnLed():
    if automationhat.is_automation_hat():
        automationhat.light.warn.off()

# Turn's off the Automation Hat LED's after a specified time delay in seconds
def turnOffLeds(commsLedTime, warnLedTime = None):
    if automationhat.is_automation_hat():
        t = Timer(commsLedTime, turnOffCommsLed)
        t.start()
        if warnLedTime is not None:
            t2 = Timer(warnLedTime, turnOffWarnLed)
            t2.start()

# Translate the state attribute
def getStateFromAttribute(obj, attrName):
    state = obj.get(attrName, None)
    #print('state: {}'.format(state))
    if state == 1 or state == '1' or state == 'on':
        state = 1
    elif state == 0 or state == '0' or state == 'off':
        state = 0
    else:
        state = None
    return state


# Web API functions
# ================

# Process the entering or exiting of a geofence location
class Location(Resource):
    def post(self):
        content = request.get_json()
        print('post body: {}'.format(content))
        location = content.get('location', None)
        turnOnLeds()

        if location == 'entered':
            GPIO.output(PORCH_LIGHT_PIN, 1)
        elif location == 'exited':
            GPIO.output(PORCH_LIGHT_PIN, 0)
        
        porchLight = GPIO.input(PORCH_LIGHT_PIN)
        turnOffLeds(0.5, 1.0) 
        return { 'porchLight':porchLight }

# Gets and sets the state of the additional pins
class OutputPins(Resource):
    def get(self):
        turnOnCommsLed()
        porchLight = GPIO.input(PORCH_LIGHT_PIN)
        spare1 = GPIO.input(SPARE1_PIN)
        spare2 = GPIO.input(SPARE2_PIN)
        turnOffLeds(0.5)
        return { 'porchLight':porchLight, 'spare1':spare1, 'spare2':spare2 }

    def post(self):
        content = request.get_json()
        print('post body: {}'.format(content))
        porchLight = getStateFromAttribute(content, 'porchLight')
        spare1 = getStateFromAttribute(content, 'spare1')
        spare2 = getStateFromAttribute(content, 'spare2')
        turnOnLeds()

        if porchLight is not None:
            GPIO.output(PORCH_LIGHT_PIN, porchLight)
        if spare1 is not None:
            GPIO.output(SPARE1_PIN, spare1)
        if spare2 is not None:
            GPIO.output(SPARE2_PIN, spare2)
        
        porchLight = GPIO.input(PORCH_LIGHT_PIN)
        spare1 = GPIO.input(SPARE1_PIN)
        spare2 = GPIO.input(SPARE2_PIN)
        turnOffLeds(0.5, 1.0) 
        return { 'porchLight':porchLight, 'spare1':spare1, 'spare2':spare2 }

# Get the state of the Automation Hat's ADC pins
class Analog(Resource):
    def get(self):
        if automationhat.is_automation_hat():
            automationhat.light.comms.on()
            one = automationhat.analog.one.read()
            two = automationhat.analog.two.read()
            three = automationhat.analog.three.read()
            turnOffLeds(0.5) 
            return { 'one':one, 'two': two, 'three':three }
        else:
            return { 'error':'Automation Hat not found!' }, 500

# Get the state of the Automation Hat's digital input pins
class Input(Resource):
    def get(self):
        if automationhat.is_automation_hat():
            automationhat.light.comms.on()
            one = automationhat.input.one.read()
            two = automationhat.input.two.read()
            three = automationhat.input.three.read()
            turnOffLeds(0.5) 
            return { 'one':one, 'two': two, 'three':three }
        else:
            return { 'error':'Automation Hat not found!' }, 500

# Gets and sets the state of the Automation Hat's buffered digital output pins
class Output(Resource):
    def get(self):
        if automationhat.is_automation_hat():
            automationhat.light.comms.on()
            one = automationhat.output.one.read()
            two = automationhat.output.two.read()
            three = automationhat.output.three.read()
            turnOffLeds(0.5) 
            return { 'one':one, 'two': two, 'three':three }
        else:
            return { 'error':'Automation Hat not found!' }, 500

    def post(self):
        content = request.get_json()
        print('post body: {}'.format(content))
        one = getStateFromAttribute(content, 'one')
        two = getStateFromAttribute(content, 'two')
        three = getStateFromAttribute(content, 'three')

        if automationhat.is_automation_hat():
            automationhat.light.comms.on()
            automationhat.light.warn.on()
            if one is not None:
                automationhat.output.one.write(one)
            if two is not None:
                automationhat.output.two.write(two)
            if three is not None:
                automationhat.output.three.write(three)

            turnOffLeds(0.5, 1.0) 
            one = automationhat.output.one.read()
            two = automationhat.output.two.read()
            three = automationhat.output.three.read()
            return { 'one':one, 'two': two, 'three':three }
        else:
            return { 'error':'Automation Hat not found!' }, 500

# Gets and sets the state of the Automation Hat's relay output pins
class Relay(Resource):
    def get(self):
        if automationhat.is_automation_hat():
            automationhat.light.comms.on()
            one = automationhat.relay.one.read()
            two = automationhat.relay.two.read()
            three = automationhat.relay.three.read()
            turnOffLeds(0.5) 
            return { 'one':one, 'two': two, 'three':three }
        else:
            return { 'error':'Automation Hat not found!' }, 500

    def post(self):
        content = request.get_json()
        print('post body: {}'.format(content))
        one = getStateFromAttribute(content, 'one')
        two = getStateFromAttribute(content, 'two')
        three = getStateFromAttribute(content, 'three')

        if automationhat.is_automation_hat():
            automationhat.light.comms.on()
            automationhat.light.warn.on()
            if one is not None:
                automationhat.relay.one.write(one)
            if two is not None:
                automationhat.relay.two.write(two)
            if three is not None:
                automationhat.relay.three.write(three)
            turnOffLeds(0.5, 1.0) 

            one = automationhat.relay.one.read()
            two = automationhat.relay.two.read()
            three = automationhat.relay.three.read()
            return { 'one':one, 'two': two, 'three':three }
        else:
            return { 'error':'AutomationHat not found!' }, 500


# Define the routes
api.add_resource(Location, '/api/location')
api.add_resource(OutputPins, '/api/outputpins')
api.add_resource(Input, '/api/input')
api.add_resource(Analog, '/api/analog')
api.add_resource(Output, '/api/output')
api.add_resource(Relay, '/api/relay')

# Start the server
if __name__ == '__main__':
    print("Starting Server...")
    try: 
        Setup()
        app.run(host= '0.0.0.0', port=5002)
    
    except KeyboardInterrupt:  
        # here you put any code you want to run before the program   
        # exits when you press CTRL+C  
        print("\nKeyboard interrupted the server")
    
    # except:  
    #     # this catches ALL other exceptions including errors.  
    #     # You won't get any error messages for debugging  
    #     # so only use it once your code is working  
    #     print("\nOther error or exception occurred!")
    
    finally:
        print("\nScript exited")
        # GPIO.cleanup is actually handled by the Automation Hat library
        # print("\nCleaning up")
        # GPIO.cleanup() # this ensures a clean exit 