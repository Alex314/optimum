import logging

from flask import request, jsonify, render_template

from hyperApp import HyperApp


app = HyperApp(__name__)
app.logger.setLevel(logging.INFO)


@app.route("/status", methods=['GET'])
def status():
    """Status of service"""
    app.logger.info("Status requested")
    return {'status': 'OK'}


@app.route("/experiment", methods=['GET', 'POST'])
def experiment():
    if request.method == 'POST':  # Create new experiment
        params = request.json
        app.logger.info(f'Request experiment creation: {params}')
        experiment_id = app.start_experiment(params)
        app.logger.info(f'Experiment created: {experiment_id}')
        return {'experiment_id': experiment_id}
    else:  # List all active experiments
        ans = [{'experiment_id': experiment_id} for experiment_id in app.experiments]
        return jsonify(ans)


@app.route("/experiment/<experiment_id>", methods=['GET', 'DELETE'])
def particular_experiment(experiment_id):
    if experiment_id not in app.experiments:
        return {'status': 'Experiment with such ID not Found'}, 404

    if request.method == 'DELETE':  # Delete experiment
        del app.experiments[experiment_id]
        app.logger.info(f'Experiment {experiment_id} deleted')
        return {'status': 'OK'}
    else:  # Get status and current best point for experiment
        status = app.get_status(experiment_id)
        return status


@app.route("/experiment/<experiment_id>/ask", methods=['GET'])
def ask(experiment_id):
    if experiment_id not in app.experiments:
        return {'status': f'Experiment with ID {experiment_id} not Found'}, 404
    point = app.ask(experiment_id)
    app.logger.info(f'Point to return: {point}')
    return point


@app.route("/experiment/<experiment_id>/tell", methods=['POST'])
def tell(experiment_id):
    if experiment_id not in app.experiments:
        return {'status': f'Experiment with ID {experiment_id} not Found'}, 404
    point = request.json['point']
    value = request.json['value']
    app.logger.info(f'Tell value: {value} at point: {point}')
    app.tell(experiment_id, point, value)
    return {'status': 'OK'}


@app.route("/dashboard", methods=['GET'])
def dashboard():
    experiments = [[experiment_id, params['optimizer_title']]
                   for experiment_id, params in app.experiments.items()]
    return render_template('experiments.html', experiments=experiments)


@app.route("/dashboard/<experiment_id>", methods=['GET'])
def dashboard_experiment(experiment_id):
    app.logger.info(f"Visualization requested for {experiment_id}")
    if experiment_id not in app.experiments:
        return f'Experiment with ID {experiment_id} not Found', 404
    target_chart = app.get_target_chart(experiment_id)
    charts = app.get_charts(experiment_id)
    return render_template('charts.html', target_chart=target_chart, charts=charts)


if __name__ == '__main__':
    app.run({}, host='0.0.0.0', port=5000)
