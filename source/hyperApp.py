import uuid

from flask import Flask
import nevergrad as ng


class HyperApp(Flask):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.experiments = {}

    def run(self, params, *args, **kwargs):
        super().run(*args, **kwargs)

    def parse_params_space(self, params):
        ng_param_types = {
            'log': ng.p.Log,
            'choice': ng.p.Choice,
            'scalar': ng.p.Scalar,
        }
        ng_params = {}
        for parameter_name, specs in params.items():
            if not isinstance(specs, dict):
                raise ValueError(f'Parameter specifications should be dict for {parameter_name}')
            param_type = specs.get('type', None)
            if param_type is None:
                raise ValueError()
            param_attributes = specs.get('parameters', {})

            try:
                ng_params[parameter_name] = ng_param_types.get(param_type, None)(**param_attributes)
            except Exception:
                raise ValueError(f'Unknown attributes for parameter {parameter_name!r}')
        return ng.p.Dict(**ng_params)

    def start_experiment(self, params):
        params_space = self.parse_params_space(params)
        self.logger.info(f'Params space defined: {str(params_space)}')
        optimizer = ng.optimizers.OnePlusOne(parametrization=params_space)
        experiment_id = str(uuid.uuid4())
        self.experiments[experiment_id] = {
            'optimizer': optimizer
        }
        return experiment_id

    def ask(self, experiment_id):
        optimizer = self.experiments[experiment_id]['optimizer']
        point = optimizer.ask()
        return point.value
