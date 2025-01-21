% Main function
n = 5; % Number of variables
psis = cell(n-1, 1); % Initialize potentials

% Define the given potentials
psis{1} = [0.1, 0.7; 0.8, 0.3];
psis{2} = [0.5, 0.1; 0.1, 0.5];
psis{3} = [0.1, 0.5; 0.5, 0.1];
psis{4} = [0.9, 0.3; 0.1, 0.3];

% Compute marginals using JTA
[marginals] = problem4_JTAMC(psis);

% Display results
disp('Pairwise Marginals and Sums:');
for i = 1:length(marginals)
    fprintf('Marginal %d:\n', i);
    disp(marginals{i});
    
    % Compute and display row sums
    rowSums = sum(marginals{i}, 2);
    fprintf('Row sums for Marginal %d: [%.4f, %.4f]\n', i, rowSums(1), rowSums(2));
    
    % Compute and display column sums
    colSums = sum(marginals{i}, 1);
    fprintf('Column sums for Marginal %d: [%.4f, %.4f]\n', i, colSums(1), colSums(2));
    
    % Compute and display total sum
    totalSum = sum(marginals{i}(:));
    fprintf('Total sum for Marginal %d: %.4f\n\n', i, totalSum);
end