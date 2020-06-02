from itertools import product

import numpy as np
import nevergrad as ng


def n_dim_inf_generator(n=1):
    """Iterates in n-dimensional box from 0 to 1 in each dimension.

    Perform sort of exhaustive search with steps decreasing as power of 2"""
    for idx in product(*[[0, 1]]*n):
        yield np.array(idx)

    power = 1
    while True:
        k = 2**power
        one_d_vals = np.linspace(0, 1, k+1)
        for idxs in product(*[range(k+1)]*n):
            if all(not i % 2 for i in idxs):
                continue
            yield one_d_vals[list(idxs)]
        power += 1


class BaseOptimizer(ng.optimization.base.Optimizer):
    def __init__(self, *args, parametrization=None, **kwargs):
        super(BaseOptimizer, self).__init__(*args, parametrization=parametrization, **kwargs)
        self.grid_state = n_dim_inf_generator(n=parametrization.dimension)

    def _internal_ask(self):
        """Called every time `ask` request processed.

        Should be implemented for optimizer to work.
        Return 1-d array-like structure with shape same as parametrization.dimension
            Returned values should be standardized to [-3, 3] interval.
            Further mapping on hyperparameters space performed automatically
            (i.e. for scalar hyperparameter -3 will be mapped to lower limit, 3 to upper limit)
            Values out of [-3, 3] interval are truncated
            (may be useful to consider that as truncated z-index of normal distribution)"""
        return next(self.grid_state)*6-3


def get_optimizer(title):
    """Mapping of optimizer name to implementation"""
    custom_registry = {
        'GridSearch': BaseOptimizer,
        # New optimizers may be added here
    }
    optimizer = custom_registry.get(title, None)
    if optimizer is not None:
        return optimizer
    optimizer = ng.optimizers.registry.get(title, None)
    if optimizer is None:
        raise ValueError(f'unknown optimizer {title!r}')
    return optimizer
