function [su, pf]=Pf_of_vertex(nodeId,G,A)
    N = numnodes(G);
    
    sumNeighbor = zeros(1,N);
    for ii=1:N
        M = neighbors(G, ii);
        for jj=1:length(M)
            sumNeighbor(ii) = sumNeighbor(ii) + A(ii, M(jj));
        end
    end
    
    su=zeros(1,N);
    
    for ii=1:N
        su(1,ii)=score_of_vertex(ii, G, A, sumNeighbor);
    end
    S=sum(su);
    score=su(nodeId);
    % fprintf('%d: sum=%f, score = %f,', nodeId, S, score);
    pf=(1-(score/S))*(1/(N-1));
    %if nodeId == 101
        % fprintf('%d: sum=%f, score = %f,', nodeId, S, score);
        % fprintf('Pf=%f\n', pf);    
    %end
end