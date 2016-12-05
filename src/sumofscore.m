function [s]=sumofscore(G,A)
N = numnodes(G);
s=0;
for nodeId=1:N
    su1=sum(A(nodeId,:));
    su2=sum(A(:,nodeId));
    su=su1+su2;
    s=s+su;
end
end