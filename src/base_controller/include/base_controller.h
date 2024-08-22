#ifndef MOVE
#define MOVE

#include <ros/ros.h>
#include <move_base_msgs/MoveBaseAction.h>
#include <actionlib/client/simple_action_client.h>

#include <tf/transform_broadcaster.h>

#include "base_controller/move_goal.h"

#include "math.h"

#include <geometry_msgs/Vector3.h>
#include <geometry_msgs/Twist.h>



static float linear_tolerance  = 2.5;  //  [cm]
static float angular_tolerance = 1;  //  [degrees]

//Robot Position
static float x_global = 0;    //Robot Global Position on the X  axis  [cm]
static float y_global = 0;    //Robot Global Position on the Y  axis  [cm]
static float th_global = 0;   //Robot Global Position on the Th axis  [degrees]

ros::Publisher cmd_vel_pub;
geometry_msgs::Quaternion odom_quat;
static const double PI = 3.14159265;

//Functions protofunctions
bool move( base_controller::move_goal::Request &req, base_controller::move_goal::Response &res );
bool simple_move( base_controller::move_goal::Request &req, base_controller::move_goal::Response &res );

geometry_msgs::Quaternion SetTheta(double theta);
double Quotient_Remainder( double x, double y );
void rotate( double & x, double & y, double phi);
void odomCallback( const geometry_msgs::Vector3::ConstPtr& msg );

#endif
