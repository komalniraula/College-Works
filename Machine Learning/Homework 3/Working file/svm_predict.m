function predictions = svm_predict(X_test, X_train, Y_train, alpha, b0, kernel, kernel_options)
    % Compute the kernel matrix between test data and training data
    n_test = size(X_test, 1);
    K = zeros(n_test, size(X_train, 1));
    
    for i = 1:n_test
        for j = 1:size(X_train, 1)
            K(i,j) = Y_train(j) * svkernel(kernel, X_test(i,:), X_train(j,:), kernel_options);
        end
    end
    
    % Decision function
    decision_values = K * alpha + b0;
    predictions = sign(decision_values);
end
