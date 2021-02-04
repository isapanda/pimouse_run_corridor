#!/usr/bin/env python
#encoding: utf8
import rospy, copy
from geometry_msgs.msg import Twist
from pimouse_run_corridor.msg import ButtonValues
from std_srvs.srv import Trigger, TriggerResponse
from pimouse_ros.msg import LightSensorValues

class WallStop():
    def __init__(self):
        self.cmd_vel = rospy.Publisher('/cmd_vel',Twist,queue_size=1)

        self.sensor_values = LightSensorValues()
        self.button_status = ButtonValues()
        self.START = 1
        self.sw_counter = 0
        self.state = 0
        rospy.Subscriber('/lightsensors', LightSensorValues, self.callback)
        rospy.Subscriber('/button_values',ButtonValues,self.callback_button_status)

    def callback(self,messages):
        self.sensor_values = messages

    def callback_button_status(self,messages):
        self.button_status = messages

    def run(self):
        rate = rospy.Rate(10)
        data = Twist()
        while not rospy.is_shutdown():
            if self.button_status.button1 == 1:
              self.START = 1
              self.sw_counter = self.sw_counter + 1
            else:
              self.START = 0
              self.sw_counter = 0

#            self.START = 1 if self.button_status == UInt16(1) else 0
            if self.START == 1 and self.sw_counter == 10:
               if self.state == 1 :
                    self.state = 0
               elif self.state == 0:
                    self.state = 1

            if self.state == 1:
               rospy.ServiceProxy('/motor_on',Trigger).call()
               if self.sensor_values.sum_all < 80:
                  with open("/dev/rtled0","w") as f:
                     f.write("1\n")
                  with open("/dev/rtled2","w") as f:
                     f.write("0\n")
                  with open("/dev/rtled3","w") as f:
                     f.write("0\n")
                  data.linear.x = 0.1
                  self.cmd_vel.publish(data)
               else:
                  with open("/dev/rtled0","w") as f:
                     f.write("0\n")
                  with open("/dev/rtled2","w") as f:
                     f.write("1\n")
                  with open("/dev/rtled3","w") as f:
                     f.write("0\n")
                  data.linear.x = 0.0
                  self.cmd_vel.publish(data)
            else:
               with open("/dev/rtled0","w") as f:
                  f.write("0\n")
               with open("/dev/rtled2","w") as f:
                  f.write("0\n")
               with open("/dev/rtled3","w") as f:
                  f.write("1\n")
               data.linear.x = 0.0
               self.cmd_vel.publish(data)
               rospy.ServiceProxy('/motor_off',Trigger).call()

            rospy.loginfo(self.button_status)
            rospy.loginfo(self.state)
            rate.sleep()

if __name__=='__main__':
    rospy.init_node('wall_stop')
    rospy.wait_for_service('/motor_on')
    rospy.wait_for_service('/motor_off')
    rospy.on_shutdown(rospy.ServiceProxy('/motor_off',Trigger).call)
#    rospy.ServiceProxy('/motor_on',Trigger).call()
    WallStop().run()
