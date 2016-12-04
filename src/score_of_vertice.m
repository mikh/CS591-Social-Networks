function [score]=score_of_vertice(nodeId,G,A)
su1=sum(A(nodeId,:));
su2=sum(A(:,nodeId));
su=su1+su2;
deg = degree(G,nodeId);
score=deg/(2*count_edge(G))+(su/sumofscore(G,A));

end