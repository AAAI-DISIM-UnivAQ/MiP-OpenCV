import redis
import pexpect
import time
import math



class GattTool:
    PROMPT = '.*\[LE\]>'

    def __init__(self):
        cmd = 'gatttool -b 1C:05:B2:FA:01:47 -I'
        self.child = pexpect.sp
        self.child.expect(self.PROMPT, timeout=1)

    def connect(self):
        self.child.sendline('connect')
        time.sleep(5)
        self.child.expect(self.PROMPT, timeout=1)

    def disconnect(self):
        self.child.sendline('disconnect')
        self.child.expect(self.PROMPT, timeout=1)

    def charWriteCmd(self, byte_vals, timesleep=0):

        cmd = 'char-write-cmd 0x001b ' + str(byte_vals)
        print(cmd)
        self.child.sendline(cmd)
        time.sleep(timesleep)

    def charReadReply(self, timeout=10):

        self.child.expect(self.PROMPT, timeout)
        self.child.sendline("char-read-uuid FFE4")
        self.child.expect('handle: 0x0016 	 value:', timeout)
        returnString = self.child.readline()
        retArray = returnString.split()
        hexList = []
        for i in range(0,len(retArray)):
            hexList.append(retArray[i].decode('utf-8'))
        result = []
        for i in range(0,len(hexList)):
            result.append((chr(int(hexList[i],16))))
        resultInt = []
        for j in range(0,len(result),2):
            resultInt.append(result[j]+(result[j+1]))
        return resultInt

class MIP:

    def __init__(self, host_p, port_p=6379):
        self.direction = 90.0
        self.red = redis.Redis(host = host_p,port = port_p)
        self.gat = GattTool()
        self.gat.connect()
        self.red.delete('mip_position')
        self.red.delete('obs_position')

    def _angle(self, a, b):
        assert isinstance(a,tuple)
        assert isinstance(b,tuple)
        c = (a[0], b[1])
        i = math.sqrt( (a[0] - b[0])**2 + (a[1] - b[1]) ** 2 )
        c1 = math.sqrt( (a[0] - c[0])**2 + (a[1] - c[1]) ** 2 )
        c2 = math.sqrt( (b[0] - c[0])**2 + (b[1] - c[1]) ** 2 )
        if c1 == 0.0:
            return 90.0
        alpha = math.degrees(math.acos((i * i + c1 * c1 - c2 * c2)/(2.0 * i * c1)))
        return 90 - alpha

    def sense(self):

        #check Mip position
        mip_pos = self.red.lrange('mip_position', 0, 0)
        if len(mip_pos) > 0:
            mip_pos = mip_pos[0].decode()
            mip_pos = mip_pos[1:-1].split(',')
            mip_pos[0] = int(mip_pos[0])
            mip_pos[1] = int(mip_pos[1])  

        # mip_pos contains the position of the robot in an array of int (x,y)

        #check collision
        coll = self.red.lrange('obs_position', 0, -1)
        collisions = []
        if len(coll) > 0:

            for obj in coll:
                curr = obj.decode()[1:-1].split(',')
                curr[0] = int(curr[0])
                curr[1] = int(curr[1])
                collisions.append(curr)
            self.red.delete('obs_position')
        return (mip_pos, collisions)

    def keepInside(self,pos):
        global x
        x = False

        if(self.direction==90.0):
            if(pos[1]>=310):
                x=True
                self.act([180.0, 'back'])
        elif(self.direction==270.0):
            if (pos[1] <= 70):
                x = True
                self.act([180.0, 'back'])

        elif (self.direction == 180.0):
            if (pos[0] <= 105):
                    x = True
                    self.act([180.0,'back'])

        elif (self.direction == 0.0):
            if (pos[0] >= 430):
                x = True
                self.act([180.0,'back'])



    def think(self, pos, coll):

        if (len(pos)>0):
            self.keepInside(pos)
            if (x == False):

                if(len(coll) < 1):
                    return [0.0, '']
                else:
                    for i in range(0,len(coll)):
                        # Y Directions
                        # -- Going forward
                        if self.direction == 90.0:
                            if pos[1] > coll[i][1]:
                                print('obastacle behind HERE-1!')
                                continue
                            else: #Right or left obj
                                if  coll[i][0] in range(pos[0],pos[0]+45):
                                    print('obstacle on left')
                                    return [90.0, 'right']
                                elif coll[i][0] in range(pos[0]-45,pos[0]):
                                    print('obstacle on right')
                                    return [270.0,'left']
                                else:
                                    return [0.0, '']
                        # -- Going Backwards
                        elif self.direction == 270.0:
                            # Right or left obj
                            if pos[1] > coll[i][1]:
                                if coll[i][0] in range(pos[0],pos[0] + 45):
                                    print('obstacle on right')
                                    return [270.0,'left']
                                elif coll[i][0] in range(pos[0]-45,pos[0]) :
                                    print('obstacle on left')
                                    return [90.0,'right']
                                else:
                                    return [0.0, '']
                            else:
                                print('obstacle behind  HERE-2')
                                continue
                        # X Directions
                        # -- Going forward
                        elif self.direction == 0.0:
                            if pos[0] > coll[i][0]:
                                print('obstacle behind HERE-3')
                                continue
                            else: # Obj on Left or Right
                                if coll[i][1] in range(pos[1],pos[1]+45):
                                    print('obstacle on right')
                                    return [270.0,'left']
                                elif coll[i][1] in range(pos[1]-45,pos[1]):
                                    print('obstacle on left')
                                    return [90.0,'right']
                                else:
                                    return [0.0,'']
                        # -- Going backwards
                        elif self.direction == 180.0:
                            if pos[0] < coll[i][0]:
                                print('obstacles behind HERE-4')
                                continue
                            else: # Right or left obj
                                if coll[i][1] in range(pos[1],pos[1] + 45):
                                    print('obstacle on left')
                                    return [90.0,'right']
                                elif coll[i][1] in range(pos[1]-45,pos[1]):
                                    print('obstacle on right')
                                    return [270.0 ,'left']
                                else:
                                    return [0.0,'']
                        else:
                            return [0.0,'']

    def act(self,turning_angle):

        if(not (turning_angle == None)):
            print(self.direction)
            if turning_angle[1]== 'error':
                print('error')
                self.gat.charWriteCmd('710446') 
                time.sleep(0.7)
            if turning_angle[0] == 0.0:
                self.gat.charWriteCmd('710446')
                time.sleep(0.7)
                
            else:
                print("before")
                print(self.direction)
                self.gat.charWriteCmd('77')
                time.sleep(0.5)
                self.direction = (self.direction + turning_angle[0]) % 360
                print("after")
                print(self.direction)
                if turning_angle[1] == 'left':
                    self.gat.charWriteCmd('73' + '13' + '10')
                elif turning_angle[1] == 'right':
                    self.gat.charWriteCmd('74' + '13' + '10')
                elif turning_angle[1] == 'back':
                    self.gat.charWriteCmd('732610')
                    time.sleep(0.7)
                time.sleep(0.5)
                self.red.delete('obs_position')
        else:
            self.gat.charWriteCmd('710446')
            time.sleep(0.7)

