#import node2vec
import networkx as nx








if __name__ == '__main__':
    G = nx.read_edgelist('test.edgelist', nodetype=int, create_using=nx.DiGraph())
    for edge in G.edges():
        G[edge[0]][edge[1]]['weight'] = 1
    G = G.to_undirected()

    G = node2vec.Graph(G, False, 1, 1)
    G.preprocess_transition_probs()
    a = 1
    '''
 neighbours = [[]]
    for i in range(1, 35):
        neighbours.append([nb for nb in G.neighbors(i)])
    for i in range(1, 35):
        print(neighbours[i])    
    '''
