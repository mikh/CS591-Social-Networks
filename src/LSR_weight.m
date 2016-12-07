    %%data=load('');%%ur file here
    
   % A = [0 31 41 12 2;0 0 5 61 0; 0 0 0 5 0; 0 0 0 0 1;0 0 0 0 0];%%need parse data here according to different datasets
    % A = input_adj;
    G=graph(A,'upper');
    G_original = G;
    m=10;
    s=10;
    N = numnodes(G);
    number_edge=count_edge(G);
    B=zeros(m,number_edge);%% the A in Ax=y
    y = zeros(1,m);
    for i=1:m
        G=graph(A,'upper');%% 
        
        score=zeros(1,N);
        Pf=zeros(1,N);
        
        % Find Pf for all vertices and Vc is the one with max Pf
        for ii=1:N
            score(1,ii)=score_of_vertice(ii,G,A);
            Pf(1,ii)=Pf_of_vertice(ii,G,A);
        end
        [maxx,Vc]=max(Pf);
        
        % Check all neighbors of Vc and find Pt, to get Vn
        B_edge_index=zeros(1,s);
        
        % add all weights of edges and store in y(i)
        y_sumi = 0;
        for j=1:s
             G=graph(A,'upper');
             M = neighbors(G,Vc);
             
             % DEBUG: fprintf('#%d: %d neighbors = ', i, Vc);
             % fprintf('%d,', M);
             % fprintf('\n');
             leng=length(M);
            if M~=0
                scoren=zeros(1,leng);
                %Pt=zeros(1,leng);
                for jj=1:leng
                    score1=min(1,leng/degree(G,M(jj,:)))/leng;
                    score2=neighbor_weight(Vc,G,A)/((A(Vc,M(jj,:))+A(M(jj,:),Vc))*min(1,(neighbor_weight(Vc,G,A))/(neighbor_weight(M(jj,:),G,A)) ));%%
                    scoren(:,jj)=score1*score2;
                end
                % DEBUG: fprintf('#%d: Ptansitive = ', i);
                % fprintf('%d,', Pt);
                % fprintf('\n');
                hg=sum(scoren);
                Pt=scoren./hg;
                [maxxx,Vn_id] = max(Pt);
                Vn = M(Vn_id);
                
                ei = findedge(G,Vc,Vn);
                if ei == 0
                    fprintf('FATAL: no edge in (Vc,Vc) = (%d,%d)\n', Vc, Vn);
                end
                    
                B_edge_index(1,j)=ei;  
                y_sumi = y_sumi + G.Edges.Weight(ei);
                % fprintf('#%d: (%d,%d) edge idx: %d, sum=%d\n', i, Vc, Vn, ei, y_sumi);
                
                %Vn_neigh=neighbors(G,Vn);
                A(Vc,Vn)=0;
                A(Vn,Vc)=0;
                
            else
                % For empty neigh(Vc), proceed to next node
                Vn=Vc;
            end
            % Proceed to next node
            Vc=Vn;
        end
        % fprintf('%d, ', B_edge_index); 
        % fprintf('\n');
        if any(B_edge_index == 0)
            fprintf('Nonexisting edge indices found. Skip adding to B\n');
            continue;
        end
            
        B(i,B_edge_index)=1;
        y(i) = y_sumi;
    end
B % print B
y % print y
[x,FitInfo] = lasso(B, y','Lambda',1)
% use this y and B to find x using Lasso with optimization for-
% problem: min ||x||_1 + ||Bx-y||_2^2
