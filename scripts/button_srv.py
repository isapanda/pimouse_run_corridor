#!/usr/bin/env python
#!encoding: utf8

import sys, rospy, math, os
from std_srvs.srv import Trigger, TriggerResponse


class Button():
    def  __init__(self):
        rospy.Service('button_read', Trigger, self.callback_button_read)

    def callback_button_read(self,message): return self.button_read()

    def button_read(self):
        d = TriggerResponse()
        try:
            with open("/dev/rtswitch1","r") as f:
                self.log = int(f.read())
                d.success = True
                d.message = "ON" if self.log else "OFF"
                rospy.loginfo(self.log)
                
        except:
           rospy.logerr("cannot read rtswitch1")
        return d
if __name__=='__main__':
    rospy.init_node('button') 
#    rospy.wait_for_service('/button_read')
    b = Button()
    rospy.spin()
