#!/usr/bin/env python
#encoding: utf8
import rospy, copy
from geometry_msgs.msg import Twist
from pimouse_run_corridor.msg import ButtonValues
from pimouse_run_corridor.msg import LedValues
from std_srvs.srv import Trigger, TriggerResponse
from pimouse_ros.msg import LightSensorValues

class WallStop():
    def __init__(self):
        self.cmd_vel = rospy.Publisher('/cmd_vel',Twist,queue_size=1)

        self.sensor_values = LightSensorValues()
        self.button_status = ButtonValues()
        self.PROGRAM = 1
        self.sw_counter = 0
        self.state = 0
        self.led = rospy.Publisher('led_values', LedValues, queue_size=1)
        rospy.Subscriber('/lightsensors', LightSensorValues, self.callback)
        rospy.Subscriber('/button_values',ButtonValues,self.callback_button_status)


    def callback(self,messages):
        self.sensor_values = messages

    def callback_button_status(self,messages):
        self.button_status = messages

    def run(self):
        rate = rospy.Rate(10)
        
        ON    = 1
        OFF   = 0
        GO    = 1
        STOP  = 0
        CLEAR = 0
        THRESHOLD = 80

        led_on_off= LedValues()
        motor_speed = Twist()

        while not rospy.is_shutdown():
            if self.button_status.button1 == ON:
                self.PROGRAM    = GO
                self.sw_counter = self.sw_counter + 1
            else:
                self.PROGRAM    = STOP
                self.sw_counter = CLEAR

#            self.START = 1 if self.button_status == UInt16(1) else 0
            if self.PROGRAM == ON and self.sw_counter == 10:
               if   self.state == GO  :
                      self.state = STOP
               elif self.state == STOP:
                      self.state = GO

            if self.state == GO:
               rospy.ServiceProxy('/motor_on',Trigger).call()
               if self.sensor_values.sum_all < THRESHOLD:
                  
                  led_on_off.green_value  = ON
                  led_on_off.blue_value   = OFF
                  led_on_off.yellow_value = OFF
                  led_on_off.red_value    = OFF
                   
                  motor_speed.linear.x = 0.1
                  
                  self.led.publish(led_on_off)
                  self.cmd_vel.publish(motor_speed)

               else:
                  led_on_off.green_value  = OFF
                  led_on_off.blue_value   = OFF
                  led_on_off.yellow_value = ON
                  led_on_off.red_value    = OFF

                  motor_speed.linear.x = 0.0
                  
                  self.led.publish(led_on_off)
                  self.cmd_vel.publish(motor_speed)

            else: #if PROGRAM = STOP
               led_on_off.green_value  = OFF
               led_on_off.blue_value   = OFF
               led_on_off.yellow_value = OFF
               led_on_off.red_value    = ON
               
               motor_speed.linear.x = 0.0
               
               self.led.publish(led_on_off)
               self.cmd_vel.publish(motor_speed)
           
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
