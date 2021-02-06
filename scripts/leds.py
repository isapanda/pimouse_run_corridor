#!/usr/bin/env python
#!encoding: utf8

import sys, rospy, math, os
from pimouse_run_corridor.msg import LedValues

class Leds():

    def __init__(self):
        self.led_values = LedValues()
        self.ON = 1
        self.OFF = 0
        rospy.Subscriber('/led_values', LedValues, self.callback_leds)

    def callback_leds(self,message):
        self.switch_leds(message.green_value, message.blue_value, message.yellow_value, message.red_value)
 
    def switch_leds(self,green_value, blue_value, yellow_value, red_value): 
        try:
           with open("/dev/rtled0",'w') as green,\
                open("/dev/rtled1",'w') as blue,\
                open("/dev/rtled2",'w') as yellow,\
                open("/dev/rtled3",'w') as red:
           
                green.write(str(green_value) +"\n")
                blue.write(str(blue_value) +"\n")
                yellow.write(str(yellow_value) +"\n")
                red.write(str(red_value) +"\n")
        except:
           rospy.logerr("cannot switch leds")


if __name__=='__main__':
    rospy.init_node('leds')
    l = Leds()
    rospy.spin()   
