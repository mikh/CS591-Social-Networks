
fprintf('Hello World!\n');

fprintf('Reading configuration...\t');
fileID = fopen('config.txt');
C = textscan(fileID, '%s');
fclose(fileID);
fprintf('Done.\n');

input_file = C{1}{1};
output_file = C{1}{2};

fprintf('Loading adjacency matrix...\t');
A_original = importdata(input_file, ' ');
fprintf('Done.\n');

fprintf('Running algorithm...\n');
LSR_weight

fileID = fopen('lock.txt', 'w');
fprintf(fileID, '0');
fclose(fileID);

exit;