/************************************
 *  Author: Felipe Ferreira
 * Release version: 1.0.0.0
 * Release date: 27/06/2024
 * 
 * Modified by: Felipe Ferreira
 * Last modification date: 
 * New version:

*************************************/

#include "main.h"

int main(int argc, char **argv)
{
    ros::init(argc,argv,"main_node");
    ros::NodeHandle nh;

    ROS_INFO("main node is now started");

    move_goal_c    = nh.serviceClient<base_controller::move_goal>    ("base_controller/move_base/goal"  );
    simple_goal_c  = nh.serviceClient<base_controller::move_goal>    ("base_controller/simple_move/goal");
    set_position_c = nh.serviceClient<odometry::pose_odom>           ("odometry/set_position"           );
    set_height_c   = nh.serviceClient<vmxpi_ros_bringup::set_height> ("oms/set_height"                  );
    reset_height_c = nh.serviceClient<vmxpi_ros_bringup::reset>      ("oms/reset"                       );
    set_gripper_c  = nh.serviceClient<vmxpi_ros_bringup::set_gripper>("oms/set_gripper"                 );
    read_order_c   = nh.serviceClient<camera::order_board>           ("camera/read_order_board"         );
    read_disp_c    = nh.serviceClient<camera::dispensary>            ("camera/dispensary/follow_cube"   );

    ros::Subscriber height_sub   = nh.subscribe("oms/height",     1, heightCallback  );
    ros::Subscriber position_sub = nh.subscribe("robot/position", 1, positionCallback);

    
    ros::Duration(10).sleep();

    // Main Logic

    // reset_height( 1 );

    // set_gripper( GRIPPER_OPEN );

    // set_position( 30, 30, 90 );  

    // position_driver( 100, 30, 90, "simple_move" );


    // position_driver( 0.87, 0.75, 270, "simple_move" );

    // oms_driver( 20 );

    // read_order();

    // reset_height( 1 );

    // char task_to_do = 'n';
    // int room = -1;

    // for ( int i = 1; i < 7; i++ ){
    //     for ( int j = 1; j < 7; j++ ){
    //         if ( order_board[j][i] != 'n' ){
    //             task_to_do = order_board[j][i];
    //             room = i;
    //             order_board[j][i] = 'n';
    //             break;
    //         }
    //     }
    //     if ( task_to_do != 'n' ){ break; }
    // }

    // ROS_INFO("task: %c, room: %i", task_to_do, room);

    // position_driver( 1.0, 1.0, 180, "simple_move" );

    read_dispensary( "yellow", 180 );

    // ros::spinOnce();

    // oms_driver( oms_height + 10 );

    // position_driver( robot_position.x - 18, robot_position.y, 180, "simple_move" );

    ros::spin();
    ros::shutdown();

    return 0;
};
