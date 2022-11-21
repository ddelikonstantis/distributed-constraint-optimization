import networkx as nx
import matplotlib.pyplot as plt
import utils.util as u
import utils.pseudotree as ptree
from networkx.drawing.nx_pydot import graphviz_layout
from pympler import asizeof


root_node = 0
agentsList = {}
sentMsgs = []
seenMsgs = []
value_prop_order = []
MESSAGES_SIZE = []
msgSizePerCycleCounter = 0
msgSizePerCycle = []
msgCounter = 0
msgCountPerIteration =[]
cycleCounter = 0
cyclePerLevel = []


def get_parent(T, node):
    parent = None
    pseudo_parents = []
    in_edges = list(T.in_edges(node ,data=True))
    out_edges = list(T.out_edges(node, data=True))

    for p,_,c in in_edges:
        try:
            if c['color'] == 'blue':
                pseudo_parents.append(p) 
        except KeyError as e:
            children = []
            for _,a,c in list(T.out_edges(p, data=True)):
                try:
                    if c['color'] == 'blue':
                        pass
                except KeyError as k:
                    children.append(a)  

            result = set(children).issubset(sentMsgs)
            if result:
                parent = p

    return parent, pseudo_parents


def send_util_msg(T, nodes, msgCounter, msgSizePerCycleCounter, cycleCounter):
    # compute utility from each node and parse it to parents
    # keep track of parents
    if len(nodes) == 0:
        print("root node: ", agentsList[root_node].createHypercube(-1))

        return    

    parents = []
    for node in nodes:
        sentMsgs.append(node)
        [parent, _] = get_parent(T,node)
        
        if parent != None:
            if (node,parent) not in seenMsgs:
                print("Util Message from: %d to %d" %(node,parent))
                if agentsList[node].id != node:
                    print("message sent twice")
                else:
                    MSG = agentsList[node].createHypercube(parent)
                    agentsList[parent].addReceivedMsgs(MSG)
                    MESSAGES_SIZE.append(asizeof.asizeof(MSG))
                    msgSizePerCycleCounter += asizeof.asizeof(MSG)

                seenMsgs.append((node,parent))
                msgCounter += 1
                msgCountPerIteration.append(msgCounter)
                # keep parents order for value propagation computation
                value_prop_order.append((parent,node))

            if parent not in parents:
                parents.append(parent)

        elif node != root_node:
            if node not in parents:
                msgSizePerCycle.append(msgSizePerCycleCounter)
                msgSizePerCycleCounter = 0
                cycleCounter += 1
                cyclePerLevel.append(cycleCounter)
                parents.append(node)

    send_util_msg(T,parents, msgCounter, msgSizePerCycleCounter, cycleCounter)


def send_value_msg():
    # reverse in order to use recursion in send_util_msg
    value_prop_order.reverse()
    for p in value_prop_order:
        [parent, child] = p
        print("Value Message from: %d to %d" %(parent,child))


def find_leave_nodes(TreeDfs):
    leaves = []
    for v in TreeDfs.nodes(data=True):
        out_edges = list(TreeDfs.out_edges(v[0], data=True))
        if len(out_edges) == 0:
            leaves.append(v[0])
            continue

        all_blue = True
        for _,_,color in out_edges:
            try:
                if color['color'] != 'blue':
                    all_blue = False
                    break
            except KeyError as key:
                    all_blue = False
                    break
        if all_blue:
            leaves.append(v[0])  

    return leaves    


def create_relations(TreeDfs, agentsList):
    for node in TreeDfs.nodes(data=True):
        out_edges = list(TreeDfs.out_edges(node[0], data=True))
        for parent, child, edge_color in out_edges:
            sharedMeetings = u.intersection(agentsList[parent].meetings , agentsList[child].meetings)
            for meeting in sharedMeetings:
                pMatrix = agentsList[parent].internalMatrix[meeting]
                cMatrix = agentsList[child].internalMatrix[meeting]
                agentsList[child].addRelation(parent, meeting, pMatrix + cMatrix)


