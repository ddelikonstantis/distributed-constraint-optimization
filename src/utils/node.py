import numpy as np
import utils.base as u


class NodeAttributes:
    def __init__(self, _id, _meetings, _preference):
        self.id = _id
        self.meetings = _meetings
        self.preference = _preference 
        self.util_msgs = {}
        self.relations = {}
        self.join = np.zeros((u.TIME_SLOTS, u.TIME_SLOTS))

    def addRelation(self, relation):
        self.relations[relation['withParentId']] = relation
    
    def addUtilMsg(self, msg):
        self.util_msgs[msg['meetingId']] = msg

    def joinUtilMsgs(self):
        for i in range(0, u.TIME_SLOTS):
            for j in range(0, u.TIME_SLOTS):
                sum = 0
                for [_, dict] in self.util_msgs.items():
                    sum += dict['util'][i]

                self.join[i][j] = sum


    def printNode(self):
        info = {'id': self.id, 
                    'relations': self.relations,
                    'msgs': self.util_msgs }
        try:
            maxU=np.max(self.util_msgs[0]['util'])
            choice=np.where(self.util_msgs[0]['util']==maxU)
            choice=choice[0][0]
            print('--------------------------------------------------------------------------------------')
            print("Node " + str(self.id) + " choice is " + u.SLOTS[choice])
        except KeyError as e:
            pass