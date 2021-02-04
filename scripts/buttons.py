#!/usr/bin/env python
#!encoding: utf8

import sys, rospy, math, os
from pimouse_run_corridor.msg import ButtonValues
from std_srvs.srv import Trigger, TriggerResponse

dev_file = "/dev/rtswitch"
button_values = [0,0,0]

if __name__=='__main__':
    rospy.init_node('buttons')
    pub = rospy.Publisher('/button_values', ButtonValues, queue_size =1)
    rate = rospy.Rate(10)
    
    while not rospy.is_shutdown():

     try:
       for i in range(3): 
         button = dev_file + str(i)  
         with open(button,'r') as f:
              button_values[i]=int((f.read())) 
       
       d = ButtonValues()
       d.button0 = button_values[0]
       d.button1 = button_values[1]
       d.button2 = button_values[2]

#       print(d)
       pub.publish(d)
     except:
       rospy.logerr("cannot read rtswitchs")
     
     rate.sleep()