def main():
    useAgents = True
    # parse file data
    inputFilename = 'data/DCOP_300'
    input = open(inputFilename, 'r')
    # get first row
    [nrAgents, nrMeetings, nrVars] = u.readLine(input)
    print("Number of agents:%d \nNumber of meetings:%d \nNumber of variables:%d" %(nrAgents, nrMeetings, nrVars))

    # read variables
    global agentsList
    varList, agentsList = u.readVariables(input, nrVars)

    # read preference
    agentsList = u.readPrerefence(input, agentsList)

    # create internal node matrix per meeting
    agentsList = u.buildPrefMatrixInternal(agentsList)

    print('-----------Variables Graph--------------')   
    graphVariables = {}
    for v in varList:
        graphVariables[v.varId] = ptree.getAllVarsWithSameMeeting(varList, v.meetingId, v.varId)
    print(graphVariables) 

    print('-----------Agents Graph--------------')   
    graphAgents = {}
    for id, attr in agentsList.items():
        graphAgents[id] = ptree.getAllAgentsWithSameMeeting(agentsList, attr.meetings, id)
    print(graphAgents)

    graph = graphVariables
    if useAgents == True:
        graph = graphAgents

    # add all edges to graph
    graph_edges = []
    for k, l in graph.items():
        for v in l:
            graph_edges.append((k,v))
    graph_edges = [list(tpl) for tpl in list(set([tuple(sorted(pair)) for pair in graph_edges]))]
    print(graph_edges)

    # create graph
    G = nx.Graph()
    
    # constraint graph
    for e in graph_edges:
        G.add_edge(*e, color = 'black')

    # visualize tree
    layout = graphviz_layout(G, prog="dot") 
    nx.draw(G, layout, with_labels=True, node_color='#efedf2', arrowsize=1)
    output = "root_"+str(root_node)+".png"
    plt.savefig(output, format="PNG")

    # create Depth-First Search tree with speficied node
    TreeDfs = nx.dfs_tree(G, root_node)

    print("----------------")
    back_edges = []
    for node, connected in graph.items():
        e = set(TreeDfs.edges([node]))
        shouldBe = []
        for con in connected:
            if (node, con) in e: continue
            if (con, node) in e: continue
            if TreeDfs.has_edge(node,con): continue
            if TreeDfs.has_edge(con,node): continue

            shouldBe.append((node, con))

        back = set(shouldBe) - e
        back_edges.append(back)

    back_edges = [item for sublist in back_edges for item in sublist]
    back_edges = [list(tpl) for tpl in list(set([tuple(sorted(pair)) for pair in back_edges]))]
    print(back_edges)
    for e in back_edges:
        TreeDfs.add_edge(*e, color = 'blue', style='dashed')

    # create relations based on tree edges
    create_relations(TreeDfs, agentsList)

    # find leaves in order to compute utility propagation
    leaves = find_leave_nodes(TreeDfs)

    edges = TreeDfs.edges.data('color', default='black')
    colors = []
    for _,_,c in edges:
        colors.append(c)

    print("Leaves are:", leaves)
    send_util_msg(TreeDfs, leaves, msgCounter, msgSizePerCycleCounter, cycleCounter)
    send_value_msg()

    # constraints is Number of edges + Inequality constraints
    EQConstraints = TreeDfs.number_of_edges()

    # iterate through every agent and count number of inequality constraints
    NEQConstraints = 0
    for id, attr in agentsList.items():
        i = len(attr.meetings) - 1
        count = 0
        while i > 0:
            count += i
            i -= 1
        NEQConstraints += count

    # get table results
    print("Number of agents:%d \nNumber of meetings:%d \nNumber of variables:%d" %(nrAgents, nrMeetings, nrVars))
    print("Total Constraints", EQConstraints+NEQConstraints)
    print("\tEquality constraints", EQConstraints)
    print("\tInequality constraints", NEQConstraints)
    print("Total number of messages:%d" %(len(msgCountPerIteration) * 2))
    print("Max message size:%d"% (max(MESSAGES_SIZE)))
    print("Cycles:%d"% (len(cyclePerLevel) * 2))



if __name__ == "__main__":
    main()