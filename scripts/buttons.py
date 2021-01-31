#!/usr/bin/env python
#!encoding: utf8

import sys, rospy, math, os
from std_msgs.msg import UInt16
from std_srvs.srv import Trigger, TriggerResponse

if __name__=='__main__':
    devfile = "/dev/rtswitch1"
    rospy.init_node('button')
    pub = rospy.Publisher('/button_read', UInt16, queue_size =1)
    rate = rospy.Rate(10)
#    rospy.wait_for_service('/button_read')
    while not rospy.is_shutdown():
      try:
          with open(devfile,'r') as f:
              status = int(f.read())
              pub.publish(status)
#              rospy.loginfo(status)
      except:
          rospy.logerr("cannot read rtswitch1")
      rate.sleep()
