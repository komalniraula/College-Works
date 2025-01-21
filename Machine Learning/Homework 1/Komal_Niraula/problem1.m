% Loading the data
load('problem1.mat');

% Checking loaded variables
whos

x(1:5)  % Printing the first 5 elements of x
y(1:5)  % Printing the first 5 elements of y

% Dividing datasets into halves 50% training, 50% testing
train_ratio = 0.5;

% Number of samples
N = length(x);

% Randomly shuffling indices
indices = randperm(N);

% Calculating the split index
split_idx = round(train_ratio * N);

% Spliting the data
x_train = x(indices(1:split_idx));
y_train = y(indices(1:split_idx));

x_test = x(indices(split_idx+1:end));
y_test = y(indices(split_idx+1:end));

% Printing the sizes of the splits
fprintf('Training set size: %d, Testing set size: %d\n', length(x_train), length(x_test));

% Defining the degrees of the polynomial (D - 1 is the degree, D = number of coefficients)
D_values = [2, 4, 6, 9, 11, 16, 21, 26];  % Different degrees of the polynomial

% Initialize arrays to store training and testing errors for each degree
train_errors = zeros(length(D_values), 1);
test_errors = zeros(length(D_values), 1);

% Looping through each D value
for i = 1:length(D_values)
    D = D_values(i);  % Current D value

    % Calculating the degree of the polynomial (D - 1)
    degree = D - 1;
    
    % A new figure for each degree of polynomial
    figure;
    
    % Calculating polynomial regression and plotting using polyreg function
    [train_err, model, test_err] = polyreg(x_train, y_train, D, x_test, y_test);
    
    % Printing the errors
    fprintf('Degree: %d, Train Error: %.4f, Test Error: %.4f\n', degree, train_err, test_err);

    % Storing the errors for the current degree
    train_errors(i) = train_err;
    test_errors(i) = test_err;

    % Setting the legend
    legend('Train data', 'Test data', 'Polynomial curve fitting', 'Location', 'Best');
    
    % Title for the current figure
    title(['Polynomial Regression (Degree = ' num2str(degree) ')']);

    xlabel('x');
    ylabel('y');
    legend('Location', 'Best');
    
    % Adding train and test errors as text within the plot
    error_text = sprintf('Train Error: %.4f\nTest Error: %.4f', train_err, test_err);
    % Adjusting the position (x_pos, y_pos) of the text as necessary
    x_pos = (min(x_train) + mean(x_train))/1.5;  % x position
    y_pos = (min(y_train) + mean(y_train))/2;  % y position
    text(x_pos, y_pos, error_text, 'FontSize', 10, 'BackgroundColor', 'white', 'EdgeColor', 'black');
end

% Step 1: Plot Training and Testing Errors across Polynomial Degrees
% Using the degree (D - 1) for x-axis
figure;
plot(D_values - 1, train_errors, '-o', 'DisplayName', 'Train Error');
hold on;
plot(D_values - 1, test_errors, '-s', 'DisplayName', 'Test Error');
xlabel('Degree of Polynomial');
ylabel('Error');
title('Training and Testing Error vs Polynomial Degree');
legend('Location', 'Best');
hold off;

% Step 2: Find the best degree with the lowest test error
[~, best_degree_idx] = min(test_errors);
best_degree = D_values(best_degree_idx) - 1;  % The corresponding best degree (D - 1)
fprintf('Best Degree: %d with Test Error: %.4f\n', best_degree, test_errors(best_degree_idx));

% Step 3: Plot f(x;θ) for the best degree
best_D = D_values(best_degree_idx);  % Get the corresponding best D (since D = degree + 1)
figure;
[train_err, model, test_err] = polyreg(x_train, y_train, best_D, x_test, y_test);
title(['Best Polynomial Fit (Degree = ' num2str(best_degree) ')']);
legend('Train data', 'Test data', 'Best Polynomial Curve', 'Location', 'Best');