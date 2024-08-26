#include <ros/ros.h>
#include <tf/transform_broadcaster.h>
#include <geometry_msgs/Pose.h>

#include "std_msgs/Float32.h"
#include "std_msgs/Bool.h"
#include <geometry_msgs/Vector3.h>

#include <string.h>

// Move Service
#include "base_controller/move_goal.h"
// Odometry Service
#include "odometry/pose_odom.h"
// OMS services
#include "vmxpi_ros_bringup/set_height.h"
#include "vmxpi_ros_bringup/set_gripper.h"
#include "vmxpi_ros_bringup/reset.h"
// Camera services
#include "camera/order_board.h"
#include "camera/dispensary.h"


ros::ServiceClient move_goal_c, set_position_c, set_height_c, reset_height_c, set_gripper_c, read_order_c, read_disp_c, simple_goal_c;

enum GRIPPER { GRIPPER_OPEN = 70,  GRIPPER_CUBE_O = 90, GRIPPER_CUBE_C = 140, GRIPPER_CLOSE = 150 };

inline bool start_button = true;
inline double oms_height;
inline geometry_msgs::Vector3 robot_position;

char order_board[7][7] = {{'n', 'n', 'n', 'n', 'n', 'n', 'n'},
                          {'n', 'n', 'n', 'n', 'n', 'n', 'n'},
                          {'n', 'n', 'n', 'n', 'n', 'n', 'n'},
                          {'n', 'n', 'n', 'n', 'n', 'n', 'n'},
                          {'n', 'n', 'n', 'n', 'n', 'n', 'n'},
                          {'n', 'n', 'n', 'n', 'n', 'n', 'n'},
                          {'n', 'n', 'n', 'n', 'n', 'n', 'n'}};

void set_position( double x, double y, double th ){
    odometry::pose_odom pose;

    pose.request.x = x;
    pose.request.y = y;
    pose.request.th = th;

    set_position_c.call( pose );
}

void position_driver( double x, double y, double th, std::string move_type ){
    base_controller::move_goal goal;

    goal.request.x = x;
    goal.request.y = y;
    goal.request.th = th;

    if ( move_type.compare( "move_base" ) == 0 ){
        move_goal_c.call( goal );
    }
    else if ( move_type.compare( "simple_move" ) == 0 ){
        simple_goal_c.call( goal );
    }

}

void oms_driver( double height ){
    vmxpi_ros_bringup::set_height position;

    position.request.height = height;

    set_height_c.call(position);
}

void reset_height( int direction ){
    vmxpi_ros_bringup::reset reset;

    reset.request.direction = direction;

    reset_height_c.call( reset );
}

void set_gripper( int angle ){
    vmxpi_ros_bringup::set_gripper gripper;

    gripper.request.angle = angle;

    set_gripper_c.call( gripper );
}

void read_order( ){
    
    ROS_INFO("Start Read Work Order Service");

    camera::order_board msg;
    msg.request.start = true;
    read_order_c.call( msg );

    for ( int i = 0; i < msg.response.step; i++ ){
        for ( int j = 0; j < msg.response.step; j++ ){
            order_board[i][j] = char(msg.response.board[ (i * msg.response.step) + j][0]);
        }
    }
}

void read_dispensary( std::string cube, float angle ){
    camera::dispensary msg;
    msg.request.cube.assign( cube );
    msg.request.angle = angle;

    read_disp_c.call(msg);
}

void heightCallback( const std_msgs::Float32::ConstPtr& msg ){
    oms_height = msg->data;
}

void positionCallback( const geometry_msgs::Vector3::ConstPtr& msg ){
    robot_position.x = msg->x;
    robot_position.y = msg->y;
    robot_position.z = msg->z;
}

void startCallback( const std_msgs::Bool::ConstPtr& msg ){
    start_button = msg->data;
}