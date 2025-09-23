import numpy as np
import networkx as nx
from typing import Dict, Iterable, Tuple, List

def build_flow_graph(flows: Iterable[Tuple[str, str, float]]) -> nx.Graph:
    """
    Build an undirected weighted graph from (source, target, weight) flows.
    """
    G = nx.Graph()
    for u, v, w in flows:
        if G.has_edge(u, v):
            G[u][v]["weight"] += float(w)
        else:
            G.add_edge(u, v, weight=float(w))
    return G

def convergence_nodes(G: nx.Graph, top_k: int = 5) -> List[Tuple[str, float]]:
    """
    Return nodes that act as convergence hubs via weighted betweenness centrality.
    """
    bc = nx.betweenness_centrality(G, weight="weight", normalized=True)
    return sorted(bc.items(), key=lambda kv: kv[1], reverse=True)[:top_k]

def node_coherence(G: nx.Graph) -> Dict[str, float]:
    """
    Simple coherence proxy: degree centrality weighted by incident edge weights.
    """
    coh = {}
    for n in G.nodes():
        wsum = sum(G[n][nbr].get("weight", 1.0) for nbr in G.neighbors(n))
        coh[n] = wsum
    # normalize
    mx = max(coh.values()) if coh else 1.0
    return {k: v / mx for k, v in coh.items()}
