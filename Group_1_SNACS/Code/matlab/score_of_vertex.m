function [score]=score_of_vertex(nodeId,G,~, sumNeighbor)       
    deg = degree(G,nodeId);
    score=deg/(2*count_edge(G))+(sumNeighbor(nodeId)/sum(sumNeighbor));

end