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

    move_goal_c    = nh.serviceClient<base_controller::move_goal> ("base_controller/move_base/goal"  );
    simple_goal_c  = nh.serviceClient<base_controller::move_goal> ("base_controller/simple_move/goal");
    set_position_c = nh.serviceClient<odometry::pose_odom>        ("odometry/set_position"           );
    set_height_c   = nh.serviceClient<oms::set_height>            ("oms/set_height"                  );
    reset_height_c = nh.serviceClient<oms::reset>                 ("oms/reset"                       );
    set_gripper_c  = nh.serviceClient<oms::set_gripper>           ("oms/set_gripper"                 );
    read_order_c   = nh.serviceClient<camera::order_board>        ("camera/read_order_board"         );
    read_disp_c    = nh.serviceClient<camera::dispensary>         ("camera/dispensary/follow_cube"   );

    ros::Subscriber height_sub   = nh.subscribe("oms/height",     1, heightCallback  );
    ros::Subscriber position_sub = nh.subscribe("robot/position", 1, positionCallback);
    ros::Subscriber start_sub    = nh.subscribe("/robot/digital_in/start_button/state", 1, startCallback);


    
    ros::Duration(10).sleep();
    

    set_gripper( GRIPPER_CUBE_O );

    do{ 
        ros::spinOnce();
        ros::Duration(0.5).sleep();
    }while ( start_button );



    // Main Logic

    reset_height( 1 );

    set_gripper( GRIPPER_OPEN );

    set_position   ( 34, 34, 180 );  

    position_driver( 34, 34, 0, "simple_move" );

    position_driver( 105 + (32.8/2.0), 100, 90, "move_base" );

    // oms_driver( 20 );

    // read_order();

    // reset_height( 1 );

    char task_to_do = 'n';
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

    task_to_do = 'b';
    std::string cube(1, task_to_do);

    position_driver( 20 + (65.0/2.0), 100, 90, "simple_move" );

    oms_driver( 20 );

    read_dispensary( cube, 90 );

    ros::spinOnce();

    float shelf = (int(oms_height / 15) * 13.5) + 10.5;

    oms_driver( shelf );

    position_driver( robot_position.x, robot_position.y + 20, 90, "simple_move" );

    set_gripper( GRIPPER_CUBE_C );

    position_driver( robot_position.x, robot_position.y - 20, 90, "simple_move" );

    

    ros::shutdown();

    return 0;
};
