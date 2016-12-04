    %%data=load('');%%ur file here
    
    A = [0 3 4 12 2;0 0 5 61 0; 0 0 0 4 0; 0 0 0 0 1;0 0 0 0 0];%%need parse data here according to different datasets
    G=graph(A,'upper');
    m=2;
    s=2;
    N = numnodes(G);
    number_edge=count_edge(G);
    B=zeros(m,number_edge);%% the A in Ax=y
    for i=1:m
        G=graph(A,'upper');%% 
        
        score=zeros(1,N);
        Pf=zeros(1,N);
        for ii=1:N
            score(1,ii)=score_of_vertice(ii,G,A);
            Pf(1,ii)=Pf_of_vertice(ii,G,A);
            
            
        end
        [maxx,Vc]=max(Pf);
        B_edge_index=zeros(1,s);
        for j=1:s
             G=graph(A,'upper');
             M = neighbors(G,Vc);
             leng=length(M);
             
            
            if M~=0
                scoren=zeros(1,leng);
                Pt=zeros(1,leng);
                for jj=1:leng
                    score1=min(1,leng/degree(G,M(jj,:)))/leng;
                    score2=neighbor_weight(Vc,G,A)/((A(Vc,M(jj,:))+A(M(jj,:),Vc))*min(1,(neighbor_weight(Vc,G,A))/(neighbor_weight(M(jj,:),G,A)) ));%%
                    scoren(:,jj)=score1*score2;
                    
                    
                end
                hg=sum(scoren);
                Pt=scoren./hg;
                [maxxx,Vn] = max(Pt);
                Vn_neigh=neighbors(G,Vn);
                A(Vc,Vn)=0;
                A(Vn,Vc)=0;
                ei = findedge(G,Vc,Vn);
                B_edge_index(1,j)=ei;
               
                
                
                
                
                
                    
                
            else
                Vn=Vc;%%not exactly sure the syntax here
                
                
                
            end
            Vc=Vn;%not exactly sure the syntax here
        end%%add measurement matrix here, where i got stuck
        
        B(i,B_edge_index)=1;
        
    
        
    end

