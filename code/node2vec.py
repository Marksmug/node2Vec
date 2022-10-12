
import numpy as np
import random





class Graph():
    def __init__(self, G, is_directed, p ,q):
        self.G = G
        self.is_directed = is_directed
        self.p = p
        self.q = q
        self.transition_probs_nodes = []
        self.transition_probs_edges = []


    def preprocess_transition_probs(self):
        g = self.G
        is_directed = self.is_directed

        transition_probs_nodes = {}
        transition_probs_edges = {}

        for node in g.nodes():
            #sorted neighbors for indexing neighbors in the alias method
            sorted_neighbors = sorted(g.neighbors(node))
            unnormalized_probs = [g[node][nb]['weight'] for nb in sorted_neighbors]
            Z = sum(unnormalized_probs)
            normarlized_probs = [float(prob)/Z for prob in unnormalized_probs]
            transition_probs_nodes[node] = create_alias_table(normarlized_probs)

        if is_directed:
            # one direction transition probs
            for edge in g.edges():
                transition_probs_edges[edge] = self.create_alias_edge_table(edge[0], edge[1])
        else:
            # two directions transition probs
            for edge in g.edges():
                transition_probs_edges[edge] = self.create_alias_edge_table(edge[0], edge[1])
                transition_probs_edges[(edge[1], edge[0])] = self.create_alias_edge_table(edge[1], edge[0])

        self.transition_probs_nodes = transition_probs_nodes
        self.transition_probs_edges = transition_probs_edges

        return

    def create_alias_edge_table(self, src, dst):
        g = self.G
        p = self.p
        q = self.q

        # find neighbors of dst
        unnormalized_probs = []
        neighbors = sorted(g.neighbors(dst))
        for nb in neighbors:
            if nb == src:
                unnormalized_probs.append(g[dst][nb]['weight'] / p)            #pi(x) = 1/p if d_tx = 0
            elif g.has_edge(nb, src):
                unnormalized_probs.append(g[dst][nb]['weight'])                #pi(x) = 1 if d_tx = 1
            else:
                unnormalized_probs.append(g[dst][nb]['weight'] / q)            #pi(x) = 1/q if d_tx = 2
        Z = sum(unnormalized_probs)
        normarlized_probs = [float(prob)/Z for prob in unnormalized_probs]

        return create_alias_table(normarlized_probs)


    def draw_walks(self, walks_num, walk_length):
        g = self.G


        walks = []
        nodes = list(g.nodes())

        for i in range(walks_num):
            random.shuffle(nodes)
            for start_node in nodes:
                walk = self.node2vecWalk(start_node, walk_length)
                walks.append(walk)

        return walks

    def node2vecWalk(self, start_node, walk_length):

        g = self.G
        transision_probs_nodes = self.transition_probs_nodes
        transision_probs_edges = self.transition_probs_edges

        walk = []
        walk.append(start_node)

        for i in range(walk_length-1):

            cur_node = walk[i]

            # make sure the index of neighbors is the same as the alias_table
            cur_neighbors = sorted(g.neighbors(cur_node))
            if len(cur_neighbors) == 0:
                break
            else:

                # if it's srtarting node, sample from its neighbors
                if i == 0:
                    nb_index = alias_draw(transision_probs_nodes[cur_node][0], transision_probs_nodes[cur_node][1])
                    next_node = cur_neighbors[nb_index]
                    walk.append(next_node)

                # if it's not starting node, sample based on the edge between previous node and current node
                else:
                    pre_node = walk[i-1]
                    edge = (pre_node, cur_node)
                    nb_index = alias_draw(transision_probs_edges[edge][0], transision_probs_edges[edge][1])
                    next_node = cur_neighbors[nb_index]
                    walk.append(next_node)

        return walk








def create_alias_table(probs):
    '''
    create a alias table (prob and another_node) for probs
    :param probs:
    :return:probs_list, another_nb_list
    '''

    n = len(probs)
    prob_list = np.zeros(n)
    another_nb_list = np.zeros(n, dtype=int)

    small = []
    large = []

    # 1. multiply probs by n
    # 2. divided the multiplied probs into probs larger than 1 and smaller than 1
    for i, prob in enumerate(probs):
        prob_list[i] = n * prob
        if prob_list[i] >= 1:
            large.append(i)
        else:
            small.append(i)

    # 3. compensate the prob between large and small
    while len(large) > 0 and len(small) > 0:
        l_index = large.pop()
        s_index = small.pop()

        # assign prob in large to small in order to make the total prob is 1
        # the index of large prob that making the compensation is another node we choose when sampling
        another_nb_list[s_index] = l_index
        prob_list[l_index] = prob_list[l_index] - (1 - prob_list[s_index])

        if prob_list[l_index] >= 1:
            large.append(l_index)
        else:
            small.append(l_index)

    return prob_list, another_nb_list

def alias_draw(prob_list, another_nb_list):
    '''
    draw sample based on the alias table(prob, another_node)
    :param prob_list:
    :param another_nb_list:
    :return:  neighbor(node)
    '''
    n = len(prob_list)

    #choose a index of prob randomly
    i = int(np.random.random() * n)

    #generate a number between 0 to 1 randomly
    r = float(np.random.random())
    if r < float(prob_list[i]):
        return i
    else:
        return another_nb_list[i]


