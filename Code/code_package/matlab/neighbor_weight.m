function[su]=neighbor_weight(nodeId,G,A)
su1=sum(A(nodeId,:));
su2=sum(A(:,nodeId));
su=su1+su2;
end