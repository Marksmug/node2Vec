import node2vec
import networkx as nx
from gensim.models import Word2Vec








if __name__ == '__main__':

    # read undirected and unweighted graph
    G = nx.read_edgelist('test.edgelist', nodetype=int, create_using=nx.DiGraph())
    for edge in G.edges():
        G[edge[0]][edge[1]]['weight'] = 1
    G = G.to_undirected()

    # learn embedings
    G = node2vec.Graph(G, False, 10, 10)
    G.preprocess_transition_probs()
    walks = G.draw_walks(10, 80)
    walks = [map(str, walk) for walk in walks]
    model = Word2Vec(walks, vector_size=128, window=10, min_count=0, sg=1,
                     workers=8, epochs=1)
    model.wv.save_word2vec_format('test_output.txt')


