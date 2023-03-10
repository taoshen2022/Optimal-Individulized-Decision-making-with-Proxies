from src.models.kernel_utils import calculate_kernel_matrix_batched

######Loss function used in NMMR########
##########adopted from https://github.com/beamlab-hsph/Neural-Moment-Matching-Regression/blob/main/src/models/NMMR/NMMR_loss.py #####


def NMMR_loss(model_output, target, kernel_matrix, loss_name: str):  # batch_indices=None):
    residual = target - model_output
    n = residual.shape[0]
    K = kernel_matrix

    if loss_name == "U_stats":
        K.fill_diagonal_(0)
        loss = (residual.T @ K @ residual) / (n * (n-1))
    else:
        raise ValueError(f"{loss_name} is not valid. Must be 'U_stats'.")

    return loss[0, 0]


def NMMR_loss_batched(model_output, target, kernel_inputs, kernel, batch_size: int, loss_name: str):
    residual = target - model_output
    n = residual.shape[0]

    loss = 0
    for i in range(0, n, batch_size):
        partial_kernel_matrix = calculate_kernel_matrix_batched(kernel_inputs, (i, i+batch_size), kernel)
        if loss_name == "U_stats":
            factor = n * (n-1)
            # zero out the main diagonal of the full matrix
            for row_idx in range(partial_kernel_matrix.shape[0]):
                partial_kernel_matrix[row_idx, row_idx+i] = 0
        temp_loss = residual[i:(i+batch_size)].T @ partial_kernel_matrix @ residual / factor
        loss += temp_loss[0, 0]
    return loss


