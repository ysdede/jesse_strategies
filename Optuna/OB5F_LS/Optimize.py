import json
import signal
import sys
from subprocess import PIPE, Popen, call

import jessetk.utils as utils
import optuna

# Multi-objective NSGAII hyperparamaters optimization with Optuna
# Wraps Jesse ai's backtest function as an objective function


def objective(trial):
    ott_len = trial.suggest_int('ott_len', 5, 75)
    ott_percent = trial.suggest_int('ott_percent', 50, 550)
    ott_bw_up = trial.suggest_int('ott_bw_up', 50, 175)
    tps_qty_index = trial.suggest_int('tps_qty_index', 0, 120)
    max_risk_long = trial.suggest_int('max_risk_long', 30, 100)

    parameters = {'ott_len': ott_len, 'ott_percent': ott_percent, 'ott_bw_up': ott_bw_up,
                  'tps_qty_index': tps_qty_index, 'max_risk_long': max_risk_long}

    hps = json.dumps(parameters)

    # Long run **** market period
    process = Popen(['jesse-tk', 'backtest', '2018-04-15',
                    '2021-04-15', '--hp', hps], stdout=PIPE)

    (output, err) = process.communicate()
    exit_code = process.wait()
    output = output.decode('utf-8')
    # print(output)
    metrics = utils.get_metrics3(output)
    sharpe1 = metrics['sharpe']
    sortino1 = metrics['sortino']
    wr1 = metrics['win_rate']
    trades1 = metrics['total_trades']
    fees1 = metrics['paid_fees']
    trial.set_user_attr("trades1", trades1)
    trial.set_user_attr("wr1", wr1)
    trial.set_user_attr("fees1", fees1)

    if sharpe1 is None:
        print(output)

    # Training set-2, May 2021 Crash
    process = Popen(['jesse-tk', 'backtest', '2021-04-10',
                    '2021-07-19', '--hp', hps], stdout=PIPE)

    (output, err) = process.communicate()
    exit_code = process.wait()
    output = output.decode('utf-8')
    # print(output)
    metrics = utils.get_metrics3(output)
    sharpe2 = metrics['sharpe']
    sortino2 = metrics['sortino']
    wr2 = metrics['win_rate']
    trades2 = metrics['total_trades']
    fees2 = metrics['paid_fees']
    trial.set_user_attr("trades2", trades2)
    trial.set_user_attr("wr2", wr2)
    trial.set_user_attr("fees2", fees2)

    # Validation set
    process = Popen(['jesse-tk', 'backtest', '2021-07-24',
                    '2021-11-01', '--hp', hps], stdout=PIPE)

    (output, err) = process.communicate()
    exit_code = process.wait()
    output = output.decode('utf-8')

    metrics = utils.get_metrics3(output)
    sharpe3 = metrics['sharpe']
    sortino3 = metrics['sortino']
    wr3 = metrics['win_rate']
    trades3 = metrics['total_trades']
    fees3 = metrics['paid_fees']

    trial.set_user_attr("sortino3", sortino3)
    trial.set_user_attr("sharpe3", sharpe3)
    trial.set_user_attr("trades3", trades3)
    trial.set_user_attr("wr3", wr3)
    trial.set_user_attr("fees3", fees3)

    return sharpe1, sharpe2


def print_best_params():
    print("Number of finished trials: ", len(study.trials))

    trials = sorted(study.best_trials, key=lambda t: t.values)

    for trial in trials:
        print(f"Trial #{trial.number} Values: { trial.values} {trial.params}")


def save_best_params():
    with open("results.txt", "a") as f:
        f.write(f"Number of finished trials: {len(study.trials)}\n")

        trials = sorted(study.best_trials, key=lambda t: t.values)

        for trial in trials:
            f.write(
                f"Trial: {trial.number} Values: {trial.values} Params: {trial.params}\n")


def signal_handler(sig, frame):
    if study:
        print_best_params()
        save_best_params()

    print('You pressed Ctrl+C!')
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    # Warmup
    # You need to create pickle caches before multiprocessing backtests
    # print("Importing candles...")
    # process = call(['jesse-tk', 'import-routes', '2018-02-09'], stdout=sys.stdout, stderr=sys.stderr)

    # print("Performing one-pass backtest...")
    # process = call(['jesse-tk', 'backtest', '2019-02-15', '2021-11-25'], stdout=sys.stdout, stderr=sys.stderr)

    # if input("Are you sure? (y/n): ").lower().strip()[:1] != "y": exit(1)

    n_of_trials = 60
    workers = 4

    print(f"Running {n_of_trials} trials...")
    study = optuna.create_study(study_name="Band5min-LongOnly", directions=["maximize", "maximize"],
                                storage="postgresql://optuna_user:optuna_password@192.168.1.25/optuna_db_3", load_if_exists=True)
    study.optimize(objective, n_jobs=workers, n_trials=n_of_trials)

    print_best_params()
    save_best_params()
