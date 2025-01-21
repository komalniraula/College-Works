% Loading the dataset
load('problem2.mat'); 

% Degree of polynomial + 1 (for example, D=4 for a cubic polynomial)
D = size(x, 2);  % Number of features in the dataset

% Setting lambda values (100 values between 0 and 1000)
lambdas = linspace(0, 1000, 100);

% Splitting the data into two folds for cross-validation
N = length(y);  % Number of data points
half = floor(N / 2);  % Split the data in half

% First fold
x_train1 = x(1:half, :);
y_train1 = y(1:half);
x_test1 = x(half+1:end, :);
y_test1 = y(half+1:end);

% Second fold (swapped)
x_train2 = x(half+1:end, :);
y_train2 = y(half+1:end);
x_test2 = x(1:half, :);
y_test2 = y(1:half);

% Initializing arrays to store training and test errors
train_errors = zeros(length(lambdas), 1);
test_errors = zeros(length(lambdas), 1);

% Start looping over each lambda value
for i = 1:length(lambdas)
    lambda = lambdas(i);
    
    % Train and test on first fold
    [err_train1, ~, err_test1] = polyreg2(x_train1, y_train1, D, x_test1, y_test1, lambda);
    
    % Train and test on second fold
    [err_train2, ~, err_test2] = polyreg2(x_train2, y_train2, D, x_test2, y_test2, lambda);
    
    % Average the errors across the two folds
    train_errors(i) = (err_train1 + err_train2) / 2;
    test_errors(i) = (err_test1 + err_test2) / 2;
end

% Finding the lambda that minimizes test error
[~, best_idx] = min(test_errors);
best_lambda = lambdas(best_idx);

% Calculating the differences between consecutive test errors
differences = abs(diff(test_errors));

% Setting a small threshold to detect convergence
threshold = 0.1;

% Finding the index where the change in test error is below the threshold
convergence_idx = find(differences < threshold, 1);

% Getting the corresponding lambda value and test error at the convergence point
convergence_lambda = lambdas(convergence_idx);
convergence_test_error = test_errors(convergence_idx);
fprintf('Convergence found at lambda = %.2f with test error = %.4f\n', convergence_lambda, convergence_test_error);

% Plotting the training and test errors against lambda values
figure;
plot(lambdas, train_errors, '-o', 'DisplayName', 'Training Error');
hold on;
plot(lambdas, test_errors, '-x', 'DisplayName', 'Testing Error');
xlabel('Lambda');
ylabel('Error');
title('Training and Test Errors vs Lambda');
legend;

% Mark the best lambda (that minimizes test error) on the plot
plot(lambdas(best_idx), test_errors(best_idx), 'ro', 'MarkerSize', 10, 'LineWidth', 2, 'DisplayName', 'Best Lambda');

% Mark the convergence lambda on the plot (if found)
plot(lambdas(convergence_idx), test_errors(convergence_idx), 'go', 'MarkerSize', 10, 'LineWidth', 2, 'DisplayName', 'Convergence Point');
text(lambdas(convergence_idx), test_errors(convergence_idx), sprintf(' \\lambda = %.2f', convergence_lambda), 'VerticalAlignment', 'bottom', 'HorizontalAlignment', 'right');
hold off;

% Printing the best lambda value
disp(['The best lambda is: ', num2str(best_lambda)]);