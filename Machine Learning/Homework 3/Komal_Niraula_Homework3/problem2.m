% Add folder path for svm
addpath('./svm')

% Load the dataset
load('dataset.mat');

% Split half dataset into training and half into testing sets
numSamples = size(X, 1);
trainSize = round(numSamples / 2);
randomIndices = randperm(numSamples);
trainIndices = randomIndices(1:trainSize);
testIndices = randomIndices(trainSize+1:end);
trainX = X(trainIndices, :);
trainY = Y(trainIndices);
testX = X(testIndices, :);
testY = Y(testIndices, :);

% Converting 0 labels to -1 for both training and testing sets
trainY(trainY == 0) = -1;
testY(testY == 0) = -1;

unique(trainY)
unique(testY)

% Parameters
C_values = [0.1, 1, 10];           % Regularization parameter
poly_orders = [1, 2, 3, 4, 5];      % Polynomial orders
sigma_values = [0.5, 1, 2, 5];      % Sigma values

% Function for computing accuracy
compute_accuracy = @(pred, actual) sum(pred == actual) / length(actual) * 100;

% Looping through different kernels and parameters
for C = C_values
    
    % Linear kernel
    fprintf('Training with linear kernel and C = %f\n', C);
    [nsv, alpha, b0] = svc(trainX, trainY, 'linear', C);
    predictions = svm_predict(testX, trainX, trainY, alpha, b0, 'linear');
    accuracy = compute_accuracy(predictions, testY);
    
    % Correct and incorrect predictions
    correct = predictions == testY;
    incorrect = ~correct;
    
    % Plot and save figure for linear kernel
    figure;
    scatter(find(correct), predictions(correct), 'filled', 'b');  % Blue for correct predictions
    hold on;
    scatter(find(incorrect), predictions(incorrect), 'filled', 'r');  % Red for incorrect predictions
    
    x_center = mean(xlim);  
    y_center = mean(ylim); 
    text(x_center, y_center, sprintf('Accuracy: %.2f%%', accuracy), 'HorizontalAlignment', 'center', 'FontSize', 12, 'BackgroundColor', 'white');
    
    title(sprintf('Linear Kernel with C = %f', C));
    xlabel('Test Sample');
    ylabel('Prediction');
    legend('Correct Predictions', 'Incorrect Predictions');
    hold off;
    print('-depsc', fullfile('output_figure/linear_kernel', sprintf('Linear_kernel_C_%f.eps', C)));
        
    % Polynomial kernel
    for order = poly_orders
        fprintf('Training with polynomial kernel (order = %d) and C = %f\n', order, C);
        kernel = sprintf('poly %d', order);
        [nsv, alpha, b0] = svc(trainX, trainY, kernel, C);
        predictions = svm_predict(testX, trainX, trainY, alpha, b0, kernel);
        accuracy = compute_accuracy(predictions, testY);

        % Correct and incorrect predictions
        correct = predictions == testY;
        incorrect = ~correct;
        
        % Plot and save figure for polynomial kernel
        figure;
        scatter(find(correct), predictions(correct), 'filled', 'b');  % Correct in blue
        hold on;
        scatter(find(incorrect), predictions(incorrect), 'filled', 'r');  % Incorrect in red
        
        x_center = mean(xlim);
        y_center = mean(ylim);
        text(x_center, y_center, sprintf('Accuracy: %.2f%%', accuracy), 'HorizontalAlignment', 'center', 'FontSize', 12, 'BackgroundColor', 'white');

        title(sprintf('Polynomial Kernel (order %d) with C = %f', order, C));
        xlabel('Test Sample');
        ylabel('Prediction');
        legend('Correct Predictions', 'Incorrect Predictions');
        hold off;
        print('-depsc', fullfile('output_figure/polynomial_kernel', sprintf('Poly_kernel_order_%d_C_%f.eps', order, C)));    
    end

    % RBF kernel
    for sigma = sigma_values
        fprintf('Training with RBF kernel (sigma = %f) and C = %f\n', sigma, C);
        kernel = sprintf('rbf %f', sigma);
        [nsv, alpha, b0] = svc(trainX, trainY, kernel, C);
        predictions = svm_predict(testX, trainX, trainY, alpha, b0, kernel);
        accuracy = compute_accuracy(predictions, testY);
    
        % Correct and incorrect predictions
        correct = predictions == testY;
        incorrect = ~correct;
        
        % Plot and save figure for RBF kernel
        figure;
        scatter(find(correct), predictions(correct), 'filled', 'b');  % Correct in blue
        hold on;
        scatter(find(incorrect), predictions(incorrect), 'filled', 'r');  % Incorrect in red
        
        x_center = mean(xlim);
        y_center = mean(ylim);
        text(x_center, y_center, sprintf('Accuracy: %.2f%%', accuracy), 'HorizontalAlignment', 'center', 'FontSize', 12, 'BackgroundColor', 'white');

        title(sprintf('RBF Kernel (sigma = %f) with C = %f', sigma, C));
        xlabel('Test Sample');
        ylabel('Prediction');
        legend('Correct Predictions', 'Incorrect Predictions');
        hold off;
        print('-depsc', fullfile('output_figure/rbf_kernel', sprintf('RBF_kernel_sigma_%f_C_%f.eps', sigma, C)));
    end
end

% Function to make predictions
function predictions = svm_predict(testX, trainX, trainY, alpha, b0, kernel)
    numTest = size(testX, 1);
    numTrain = size(trainX, 1);
    predictions = zeros(numTest, 1);

    for i = 1:numTest
        % Calculating the decision value
        decision_value = 0;
        for j = 1:numTrain
            decision_value = decision_value + alpha(j) * trainY(j) * svkernel(kernel, testX(i, :), trainX(j, :));
        end
        decision_value = decision_value + b0;

        % Predicting the class
        if decision_value >= 0
            predictions(i) = 1;
        else
            predictions(i) = -1;
        end
    end
end
