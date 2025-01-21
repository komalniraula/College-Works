% Loading the dataset
data = load('data3.mat');

% whos

matrix = data.data;     % Accessing the data inside the structure

X = matrix(:, 1:2);     % X stores features
y = matrix(:, 3);       % Y stores labels

% Initializing parameters
[num_samples, num_features] = size(X);
w = rand(num_features, 1);          % Random weight initialization
initial_bias = 0;                   % Initialized bias value (changed manually for each experiment)
b = initial_bias;                   % the b is supposed to be final learned bias. It will be updated later
learning_rate = 0.01;               % Learning rate (changed manually for each experiment)
max_iter = 100;                     % Maximum number of iterations
convergence_threshold = 1e-300;     % Threshold for detecting convergence

binary_errors = zeros(max_iter, 1);     % Array to store the error rate per iteration
perceptron_errors = zeros(max_iter, 1); % Array to store perceptron error

convergence_point = max_iter;  % Initializing the convergence point to max iterations (This will be updated if the following program finds convergence point before maximum interation)

% Stochastic Gradient Descent (SGD)
for epoch = 1:max_iter
    % Shuffling the data for each epoch
    indices = randperm(num_samples);
    X = X(indices, :);
    y = y(indices);
    
    for i = 1:num_samples
        % Computing the perceptron output (linear combination of weights and features)
        y_pred = sign(w' * X(i, :)' + b);
        
        % Updating weights and bias if there is a misclassification
        if y_pred ~= y(i)
            w = w + learning_rate * y(i) * X(i, :)';
            b = b + learning_rate * y(i);
        end
    end
    
    % Computing the binary classification error for this epoch
    predictions = sign(X * w + b);                          % Predictions for the entire dataset
    binary_errors(epoch) = mean(predictions ~= y);          % Misclassification rate
    
    % Computing the perceptron Error for this epoch
    margins = y .* (X * w + b);                             % Margin for each sample
    perceptron_errors(epoch) = -sum(margins(margins < 0));  % Summing negative margins
    
    % Detecting convergence and updating the convergence_point
    if epoch > 1 && abs(binary_errors(epoch) - binary_errors(epoch - 1)) < convergence_threshold
        convergence_point = epoch;  % Update the convergence point to the current epoch
        break;  % Stop further iterations after convergence is detected
    end
end

% Plotting Decision Boundary
figure;
hold on;
scatter(X(y == 1, 1), X(y == 1, 2), 'bo');      % Class 1 points
scatter(X(y == -1, 1), X(y == -1, 2), 'ro');    % Class -1 points
% Drawing the line of decision boundary
x_vals = linspace(min(X(:,1)), max(X(:,1)), 100);
y_vals = -(w(1) * x_vals + b) / w(2);
plot(x_vals, y_vals, 'k-', 'LineWidth', 2);     % Decision boundary

title(sprintf('Decision Boundary when bias: %.2f and learning rate: %.2f', b, learning_rate));
xlabel('Feature 1');
ylabel('Feature 2');
legend('Class 1', 'Class -1', 'Decision Boundary');
hold off;

% Let's see/review final weights and bias
fprintf('Final weights:\n');
disp(w);
fprintf('Initialized bias: %.4f\n', initial_bias);
fprintf('Final bias: %.4f\n', b);
fprintf('Learning rate: %.4f\n', learning_rate);

% Plotting Errors (Binary Classification Error and Perceptron Error)
figure;

figg = convergence_point + 5;
% Subplot 1: Binary Classification Error
subplot(2, 1, 1);  % 2 rows, 1 column, 1st plot
plot(1:figg, binary_errors(1:figg), 'b-', 'LineWidth', 2);
hold on;
plot(convergence_point, binary_errors(convergence_point), 'ro', 'MarkerSize', 10, 'LineWidth', 2);  % Mark the convergence point
% Adding text for Biases and Learning Rate in the first subplot
text(6, max(binary_errors) - 0.05, ['Initialized Bias: ', num2str(initial_bias)], 'FontSize', 10, 'Color', 'b');
text(6, max(binary_errors) - 0.15, ['Final Bias: ', num2str(b)], 'FontSize', 10, 'Color', 'b');
text(6, max(binary_errors) - 0.25, ['Learning Rate: ', num2str(learning_rate)], 'FontSize', 10, 'Color', 'b');
title('Binary Classification Error Over Iterations');
xlabel('Iterations');
ylabel('Binary Error Rate');
legend('Error', 'Convergence Point');
hold off;

% Subplot 2: Perceptron Error
subplot(2, 1, 2);  % 2 rows, 1 column, 2nd plot
plot(1:figg, perceptron_errors(1:figg), 'g', 'LineWidth', 2);
hold on;
plot(convergence_point, perceptron_errors(convergence_point), 'ro', 'MarkerSize', 10, 'LineWidth', 2);  % Mark the convergence point
% Adding text for Bias and Learning Rate in the second subplot
text(6, max(perceptron_errors) - 2, ['Initialized Bias: ', num2str(initial_bias)], 'FontSize', 10, 'Color', 'r');
text(6, max(perceptron_errors) - 5, ['Final Bias: ', num2str(b)], 'FontSize', 10, 'Color', 'r');
text(6, max(perceptron_errors) - 8, ['Learning Rate: ', num2str(learning_rate)], 'FontSize', 10, 'Color', 'r');
title('Perceptron Error Over Iterations');
xlabel('Iterations');
ylabel('Perceptron Error');
legend('Error', 'Convergence Point');
hold off;
