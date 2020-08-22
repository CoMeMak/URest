# URest

Python REST interface for controlling a Universal Robot



# Installation

    # Install pip dependencies
    pip3 install flask flask_restful flask_cors
    pip3 install scipy numpy
    

    # Clone repo including customized robot-driver
    git clone --recursive https://github.com/CoMeMak/URest.git


## Optional: Universal Robots Simulator


1. Go to https://www.universal-robots.com/download/ 
2. Select "e-Series > Software > Offline Simulator"
3. Follow the instructions that come with URSim



# Running Assembly


## With the simulator

First start URSim, then launch URest with:

    python3 simple.py --robot-ip=127.0.0.1


## With your robot

    python3 simple.py --robot-ip=192.168.0.100



This will launch both, the URest-server providing a rest-api, 
and the assembly frontend running in your browser. 
