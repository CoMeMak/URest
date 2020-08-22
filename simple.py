import urx
import time
import logging
from urx import RobotException
from urx.robotiq_two_finger_gripper import Robotiq_Two_Finger_Gripper

from flask import Flask,request
from flask_restful import reqparse, abort, Api, Resource, inputs
from flask_cors import CORS, cross_origin

from scipy.spatial.transform import Rotation as R
import numpy as np

app = Flask(__name__)
CORS(app)

@app.route("/")
def helloWorld():
    return "Hello, cross-origin-world!"

api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('cmd', type=str)
parser.add_argument('width', type=str)
parser.add_argument('x', type=float, help='X Coordinate')
parser.add_argument('y', type=float, help='y Coordinate')
parser.add_argument('z', type=float, help='Z Coordinate')
parser.add_argument('rx', type=float, help='RX Coordinate')
parser.add_argument('ry', type=float, help='RY Coordinate')
parser.add_argument('rz', type=float, help='RZ Coordinate')
parser.add_argument('vel', type=float, help='Velocity')
parser.add_argument('acc', type=float, help='Acceleration')
    
rob = urx.Robot("127.0.0.1")
robotiqgrip = Robotiq_Two_Finger_Gripper(rob)

class Robot(Resource):
    def get(self):
        pose = rob.getl()
        # print("robot tcp is at: ", pose)
        xyz = rob.get_pos()
        orient = rob.get_orientation()
        #print("robot orient is at: ", orient)
        
        r = R.from_rotvec(np.array([pose[3],pose[4],pose[5]]))
        rpy = r.as_euler('XYZ',degrees=True)
        
        print("rpy: ", rpy)
        
        #return {'x': pose[0] * 1000, 'y': pose[1]  * 1000, 'z':pose[2]  * 1000, 'rx': pose[3] * 57.2958, 'ry': pose[4] * 57.2958, 'rz': pose[5] * 57.2958}
        return {'x': pose[0] * 1000, 'y': pose[1]  * 1000, 'z':pose[2]  * 1000, 'rx': rpy[0], 'ry': rpy[1], 'rz': rpy[2]}

    def post(self):
        args = parser.parse_args()
        cmd = args['cmd']
        print("received command: ", cmd)
        try: 
            if (cmd == "movel") or (cmd == "movej"):
                pose = rob.getl()
                pose[0] = args['x'] / 1000
                pose[1] = args['y'] / 1000
                pose[2] = args['z'] / 1000
                rx = args['rx']
                ry = args['ry']
                rz = args['rz']
                acc = args['acc']
                vel = args['vel']
            
                r = R.from_euler('XYZ',np.array([rx,ry,rz]),degrees=True)
                rv = r.as_rotvec()        
            
                #rob = urx.Robot("192.168.50.110")
                #rob.set_pos((target_x,target_y,target_z), acc=0.3, vel=0.01)
                #rob.movej((x,y,z,rx,ry,rz), acc, vel)
            
                print("rv: ", rv)
            
                pose[3] = rv[0]
                pose[4] = rv[1]
                pose[5] = rv[2]
            
                if cmd == "movel":
                    rob.movel(pose, acc, vel)
                else:
                    # rob.movej would move in joint space
                    # rob.movej(pose, acc, vel)
                    rob.movex("movej", pose, acc, vel)
            
            if cmd == "close_gripper":
                robotiqgrip.close_gripper()
        
            if cmd == "open_gripper":
                robotiqgrip.open_gripper()
        
            if cmd == "gripper_action":
                width = args['width'];
                robotiqgrip.gripper_action(width)
        
            if cmd == "stop": 
                rob.stop()
                
            return {'status':'OK'}, 201
                
        except RobotException as ex:
            return {'status':'ERROR','message':str(ex)}, 201

##
## Actually setup the Api resource routing here
##
## cd C:\Users\tionescu\Documents\UR5\git\python-urx\examples
api.add_resource(Robot, '/robot')


class Freedrive(Resource): 
    def get(self):
        #use this to print all the mess :D 
        #attrs = vars(rob.secmon)
        #print(', '.join("%s: %s" % item for item in attrs.items()))
        fd = rob.secmon._dict["RobotModeData"]["controlMode"] == 1
        return {'freedrive': fd}
        
    def post(self):
        fd = request.args.get('enable', default = False, type = inputs.boolean)
        print("fd="+str(fd))
        print(str(request.args))
        try: 
            rob.set_freedrive(fd,1000000) # default timeout is 60s, we want basically infinity
            return {'status':'OK'}
        except RobotException as ex:
            return {'status':'ERROR','message':str(ex)}, 201

        
api.add_resource(Freedrive, '/freedrive')


# Allow files from the static directory to be served directly
@app.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('static', path)



if __name__ == '__main__':
    logging.basicConfig(level=logging.WARN)
    app.run(port=5001,debug=False)

    
"""    

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)

    rob = urx.Robot("192.168.50.110")
    #rob = urx.Robot("localhost")
    rob.set_tcp((0,0,0,0,0,0))
    rob.set_payload(0.5, (0,0,0))
    try:
        l = 0.05
        v = 0.08
        a = 0.3
        pose = rob.getl()
        xyz = rob.get_pos()
        print("robot tcp is at: ", pose)
        print("robot xyz is at: ", xyz)
        print("absolute move in base coordinate ")
        pose[2] += 0
        rob.movel(pose, acc=a, vel=v)
        rob.set_pos((0.4,0.0,0.40), acc=a, vel=v)
        print("relative move in base coordinate ")
        rob.translate((0.1, 0, 0.01), acc=a, vel=v)
        rob.translate((-0.1, 0, -0.01), acc=a, vel=v)
        time.sleep(1)
        print("relative move back and forth in tool coordinate")
        rob.translate_tool((0, 0, -l), acc=a, vel=v)
        rob.translate_tool((0, 0, l), acc=a, vel=v)
        robotiqgrip = Robotiq_Two_Finger_Gripper(rob)
        robotiqgrip.close_gripper()
        robotiqgrip.open_gripper()
        robotiqgrip.gripper_action(100)
    finally:
        rob.close()


		
"""