import networkx as nx
#from gensim.models import Word2Vec
import numpy as np




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
    r = np.random.random
    if r < prob_list[i]:
        return i
    else:
        return another_nb_list[i]


