import rospy 
import cv2 
import numpy as np

from camera.srv import dispensary
from geometry_msgs.msg import Twist
from geometry_msgs.msg import Vector3


desired_x = 175
desired_y = 175

lower_blue   = ( 100, 100,  50 )
upper_blue   = ( 130, 255, 255 )
area_blue    = 3400

lower_red    = ( 170,  25,  25 )
upper_red    = ( 180, 220, 220 )
lower_red_h  = ( 0,  25,  25 )
upper_red_h  = ( 10, 220, 220 )
area_red     = 2100

lower_yellow = ( 20,  100, 100 )
upper_yellow = ( 35,  255, 255 )
area_yellow  = 3450

class disp():
    def __init__( self ):
        self.pub = rospy.Publisher ('/cmd_vel',                       Twist, queue_size=1)
        self.sub = rospy.Subscriber( "robot/position",                Vector3,    self.pos_callback )
        self.srv = rospy.Service   ('/camera/dispensary/follow_cube', dispensary, self.take_image)
        self.th  = 0.0

    def pos_callback(self, data):
        self.th = data.z

    def take_image(self, req):
 
        # Go through the loop 2 times per second
        rate = rospy.Rate(10) # 2Hz
            
        # Create a VideoCapture object
        cap = cv2.VideoCapture(0)

        count = 0
    
        # While ROS is still running.
        while not rospy.is_shutdown():
            
            # Capture frame-by-frame
            ret, frame = cap.read()
            frame = cv2.resize( frame, None, fx = 0.5, fy = 0.5 )
                
            if ret == True:

                cube = req.cube
                area_cube = 0

                hsv = cv2.cvtColor( frame, cv2.COLOR_BGR2HSV )

                

                if   ( cube == 'blue' ):
                    mask = cv2.inRange( hsv, lower_blue, upper_blue )
                    area_cube = area_blue
                elif ( cube == 'white' ):
                    mask = cv2.inRange( hsv, lower_blue, upper_blue )
                    kernel = np.ones((6,6))
                    mask_b = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations = 5)
                    cv2.imshow('blue_close', mask_b)

                    mask_r  = cv2.inRange( hsv, lower_red,   upper_red   )
                    mask_r2 = cv2.inRange( hsv, lower_red_h, upper_red_h )
                    mask_r = cv2.bitwise_or( mask_r, mask_r2 )

                    mask_b_r = cv2.bitwise_and( mask_b, mask_r )

                    cv2.imshow('mask_b_r', mask_b_r)

                    mask = cv2.bitwise_xor( mask_r,mask_b_r )

                    cv2.imshow('mask_r', mask_r)

                    area_cube = area_red
                else:
                    mask = cv2.inRange( hsv, lower_yellow, upper_yellow )
                    area_cube = area_yellow
                
                kernel = np.ones((3,3))
                mask = cv2.morphologyEx( mask, cv2.MORPH_OPEN, kernel,  iterations = 1)

                c, h = cv2.findContours( mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE )

                max_area = 0
                x_ = 0
                y_ = 0
                for cnts in c:
                    ( x, y, w, h ) = cv2.boundingRect(cnts)

                    area = w * h


                    if area > max_area:
                        max_area = area
                        x_ = x + ( w / 2 )
                        y_ = y + ( y / 2 )

                print("x: ", x_, "y: ", y_, "max_area: ", max_area)

                vx  = 0
                vy  = 0
                vth = 0
                vz  = 0

                max_linear_speed   = 0.1
                max_elevator_speed = 0.075
                max_angular_speed  = 0.4

                if   ( abs( x_ - desired_x ) > 15 ):
                    speed = (abs( x_ - desired_x ) / 50.0) * max_linear_speed
                    if ( speed > max_linear_speed): speed = max_linear_speed
                    vy = (( x_ - desired_x ) / abs( x_ - desired_x )) * speed

                elif ( abs( y_ - desired_y ) > 15 ):
                    speed = (abs( y_ - desired_y ) / 50.0) * max_elevator_speed
                    if ( speed > max_elevator_speed): speed = max_elevator_speed
                    vz = (( y_ - desired_y ) / abs( y_ - desired_y )) * speed

                elif ( abs( max_area - area_cube ) > 150 ):
                    speed = (abs( max_area - area_cube ) / 1000.0) * 0.1
                    if ( speed > max_linear_speed): speed = max_linear_speed
                    vx = (( area_cube - max_area ) / abs( area_cube - max_area )) * speed

                th_diff = req.angle - self.th
                if   ( th_diff > 180 ):
                    th_diff = th_diff - 360
                elif ( th_diff < -180 ):
                    th_diff = th_diff + 360

                if( abs( th_diff ) > 3 ):
                    vth = (th_diff / 10.0) * max_angular_speed
                    if   ( vth > max_angular_speed ):
                        vth = max_angular_speed
                    elif ( vth < -max_angular_speed ):
                        vth = -max_angular_speed

                msg = Twist()

                msg.linear.x = vx
                msg.linear.y = vy
                msg.linear.z = vz
                msg.angular.z = vth

                self.pub.publish(msg)

                if ( vx == 0 and vy == 0 and vth == 0 and vz == 0 ):
                    count = count + 1

                if count > 3:
                    break

                cv2.imshow('image', frame)
                cv2.imshow('mask', mask)
                    
                cv2.waitKey(1)
                    
            # Sleep just enough to maintain the desired rate
            rate.sleep()

        return True


  
if __name__ == '__main__':
  rospy.init_node('dispensary_node')

  disp = disp()

  rospy.spin()