function [pf]=Pf_of_vertice(nodeId,G,A)
    N = numnodes(G);
    su=zeros(1,N);
    for ii=1:N
        su(1,ii)=score_of_vertice(ii,G,A);
    end
    S=sum(su);
    score=score_of_vertice(nodeId,G,A);
    pf=(1-(score/S))/10;%10 SHOULD BE n-1 here, I AM NOT SURE HERE


end