import uuid
from io import BytesIO
import base64

from flask import Flask
import nevergrad as ng
import matplotlib.pyplot as plt

from optimizers import get_optimizer


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
                raise ValueError(f'Parameter specifications should be dict for {parameter_name!r}')
            param_type = specs.get('type', None)
            if param_type is None:
                raise ValueError(f'No type found for parameter {parameter_name!r}')
            param_attributes = specs.get('parameters', {})

            try:
                ng_params[parameter_name] = ng_param_types.get(param_type, None)(**param_attributes)
            except Exception:
                raise ValueError(f'Unknown attributes for parameter {parameter_name!r}')
        return ng.p.Dict(**ng_params)

    def start_experiment(self, request):
        params = request.get('params')
        optimizer_title = request.get('optimizer', 'OnePlusOne')
        params_space = self.parse_params_space(params)
        self.logger.info(f'Params space defined: {str(params_space)}')
        optimizer = get_optimizer(optimizer_title)(parametrization=params_space)
        experiment_id = str(uuid.uuid4())
        self.experiments[experiment_id] = {
            'optimizer_title': optimizer_title,
            'optimizer': optimizer
        }
        return experiment_id

    def ask(self, experiment_id):
        optimizer = self.experiments[experiment_id]['optimizer']
        point = optimizer.ask()
        return point.value

    def tell(self, experiment_id, point, value):
        optimizer = self.experiments[experiment_id]['optimizer']
        candidate = optimizer.parametrization.spawn_child(new_value=point)
        optimizer.tell(candidate, value)

    def get_status(self, experiment_id):
        optimizer = self.experiments[experiment_id]['optimizer']
        ans = {
            'n evaluated points': len(optimizer.archive),
            'recommended point': optimizer.recommend().value,
        }
        return ans

    def get_target_chart(self, experiment_id):
        optimizer = self.experiments[experiment_id]['optimizer']
        values = []
        for checked in optimizer.archive.values():
            values.append(checked.mean)

        plt.figure(figsize=(20, 4))
        plt.scatter(range(len(values)), values, c='g')
        plt.title('Target function')
        plt.xlabel('# iteration')
        plt.ylabel('Target function value')
        plt.grid()

        figfile = BytesIO()
        plt.savefig(figfile, format='png')
        figfile.seek(0)
        figdata_png = base64.b64encode(figfile.getvalue()).decode()
        ans = 'data:image/png;base64, ' + figdata_png
        plt.close('all')
        return ans

    def get_charts(self, experiment_id):
        optimizer = self.experiments[experiment_id]['optimizer']
        charts = []

        checked_params = {}
        values = []
        for checked in optimizer.archive.values():
            values.append(checked.mean)
            for k, v in checked.parameter.value.items():
                checked_params[k] = checked_params.get(k, []) + [v]

        for parameter, parameter_values in checked_params.items():
            plt.figure(figsize=(20, 4))
            plt.scatter(range(len(values)), parameter_values, c=values, cmap='jet')
            plt.colorbar(label='target function values')
            plt.title(f'Parameter {parameter}')
            plt.xlabel('# iteration')
            plt.ylabel('Parameter value')
            plt.grid()

            figfile = BytesIO()
            plt.savefig(figfile, format='png')
            figfile.seek(0)
            figdata_png = base64.b64encode(figfile.getvalue()).decode()
            charts.append('data:image/png;base64, ' + figdata_png)
        plt.close('all')
        return charts
