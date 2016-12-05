
function [A]=LSR_weighted(G,m,s)
    N = numnodes(G);
    number_edge=count_edge(G);
    for i=1:m
        
        score=zeros(1,N);
        Pf=zeros(1,N);
        for ii=1:N
            score(:,nodeId)=score_of_vertice(nodeId);
            Pf(:,nodeId)=Pf_of_vertice(nodeId);
            
            
        end
        [maxx,Vc]=max(Pf);
        for j=1:s
            M = neighbors(G,Vc);
            leng=length(M);
            if M~=0
                for jj=1:leng
                    score1=min(1,leng/degree(G,M(jj,:)))/leng;
                    score2=G(Vc,:) ;%%
                    
                end
                
            else
            end
        end
    
        
    end

end