#!/usr/bin/env python
#encoding: utf8
import rospy, copy, math
from geometry_msgs.msg import Twist
from pimouse_run_corridor.msg import ButtonValues
from pimouse_run_corridor.msg import LedValues
from std_srvs.srv import Trigger, TriggerResponse
from pimouse_ros.msg import LightSensorValues

class WallStop():
    def __init__(self):

        self.state = 0
        
        self.sensor_values = LightSensorValues()
        self.button_status = ButtonValues()
        
        self.led     = rospy.Publisher('led_values', LedValues, queue_size=1)
        self.cmd_vel = rospy.Publisher('/cmd_vel',Twist,queue_size=1)
        rospy.Subscriber('/lightsensors', LightSensorValues, self.callback)
        rospy.Subscriber('/button_values',ButtonValues,self.callback_button_status)


    def callback(self,messages):
        self.sensor_values = messages

    def callback_button_status(self,messages):
        self.button_status = messages

    def run(self):
        rate = rospy.Rate(20)
        
        ON    = 1
        OFF   = 0
        GO    = 1
        STOP  = 0
        CLEAR = 0
        THRESHOLD = 300
        
        led_on_off= LedValues()
        motor_speed = Twist()

        while not rospy.is_shutdown():
            s = self.sensor_values
            if self.button_status.button1 == ON:
               sw_counter = sw_counter + 1
            else:
               sw_counter = CLEAR

            if sw_counter ==10:
               if   self.state == GO:
                    self.state = STOP
               
               elif self.state == STOP:
                    self.state = GO

            if self.state == GO:
               rospy.ServiceProxy('/motor_on',Trigger).call()
               
               led_on_off.green_value  = ON
               led_on_off.blue_value   = OFF
               led_on_off.yellow_value = OFF
               led_on_off.red_value    = OFF
                   
                 
               if s.left_forward or s.right_forward > 120:

                  error = (s.right_forward - s.left_forward)/10
              
                  #motor_speed.linear.x  = 0.1
                  motor_speed.linear.x    = 0.1 - (s.right_forward + s.left_forward)/8000
                  motor_speed.angular.z = error * 5 * math.pi /180.0               
                  self.cmd_vel.publish(motor_speed)
                  self.led.publish(led_on_off)

#               elif (s.left_side + s.right_side) > 80:
#
#                  led_on_off.blue_value   = ON
#                  motor_speed.linear.x  = 0.01
#                  motor_speed.angular.z = 300 * math.pi /180.0               
#
#                  self.cmd_vel.publish(motor_speed)
#                  self.led.publish(led_on_off)

               else:
                  led_on_off.green_value  = OFF
                  led_on_off.blue_value   = OFF
                  led_on_off.yellow_value = ON
                  led_on_off.red_value    = OFF

                  motor_speed.linear.x    = 0.1 - (s.right_side + s.left_side)/10000
                  
                  error = (s.right_side - s.left_side)/10
                  motor_speed.angular.z = error * 13 * math.pi /180.0               
                  
                  self.led.publish(led_on_off)
                  self.cmd_vel.publish(motor_speed)

            else: #if PROGRAM = STOP
               led_on_off.green_value     = OFF
               led_on_off.blue_value      = OFF
               led_on_off.yellow_value    = OFF
               led_on_off.red_value       = ON
               
               motor_speed.linear.x       = 0.0
               
               self.led.publish(led_on_off)
               self.cmd_vel.publish(motor_speed)
           
               rospy.ServiceProxy('/motor_off',Trigger).call()

            #rospy.loginfo(self.button_status)
            #rospy.loginfo(self.state)
            rate.sleep()

if __name__=='__main__':
    rospy.init_node('wall_stop')
    rospy.wait_for_service('/motor_on')
    rospy.wait_for_service('/motor_off')
    rospy.on_shutdown(rospy.ServiceProxy('/motor_off',Trigger).call)
    WallStop().run()
