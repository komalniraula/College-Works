% Loading the dataset
load('dataset4.mat')

% Augmenting X with a column of ones for the intercept term
X_aug = [ones(size(X, 1), 1), X];

% The classification function
sigmoid = @(z) 1 ./ (1 + exp(-z));

% Defining the logistic loss function (Empirical Risk)
loss = @(theta) -mean(Y .* log(sigmoid(X_aug * theta)) + (1 - Y) .* log(1 - sigmoid(X_aug * theta)));

% Defining the gradient of the logistic loss
grad = @(theta) (1 / size(X_aug, 1)) * X_aug' * (sigmoid(X_aug * theta) - Y);

% Binary classification error function
binary_error = @(theta) mean(round(sigmoid(X_aug * theta)) ~= Y);

% Accuracy function
accuracy = @(theta) mean(round(sigmoid(X_aug * theta)) == Y);

% Defining step size (eta) and tolerance (epsilon)
eta = 1;
epsilon = 0.003;

% Initializing theta randomly
theta = randn(size(X_aug, 2), 1); 

% Arrays for storing loss, binary error, and accuracy during iterations
losses = [];
errors = [];
accuracies = [];

% Gradient descent loop
max_iter = 100000;
for iter = 1:max_iter
    gradient = grad(theta);
    theta = theta - eta * gradient;
    
    % Storing the loss, binary error, and accuracy for each iteration
    current_loss = loss(theta);
    losses = [losses; current_loss];
    
    current_error = binary_error(theta);
    errors = [errors; current_error];
    
    current_accuracy = accuracy(theta);
    accuracies = [accuracies; current_accuracy];
    
    % Checking for convergence based on the gradient's norm and tolerance
    if norm(gradient) < epsilon
        break;
    end
end

fprintf('Accuracy (Step size: %.2f, Tol: %.3f, Iter: %d, Accuracy: %.2f%%)\n', eta, epsilon, iter, current_accuracy * 100);

% Calculating the mean of the additional features (excluding the first two)
mean_additional_features = mean(X(:, 3:end), 1); % This is done because there are more than two features

% Generating a grid over the first two features
x1_range = linspace(min(X(:,1)), max(X(:,1)), 100);
x2_range = linspace(min(X(:,2)), max(X(:,2)), 100);
[x1Grid, x2Grid] = meshgrid(x1_range, x2_range);

% Flattening the grid to create input for prediction
gridPoints = [x1Grid(:), x2Grid(:)];
numGridPoints = size(gridPoints, 1);

% Creating a full feature matrix with mean values for additional features
additional_features = repmat(mean_additional_features, numGridPoints, 1);
gridX = [ones(numGridPoints, 1), gridPoints, additional_features];

% Computing the probabilities
probabilities = sigmoid(gridX * theta);

% Reshaping probabilities to match the grid
probabilityGrid = reshape(probabilities, size(x1Grid));

% Plotting the data points
figure;
hold on;
scatter(X(Y == 0, 1), X(Y == 0, 2), 'bo');
scatter(X(Y == 1, 1), X(Y == 1, 2), 'r+');

% Plotting the decision boundary (probability = 0.5)
contour(x1Grid, x2Grid, probabilityGrid, [0.5 0.5], 'k', 'LineWidth', 2);

xlabel('Feature 1');
ylabel('Feature 2');
title(sprintf('Decision Boundary (Step size: %.2f, Tol: %.3f, Iter: %d, Accuracy: %.2f%%)', eta, epsilon, iter, current_accuracy * 100));
legend('Class 0', 'Class 1', 'Decision Boundary');
hold off;

% Plotting Binary Classification Error and Logistic Loss over Iterations
figure;
subplot(2, 1, 1);
plot(errors);
xlabel('Iteration');
ylabel('Binary Classification Error');
title(sprintf('Binary Error (Step size: %.2f, Tol: %.3f, Iter: %d)', eta, epsilon, iter));

subplot(2, 1, 2);
plot(losses);
xlabel('Iteration');
ylabel('Logistic Loss (Empirical Risk)');
title(sprintf('Empirical Risk (Step size: %.2f, Tol: %.3f, Iter: %d)', eta, epsilon, iter));