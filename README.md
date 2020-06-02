# optimum
Self-hosted service for hyperparameter optimization

Optimum is a service for performing hyperparameter optimization.
It functions as API, providing ask/tell interface for asking which point in hyperparameter space should be investigated next,
and supplying service with information about value of target function at given point.
Service provides multiple optimizers, including Bayesian optimization (API optimizer title - `BO`),
genetic algorithms (I.e. `OnePlusOne`), etc.

Docker image of this service is available on Docker Hub as [alex314mart/optimum](https://hub.docker.com/r/alex314mart/optimum).

To start service on default port 8001 run<br>
`docker run -p 8001:8001 alex314mart/optimum`

Then you'll be able to interact with service API with requests like that:

```
GET /status
```
To use as liveness probe

```
GET /experiment
```
List all active experiments

```
POST /experiment
{
  "params": {
    <param_name>: {
      "type": "scalar",
      "parameters": {
        "lower": <float_number>,
        "upper": <float_number>
      }
    },
    <param_name>: {
      "type": "choice",
      "parameters": {
        "choices": [<string>, ...]
      }
    },
    ...
  },
  "optimizer": <optimizer_title>
}
```
Create new experiment, defining hyperparameters space via json body.<br>
<param_name> may be arbitrary string<br>
Type of parameters may be one of `["scalar", "log", "choice"]` for numerical value, numerical with logarithmic distribution, choice from list of strings, respectively<br>
For `"choice"` parameters `"choices"` should be list of arbitrary strings.<br>
`<optimizer_title>` may be one of `["BO", "OnePlusOne", "RandomSearch", "GridSearch"]` or custom if implemented.<br>
Returns <experiment_id> (string)

```
GET /experiment/<experiment_id>
```
Get status of experiment with id <experiment_id>

```
DELETE /experiment/<experiment_id>
```
Delete experiment with id <experiment_id>. All data of given experiment will be lost.

```
GET /experiment/<experiment_id>/ask
```
Get point of hyperparameters space for experiment with id <experiment_id> to investigate next

```
POST /experiment/<experiment_id>/tell
{
  "point": {
    <param_name>: <float_number>,
    ...
  },
  "value": <float_number>
}
```
Tell value of target function at given point of hyperparameters space to service for experiment with id <experiment_id>.<br>
Such requests may be sent even without getting prior point suggestion from `/experiment/<experiment_id>/ask`.

Examples of service usage in Python are provided in jupyter notebook [TestApp.ipynb](https://github.com/Alex314/optimum/blob/master/TestApp.ipynb)
