% Add the SVM folder to the path
addpath('./svm');

% Load data from .mat file
load('dataset.mat');

% Randomly split the training and testing set
n = randperm(size(X, 1));
test_size = round(size(X, 1) * 0.5);
X_train = X(n(1:test_size), :);
Y_train = Y(n(1:test_size), :);
X_test  = X(n(test_size+1:end), :);
Y_test  = Y(n(test_size+1:end), :);

% Ensure X_train and X_test are row vectors (to avoid dimension mismatch)
X_train = X_train';  % Transpose to make sure columns represent features
X_test = X_test';    % Same for the test set

% Choose the kernel we want to experiment on
kernal = 'rbf'; % 'linear', 'rbf', 'poly'

% Set the sigma (or p1)
global p1;
p1 = 0.25;  % Adjust this for the RBF kernel

% Initialize performance tracking variables
c_list = [];
p1_list = [];
nsv_list = [];
alpha_list = [];
margin_list = [];
acc_list = [];

% Define C values to experiment with (logarithmic for small C, linear for larger C)
c_values = [logspace(-8, -1, 8), 2:8];  % Example range of C values

% Experiment with the value of C
for i = 1:length(c_values)
    c = c_values(i);
    
    % Call svc with three outputs: number of support vectors, alpha, and bias
    [nsv, alpha, b0] = svc(X_train', Y_train, kernal, c);  % Call svc with correct dimensions
    
    % Calculate margin: 2 / norm(w), where w is derived from the support vectors
    w = (alpha .* Y_train)' * X_train';  % Linear weight vector
    margin = 2 / norm(w);  % Calculate margin
    
    % Compute test error
    err = svcerror(X_train', Y_train, X_test', Y_test, kernal, alpha, b0);  % Pass row vectors to svcerror
    
    % Record performance metrics
    c_list = [c_list c];
    nsv_list = [nsv_list nsv];
    alpha_list = [alpha_list sum(alpha)];
    margin_list = [margin_list margin];
    acc_list = [acc_list 1 - err / length(Y_test)];
end

% Plot the results
figure('Name','rbf(sigma=0.25)')
subplot(2,2,1)
plot(1:length(c_values), nsv_list)
xticks(1:length(c_values))
xticklabels(c_list)
ylabel('# of support vectors')
title('C/NSV')

subplot(2,2,2)
plot(1:length(c_values), alpha_list)
xticks(1:length(c_values))
xticklabels(c_list)
ylabel('Sum of alphas')
title('C/Alpha')

subplot(2,2,3)
plot(1:length(c_values), margin_list)
xticks(1:length(c_values))
xticklabels(c_list)
ylabel('Margin')
title('C/Margin')

subplot(2,2,4)
plot(1:length(c_values), acc_list)
xticks(1:length(c_values))
xticklabels(c_list)
ylabel('Accuracy(%)')
title('C/Accuracy')