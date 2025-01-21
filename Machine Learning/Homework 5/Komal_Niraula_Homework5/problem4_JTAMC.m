function [marginals] = problem4_JTAMC(psis)
    % Number of variables
    n = length(psis) + 1;
    
    % Initialize forward and backward messages
    m_forward = cell(n, 1);
    m_backward = cell(n, 1);
    marginals = cell(n-1, 1);
    
    % Forward message passing
    m_forward{1} = ones(2, 1);
    for i = 1:n-1
        m_forward{i+1} = zeros(2, 1);
        for x_next = 1:2
            m_forward{i+1}(x_next) = sum(psis{i}(:, x_next) .* m_forward{i});
        end
    end
    
    % Backward message passing
    m_backward{n} = ones(2, 1);
    for i = n-1:-1:1
        m_backward{i} = zeros(2, 1);
        for x_prev = 1:2
            m_backward{i}(x_prev) = sum(psis{i}(x_prev, :)' .* m_backward{i+1});
        end
    end
    
    % Compute pairwise marginals
    for i = 1:n-1
        marginals{i} = zeros(2, 2);
        for x_i = 1:2
            for x_j = 1:2
                marginals{i}(x_i, x_j) = psis{i}(x_i, x_j) * m_forward{i}(x_i) * m_backward{i+1}(x_j);
            end
        end
        % Normalize the marginal
        marginals{i} = marginals{i} / sum(marginals{i}(:));
    end
end
