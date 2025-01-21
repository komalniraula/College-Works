function [err, model, errT] = polyreg2(x, y, D, xT, yT, lambda)
%
% Finds a D-1 order polynomial fit to multivariate data with regularization
%
%    function [err, model, errT] = polyreg2(x, y, D, xT, yT, lambda)
%
% x = matrix of input scalars for training (NxM, where N is the number of examples, M is the number of features)
% y = vector of output scalars for training
% D = number of features (or terms) being fit (for multivariate input)
% xT = matrix of input scalars for testing
% yT = vector of output scalars for testing
% lambda = regularization parameter
% err = average squared loss on training with regularization
% model = vector of polynomial parameter coefficients
% errT = average squared loss on testing
%

% Adding a bias term (intercept) to the input data
xx = [ones(size(x, 1), 1), x];  % Adding a column of ones for the bias term

% Correcting the size for identity matrix I (should match the size of xx)
I = eye(size(xx, 2));  % Identity matrix of size (D+1), corresponding to bias + features
I(1, 1) = 0; % No regularization of the bias term

% Model coefficients (with regularization)
model = (xx' * xx + lambda * I) \ (xx' * y);

% Training error with regularization
err = (1 / (2 * size(x, 1))) * sum((y - xx * model) .^ 2) + (lambda / (2 * size(x, 1))) * norm(model(2:end))^2;

% Adding a bias term to the test set
xxT = [ones(size(xT, 1), 1), xT];  % Adding a column of ones for the bias term
% Calculating the test error with regularization
errT = (1 / (2 * size(xT, 1))) * sum((yT - xxT * model) .^ 2) + (lambda / (2 * size(xT, 1))) * norm(model(2:end))^2;

% Only attempt to plot if it's univariate input (i.e., x has only one feature)
if size(x, 2) == 1
    % Generating points for plotting the polynomial fit
    q = linspace(min(x), max(x), 300)';  % Creating a vector of 300 points between min(x) and max(x)
    qq = [ones(size(q, 1), 1), q];  % Including bias term for plotting
    
    % Plotting the training data and polynomial fit
    clf;
    plot(x, y, 'X');
    hold on;
    if nargin >= 5 && ~isempty(xT) && ~isempty(yT)
        plot(xT, yT, 'cO');
    end
    plot(q, qq * model, 'r');
    hold off;
end
end
