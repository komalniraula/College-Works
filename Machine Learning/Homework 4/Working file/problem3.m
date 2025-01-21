%% Parameters for two Gaussian distributions
mean1 = [2, 2];
cov1 = [1, 0.5; 0.5, 1]; % Covariance for Class 1 (Σ1)

mean2 = [5, 5];
cov2 = [2, -0.5; -0.5, 1]; % Covariance for Class 2 (Σ2)

%% Grid points for visualization
x = linspace(-2, 8, 500);
y = linspace(-2, 8, 500);
[X, Y] = meshgrid(x, y);
pos = [X(:), Y(:)];

%% Gaussian probability densities
Z1 = mvnpdf(pos, mean1, cov1);
Z2 = mvnpdf(pos, mean2, cov2);
Z1 = reshape(Z1, length(y), length(x));
Z2 = reshape(Z2, length(y), length(x));

%% Decision boundary (difference of log probabilities = 0)
Z_diff = log(Z1) - log(Z2);

%% Plotting
figure;
hold on;

contour(X, Y, Z1, 5, 'LineColor', 'b', 'LineStyle', '--'); % Contours for Class 1

contour(X, Y, Z2, 5, 'LineColor', 'r', 'LineStyle', '--'); % Contours for Class 2

contour(X, Y, Z_diff, [0 0], 'LineColor', 'g', 'LineWidth', 2); % Decision Boundary

% Scatter plot of means
scatter(mean1(1), mean1(2), 100, 'b', 'filled');
scatter(mean2(1), mean2(2), 100, 'r', 'filled');

% Labels and legend
title('Decision Boundary and Gaussian Distributions');
xlabel('X-axis');
ylabel('Y-axis');
legend({'Class 1 Gaussian', 'Class 2 Gaussian', 'Decision Boundary'}, 'Location', 'best');
grid on;
hold off;
