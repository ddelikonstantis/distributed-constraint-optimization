import numpy as np


class Variable:
    def __init__(self, _index, _agentId, _meetingId, _utility):
        self.varId = _index
        self.label = (_index, _agentId, _meetingId)
        self.agentId = _agentId 
        self.meetingId = _meetingId
        self.utility = _utility
    
    def __str__ (self):
        return "Variable %s -> Agent Id:%d, Meeting Id:%d, Utility:%d" % (str(self.label), self.agentId, self.meetingId, self.utility) 
    
    def __repr__(self):  
        return "Variable %s -> Agent Id:%d, Meeting Id:%d, Utility:%d\n" % (str(self.label), self.agentId, self.meetingId, self.utility) 


class AgentClass:
    def __init__(self, id):
        self.id = id
        self.meetings = {}
        self.preference = []
        self.relations = {}
        self.internalMatrix = {}
        self.receivedMsgs = {}

    def interalPrefMatrix(self):
        slots = len(self.preference)
        inf = np.full((slots, slots), np.NINF)
        for id, util in self.meetings.items():
            self.internalMatrix[id] = inf
            np.fill_diagonal(inf, np.asarray(self.preference) * util)

    def addMeeting(self, meetingId, util):
        self.meetings[meetingId] = util

    def addPrefSlot(self, slot):
        self.preference.append(slot)
    
    def addReceivedMsgs(self, msg):
        for key,value in msg.items():
            [child,_] = key
            for key, value in self.relations.items():
                [c,_,m] = key
                if c == child:
                  self.relations[(c,self.id,m)] = value
                else:
                  self.receivedMsgs[(c,self.id,m)] = value


    def addRelation(self, parentId, meetingId, r):
        key = (self.id, parentId, meetingId)
        self.relations[key] = r
        print("relation->key:%s \n %s" %(key, r))


    def createHypercube(self,parent):
        hypercube = {}
        for m in self.meetings:
            relations_per_meeting = []
            
            for key, value in self.relations.items():
                [_,p,meetId] = key
                if meetId == m:
                    relations_per_meeting.append(value)

            if len(relations_per_meeting) > 0:
                hypercube[self.id, parent]  = (self.hyperCubeDry(relations_per_meeting))
                
        return hypercube


    def projection(self, cube):
        return np.max(cube, axis=0)

    def join(self, r1,r2):
        return r1[:,:, None] + r2[:, None, :]

    def hyperCubeDry(self, R):
        zeros = []
        for r in R:
            zeros.append(r)
        
        return np.asarray(zeros)


    def hyperCube(self, R):
        if len(R) < 2:
            return np.asarray(R)
        try:
            # get first relation
            r1 = R.pop()
            # get second relation
            r2 = R.pop()
            joined = r1[:,:, None] + r2[:, None, :]
            proj = self.projection(joined)
            R.append(proj)
            proj = self.hyperCube(R)
        except IndexError as index:
            print(index)

        return np.asarray(proj)
    

    def merge_two_dicts(self, x, y):
        """
        Given two dictionaries, merge them into a new dict as a shallow copy.
        """
        z = x.copy()
        z.update(y)
        
        return z

         