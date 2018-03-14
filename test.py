#!/usr/bin/python3

# Script to test the Automation HAT
import time
import automationhat

if automationhat.is_automation_hat():
    automationhat.light.power.write(1)

one = 1
two = 1
three = 1

if automationhat.is_automation_hat():
    automationhat.light.comms.on()
    automationhat.output.one.write(one)
    automationhat.output.two.write(two)
    automationhat.output.three.write(three)
    automationhat.light.comms.off()

if automationhat.is_automation_hat():
    automationhat.light.comms.on()
    automationhat.relay.one.write(one)
    automationhat.relay.two.write(two)
    automationhat.relay.three.write(three)

time.sleep(10)
