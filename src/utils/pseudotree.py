def getVarFromMeetingId(varList, tupleKey):
    res = []
    [varId, meetingId] = tupleKey
    for v in varList:
        if v.meetingId == meetingId and varId != v.varId:
            res.append(v)

    return res


def getVarFromAgentId(varList, agentId):
    agents = []
    for v in varList:
        if v.agentId == agentId:
            agents.append(v)

    return agents        


def addInequalityConstraintsEdges(vars):
    nequalConst = []
    for v in vars:
        list_found = getVarFromAgentId(vars, v.agentId)
        for item in list_found:
            nequalConst.append((v.label, item.label))

    # return unique tuples, order does not matter
    nequalConst = [list(tpl) for tpl in list(set([tuple(sorted(pair)) for pair in nequalConst]))]

    return nequalConst


def addEqualityConstraintsEdges(vars):
    equalConst = []
    for v in vars:
        list_found = getVarFromMeetingId(vars, (v.varId, v.meetingId))
        for item in list_found:
            if v.label != item.label:
                equalConst.append((v.label, item.label))

    # return unique tuples, order does not matter
    equalConst = [list(tpl) for tpl in list(set([tuple(sorted(pair)) for pair in equalConst]))]

    return equalConst


def getAllVarsWithSameMeeting(varList, meetingId, varId):
    vars = []
    for v in varList:
        if v.meetingId == meetingId and v.varId != varId:
            vars.append(v.varId)
    return vars


def intersection(lst1, lst2): 
    return list(set(lst1) & set(lst2))


def getAllAgentsWithSameMeeting(agentsList, meetings, agentId):
    agents = []
    for id, attr in agentsList.items():
        if id == agentId :
            continue
        shared = intersection(attr.meetings, meetings)
        if len(shared) >0 :
            agents.append(id)

    return agents