from utils.base import Variable
from utils.base import AgentClass


def intersection(lst1, lst2):
    return list(set(lst1) & set(lst2))


def readLine(input):
    try:
        [a, b, c] = input.readline().strip().split(';')
    except ValueError as e:
        return []

    return int(a), int(b), int(c)


def readVariables(input, nr_vars):
    vars = []
    for i in range(0, nr_vars):

        [agentId, meetingId, meetingUtil] = readLine(input)
        var = Variable(i, agentId, meetingId, meetingUtil) 
        vars.append(var)

    agents = groupByAgents(vars)

    return vars, agents   


def readPrerefence(input, agentsList):
    [agentId, _, pref] = readLine(input)
    while True:
        try:
            agentsList[agentId].addPrefSlot(pref)
            [agentId, _, pref] = readLine(input)
        except ValueError as v:
            break

    return agentsList


def buildPrefMatrixInternal(agentsList):
    i = 0
    while i < len(agentsList):
        agentsList[i].interalPrefMatrix()
        i += 1

    return agentsList

    
def groupByAgents(vars):
    agents = {}
    for v in vars:
        if v.agentId not in agents:
            agents[v.agentId] = AgentClass(v.agentId)

        agents[v.agentId].addMeeting(v.meetingId, v.utility)

    return agents