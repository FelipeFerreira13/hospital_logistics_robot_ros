import rospy 
import cv2 
import numpy as np

from camera.srv import stand
from geometry_msgs.msg import Twist
from geometry_msgs.msg import Vector3

lower_green   = ( 100, 100,  50 )
upper_green   = ( 130, 255, 255 )
area_green    = 3900

lower_red    = ( 170,  50,  50 )
upper_red    = ( 180, 255, 255 )
lower_red_h  = ( 0,  50,  50 )
upper_red_h  = ( 10, 255, 255 )
area_red     = 2100

desired_x = 0
desired_y = 0

class stand_class():
    def __init__( self ):
        self.pub = rospy.Publisher ('/cmd_vel',                   Twist,   queue_size=1)
        self.sub = rospy.Subscriber( "robot/position",            Vector3, self.pos_callback )
        self.srv = rospy.Service   ('/camera/stand/follow_stand', stand,   self.take_image)
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

            shape = frame.shape
                
            if ret == True:

                cube = req.cube
                area_cube = 0

                hsv = cv2.cvtColor( frame, cv2.COLOR_BGR2HSV )

                if   ( cube == 'green' ):
                    mask = cv2.inRange( hsv, lower_green, upper_green )
                    area_cube = area_green
                elif ( cube == 'red' ):
                    mask_r  = cv2.inRange( hsv, lower_red,   upper_red   )
                    mask_r2 = cv2.inRange( hsv, lower_red_h, upper_red_h )
                    mask = cv2.bitwise_or( mask_r, mask_r2 )
                    area_cube = area_red
                
                kernel = np.ones((3,3))
                mask = cv2.morphologyEx( mask, cv2.MORPH_OPEN,  kernel,  iterations = 1)
                mask = cv2.morphologyEx( mask, cv2.MORPH_CLOSE, kernel,  iterations = 1)

                c, h = cv2.findContours( mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE )

                max_area = 0
                x_ = 0
                y_ = 0
                area = 0
                c_info = []

                for cnts in c:
                    ( x, y, w, h ) = cv2.boundingRect(cnts)

                    delta_x = abs((shape[1] / 2) - (x + ( w / 2 )))
                    
                    if ( w * h ) > max_area:
                        area = ( w * h )
                        x_ = x + ( w / 2 )
                        y_ = y + ( y / 2 )
                        c_info = [ x, y, w, h ]

                print("x: ", x_, "y: ", y_, "area: ", c_info[2] * c_info[3])

                cv2.rectangle( frame, (c_info[0], c_info[1]), (c_info[0] + c_info[2], c_info[1] + c_info[3]), (0,0,255), 1 )

                vx  = 0
                vy  = 0
                vth = 0
                vz  = 0

                max_linear_speed   = 0.15
                max_elevator_speed = 0.075
                max_angular_speed  = 0.4

                if   ( abs( x_ - desired_x ) > 10 ):
                    speed = (abs( x_ - desired_x ) / 75.0) * max_linear_speed
                    if ( speed > max_linear_speed): speed = max_linear_speed
                    vy = (( x_ - desired_x ) / abs( x_ - desired_x )) * speed

                elif ( abs( y_ - desired_y ) > 10 ):
                    speed = (abs( y_ - desired_y ) / 35.0) * max_elevator_speed
                    if ( speed > max_elevator_speed): speed = max_elevator_speed
                    vz = (( y_ - desired_y ) / abs( y_ - desired_y )) * speed

                elif ( abs( area - area_cube ) > 150 ):
                    speed = (abs( area - area_cube ) / 1500.0) * 0.1
                    if ( speed > max_linear_speed): speed = max_linear_speed
                    vx = (( area_cube - area ) / abs( area_cube - area )) * speed


                th_diff = req.angle - self.th
                if   ( th_diff > 180 ):
                    th_diff = th_diff - 360
                elif ( th_diff < -180 ):
                    th_diff = th_diff + 360

                if( abs( th_diff ) > 0.5 ):
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
            
        cap.release()
        cv2.destroyAllWindows()

        return True


  
if __name__ == '__main__':
  rospy.init_node('stand_node')

  stand = stand_class()

  rospy.spin()