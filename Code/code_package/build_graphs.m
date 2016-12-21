path = 'data\modules\reddit_crawler\results.txt';
A = importdata(path, '\t');


%sparse_node/node vs. num edges
p = 'data\modules\reddit_crawler\charts\sparse_node_vs_edges.png';
sn_n = A(:, 3)./A(:, 2);
E = A(:, 4);
f = figure();
scatter(E, sn_n);
title('Sparse node percentage vs. Edges');
saveas(f, p);

%sparse edges vs edges
p = 'data\modules\reddit_crawler\charts\sparse_edges_vs_edges.png';
se = A(:, 7);
E = A(:, 4);
f = figure();
scatter(E, se);
title('Sparse Edges vs. Edges');
saveas(f, p);

%sparse cross edges vs edges
p = 'data\modules\reddit_crawler\charts\sparse_cross_intra_edges_vs_edges.png';
sc = A(:, 9);
si = A(:, 8);
E = A(:, 4);
f = figure();
hold on
scatter(E, sc, 'b');
scatter(E, si, 'r');
hold off
title('Sparse Cross and Intra Edges vs. Edges');
saveas(f, p);