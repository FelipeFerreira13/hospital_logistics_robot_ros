# Import the necessary libraries
import rospy # Python library for ROS
import cv2 # OpenCV library
import numpy as np
import time

from camera.srv import order_board, order_boardResponse

lower_board       = ( 0,     0,   0 )
upper_board       = ( 180, 100, 100 )

lower_blue        = ( 100, 100,  50 )
upper_blue        = ( 130, 255, 255 )

lower_red         = ( 0,    50,  50 )
upper_red         = ( 15,  200, 200 )
lower_red_high    = ( 170,  50,  50 )
upper_red_high    = ( 180, 200, 200 )

lower_yellow      = ( 20,  100, 100 )
upper_yellow      = ( 35,  255, 255 )


def read_order(req):
 
    # Go through the loop 2 times per second
    rate = rospy.Rate(2) # 2Hz
        
    # Create a VideoCapture object
    cap = cv2.VideoCapture(0)

    time.sleep(1)
   
    for i in range(5):

      table = np.array([["n", "n", "n", "n", "n", "n", "n"],
                        ["n", "n", "n", "n", "n", "n", "n"],
                        ["n", "n", "n", "n", "n", "n", "n"],
                        ["n", "n", "n", "n", "n", "n", "n"],
                        ["n", "n", "n", "n", "n", "n", "n"],
                        ["n", "n", "n", "n", "n", "n", "n"],
                        ["n", "n", "n", "n", "n", "n", "n"]], dtype=str)
        
      # Capture frame-by-frame
      ret, frame = cap.read()
          
      if ret == True:
        # ROtate image 180 degrees
        frame = frame[::-1,:] #Flip Horizontal
        frame = frame[:,::-1] #Flip Vertical

        img = cv2.cvtColor( frame, cv2.COLOR_BGR2HSV )

        # Find Board's information

        hsv_board = cv2.inRange( img, lower_board, upper_board )

        kernel = np.ones((4,4))
        hsv_board = cv2.morphologyEx(hsv_board, cv2.MORPH_OPEN, kernel,  iterations = 1)
        hsv_board = cv2.morphologyEx(hsv_board, cv2.MORPH_CLOSE, kernel, iterations = 5)

        c, h = cv2.findContours( hsv_board, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE )

        max_area = 0
        x_ = 0; y_ = 0; w_ = 0; h_ = 0 
        for cnts in c:
          ( x, y, w, h ) = cv2.boundingRect(cnts)

          area = w * h

          if area > max_area:
              max_area = area
              x_ = x; y_ = y; w_ = w; h_ = h

        # Selects the part of the image of the board 
        img_shape = img.shape
        img_crop = np.zeros( ( img_shape[0], img_shape[1], 3 ) )
        img_crop[ y_:y_ + h_, x_:x_ + w_ ] = img[ y_:y_ + h_, x_:x_ + w_ ]

        # Find Tag's information
              
        hsv_blue     = cv2.inRange( img_crop, lower_blue,     upper_blue     )
        hsv_red      = cv2.inRange( img_crop, lower_red,      upper_red      )
        hsv_red_high = cv2.inRange( img_crop, lower_red_high, upper_red_high )
        hsv_red = cv2.bitwise_or( hsv_red, hsv_red_high ) # Merge low and high hsv red
        hsv_yellow   = cv2.inRange( img_crop, lower_yellow,   upper_yellow   )

        hsv_blue   = cv2.morphologyEx(hsv_blue,   cv2.MORPH_OPEN, kernel,  iterations = 1)
        hsv_red    = cv2.morphologyEx(hsv_red,    cv2.MORPH_OPEN, kernel,  iterations = 1)
        hsv_yellow = cv2.morphologyEx(hsv_yellow, cv2.MORPH_OPEN, kernel,  iterations = 1)

        c_b, h = cv2.findContours( hsv_blue,   cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE )
        c_r, h = cv2.findContours( hsv_red,    cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE )
        c_y, h = cv2.findContours( hsv_yellow, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE )
        
        contours = [ c_r, c_b, c_y ]
        cube     = [ 'w', 'b', 'y' ]

        for c, name in zip(contours, cube):
          for cnts in c:
            
            if ( cv2.contourArea( cnts ) > 20):
              ( x, y, w, h ) = cv2.boundingRect(cnts)

              index_x = round((abs( (x + ( w / 2 )) - x_ ) / (w_ / 7.0)) - 0.5)
              index_y = round((abs( (y + ( h / 2 )) - y_ ) / (h_ / 7.0)) - 0.5)

              if ( table[index_x][index_y] == 'w' and name == 'b' or table[index_x][index_y] == 'b'):
                table[index_x][index_y] = name
              elif ( name == 'b' ):
                table[index_x][index_y] = 'g'
              else:
                table[index_x][index_y] = name

        rec = frame.copy()

        # Put a Rectangle around the board and each tag
        for i in range(7):
          for j in range(7):
            cv2.putText(rec, str(table[i][j]), ( int(x_ - 10 + ( (i * (w_ / 7)) + (w_ / 7) / 2 )), int(y_ + 10 + ( (j * (h_ / 7)) + (w_ / 7) / 2 ))), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2)
            cv2.rectangle( rec, ( int(x_ + ( i * w_ / 7 )), int(y_ + ( j * h_ / 7 )) ), ( int(x_ + ( (i + 1) * w_ / 7 )), int(y_ + ( (j + 1) * h_ / 7 )) ), (0,255,0),5,cv2.LINE_AA)
              

        cv2.imshow('image', frame)
        cv2.imshow('hsv_board', hsv_board)
        cv2.imshow('hsv_blue', hsv_blue)
        cv2.imshow('hsv_red', hsv_red)
        cv2.imshow('hsv_yellow', hsv_yellow)
        cv2.imshow('img_crop', img_crop)
        cv2.imshow('rec', rec)

        cv2.waitKey(0)
                
        # Sleep just enough to maintain the desired rate
        rate.sleep()
    
    cap.release()
    cv2.destroyAllWindows()

    print( table )
    
    table = table.transpose()

    step = 7

    return order_boardResponse( table.flatten(), step )

def simple_cam_node():
  rospy.init_node('order_board_node')
  srv = rospy.Service('/camera/read_order_board', order_board, read_order)

  rospy.spin()
  
if __name__ == '__main__':
  simple_cam_node()