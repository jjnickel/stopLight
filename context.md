# AI Vision Stoplight Control System

## Overview
An intelligent traffic light system using AI-based computer vision to analyze traffic flow, dynamically adjust light timing, store traffic patterns in a database, and enable connectivity between nearby intersections.

## Key Features
- AI vision detection of vehicles and pedestrians
- Traffic flow analysis including vehicle density and queue length
- SQLite database for logging traffic patterns and signal decisions
- Adjustable light timing based on real-time traffic data
- Communication between nearby intersections
- Admin override and monitoring dashboard

## System Architecture
1. **Traffic Camera** - captures live video
2. **AI Vision Module** - processes video to detect vehicles and extract traffic data
3. **Timing Controller** - adjusts stoplight durations based on traffic conditions
4. **SQLite Storage** - logs traffic data and decisions
5. **Interlight Communication** - shares data between nearby intersections
6. **Admin Dashboard** - allows manual control and monitoring

## Technology Stack
### Core Technologies
- **AI Vision**: YOLOv8 or OpenVINO, OpenCV, PyTorch or TensorFlow
- **Edge Computing**: NVIDIA Jetson Xavier or Orin, Google Coral
- **Programming Language**: Python
- **Data Storage**: SQLite
- **Web Dashboard**: React.js (frontend), Flask or FastAPI (backend)
- **Interlight Communication**: MQTT or WebSockets
- **Authentication**: JWT or OAuth 2.0
- **Version Control**: Git with GitHub or GitLab
- **Optional Deployment**: Docker

## Project Modules

### 1. AI Vision Module
- Receives video input from traffic cameras
- Detects vehicles and pedestrians
- Estimates queue length and vehicle direction
- Sends traffic data at regular intervals

### 2. Traffic Analyzer
- Calculates vehicle density, queue growth rate, and average wait time
- Stores results in the SQLite database

### 3. Signal Controller
- Adjusts green and red light durations dynamically
- Respects configured minimum and maximum limits
- Detects and prioritizes emergency vehicles

### 4. SQLite Logger
- Stores traffic metrics and signal control decisions
- Supports data retrieval for historical analysis and dashboard display

### 5. Interlight Communication
- Sends summarized traffic data to nearby intersections
- Receives upstream and downstream traffic conditions
- Coordinates light timing for smoother traffic flow

### 6. Admin Dashboard
- Displays live camera feed and signal status
- Provides access to historical logs
- Allows manual override of light timing
- Lets admins configure timing rules and thresholds
- Requires secure authentication

## Development Timeline

### Phase 1: Hardware Setup (1 week)
- Set up hardware, cameras, and edge devices

### Phase 2: AI Vision Implementation (2 weeks)
- Implement AI vision model with vehicle detection

### Phase 3: Core Logic (1 week)
- Build timing logic and SQLite logging module

### Phase 4: Dashboard Development (1.5 weeks)
- Develop admin dashboard UI and backend

### Phase 5: Communication (1 week)
- Add interlight communication capabilities

### Phase 6: Safety Features (1 week)
- Implement admin override and fail-safe mechanisms

### Phase 7: Testing (2 weeks)
- Test system in simulation environment

### Phase 8: Deployment (2+ weeks)
- Deploy pilot system at a test intersection

## Security and Reliability
- Secure admin login using token-based authentication
- Manual override and fail-safe in case of system failure
- Local default timers to handle AI or communication failure
- Logging of all admin and system actions

## Future Enhancements
- Reinforcement learning to improve signal timing decisions
- Predictive modeling based on time of day and traffic history
- Integration with municipal traffic control centers
- License plate recognition for analytics and enforcement