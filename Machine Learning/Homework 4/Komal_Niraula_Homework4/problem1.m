load("teapots.mat")
img_height = 38;
img_width = 50;

imagesc(reshape(teapotImages(3,:),img_height,img_width));
colormap gray;
title('Original Image (3rd Image)');

%% Mean image
mean_image = mean(teapotImages, 1); % Compute mean across rows
figure;
imagesc(reshape(mean_image, img_height, img_width)); % Visualize mean image
colormap gray;
title('Mean Image');

%% Covariance matrix and eigenvectors
centered_data = teapotImages - mean_image; % Center the data by subtracting the mean
cov_matrix = (centered_data' * centered_data) / 100;
[eigenvectors, eigenvalues] = eig(cov_matrix); 

%% Top 3 eigenvectors
[eigenvalues_sorted, idx] = sort(diag(eigenvalues), 'descend'); % Sort eigenvalues and corresponding eigenvectors in descending order
eigenvectors_sorted = eigenvectors(:, idx);
top_3_eigenvectors = eigenvectors_sorted(:, 1:3);
% Visualization
figure;
for i = 1:3
    subplot(1, 3, i);
    imagesc(reshape(top_3_eigenvectors(:, i), img_height, img_width));
    colormap gray;
    title(['Eigenvector ' num2str(i)]);
end

%% Reconstruct images using PCA
projection = centered_data * top_3_eigenvectors; % Project centered data onto the top 3 eigenvectors
reconstructed_data = projection * top_3_eigenvectors' + mean_image; % Reconstruct the data

%% Compare original and reconstructed images
figure;
for i = 1:10
    % Original image
    subplot(2, 10, i);
    imagesc(reshape(teapotImages(i, :), img_height, img_width));
    colormap gray;
    title(['Original ' num2str(i)]);

    % Reconstructed image
    subplot(2, 10, i + 10);
    imagesc(reshape(reconstructed_data(i, :), img_height, img_width));
    colormap gray;
    title(['Reconstructed ' num2str(i)]);
end

%% Mean Squared Error for each image
mse_per_image = mean((teapotImages - reconstructed_data).^2, 2);

% Plot MSE
figure;
plot(1:length(mse_per_image), mse_per_image, '-o', 'LineWidth', 1.5, 'MarkerSize', 8);
title('Mean Squared Error (MSE)', 'FontSize', 14);
xlabel('Image Number', 'FontSize', 12);
ylabel('MSE', 'FontSize', 12);
grid on;
set(gca, 'XTick', 1:5:100, 'FontSize', 12); % Adjust for readability
legend('MSE per Image', 'FontSize', 12, 'Location', 'best');

%% Display original and reconstructed images for images 5 and 33
selected_images = [5, 33];

% Create a new figure for visualization
figure;

for i = 1:length(selected_images)
    % Original image
    subplot(2, length(selected_images), i);
    imagesc(reshape(teapotImages(selected_images(i), :), img_height, img_width));
    colormap gray;
    title(['Original Image no. ', num2str(selected_images(i)), ' from the dataset']);

    % Reconstructed image
    subplot(2, length(selected_images), i + length(selected_images));
    imagesc(reshape(reconstructed_data(selected_images(i), :), img_height, img_width));
    colormap gray;
    title(['Reconstructed Image ', num2str(selected_images(i)), ' from the dataset']);
end
