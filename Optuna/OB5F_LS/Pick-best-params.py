import optuna
import statistics
import json

study = optuna.create_study(study_name="Band5min-LongOnly", directions=["maximize", "maximize"],
                                storage="postgresql://optuna_user:optuna_password@192.168.1.25/optuna_db_3", load_if_exists=True)

# Filter Optuna trials with performance metrics and standart deviation
# Create results.csv file with all results and a SEQ.py file with all hyperparameters

def print_best_params():
    print("Number of finished trials: ", len(study.trials))

    trials = study.trials
    
    results = []
    parameter_list = []  # to eliminate redundant trials with same parameters
    candidates = {}
    score_treshold = 1
    std_dev_treshold = 4
    from jesse.routes import router
    import jesse.helpers as jh
    r = router.routes[0]
    StrategyClass = jh.get_strategy_class(r.strategy_name)
    r.strategy = StrategyClass()
        
    for trial in trials:
        print(type(trial), trial.state)
        
        if trial.state != optuna.structs.TrialState.COMPLETE:
            continue
        
        if any(v < -1 for v in trial.values):
            continue
        
        if (not trial.user_attrs['trades1']) or trial.user_attrs['trades1'] < 50 or trial.values[0] < 1:
            continue
    
        mean_value = round(statistics.mean((*trial.values, trial.user_attrs['sharpe3'])), 3)
        std_dev = round(statistics.stdev((*trial.values, trial.user_attrs['sharpe3'])), 5)
        
        rounded_params = trial.params
    
        hp_new = {}
        
        # Sort hyperparameters as defined in the strategy
        for p in r.strategy.hyperparameters():
            hp_new[p['name']] = rounded_params[p['name']]

        rounded_params = hp_new
        
        result_line = [trial.number, *trial.values, trial.user_attrs['sharpe3'],
                       trial.user_attrs['trades1'], trial.user_attrs['trades2'], trial.user_attrs['trades3'],
                       trial.user_attrs['fees1'], trial.user_attrs['fees2'], trial.user_attrs['fees3'],
                       trial.user_attrs['wr1'], trial.user_attrs['wr2'], trial.user_attrs['wr3'],
                       mean_value, std_dev, rounded_params]
        
        # If parameters meet criteria, add to candidates
        if trial.params not in parameter_list and mean_value > score_treshold and std_dev < std_dev_treshold and trial.user_attrs['sharpe3'] > 2:
            results.append(result_line)
            parameter_list.append(trial.params)

            longest_param = 0
            
            for v in rounded_params.values():
                if len(str(v)) > longest_param:
                    longest_param = len(str(v))
            
            hash = ''.join([f'{value:0>{longest_param}}' for key, value in rounded_params.items()])
            hash = f'{hash}{longest_param}'
            candidates[hash] = rounded_params
    
    # Use it!
    sorted_results = sorted(results, key=lambda x: x[2], reverse=True)
    
    print(len(results))
    
    import csv
    
    # field names 
    fields = ['Trial #', 'Score1', 'Score2', 'Score3',
              'Trades1', 'Trades2', 'Trades3',
              'Fees1', 'Fees2', 'Fees3',
              'Winrate1', 'Winrate2', 'Winrate3',
              'Average', 'Deviation',
              'Parameters'] 
        
    with open('Results.csv', 'w') as f:
        write = csv.writer(f, delimiter='\t', lineterminator='\n')
        
        write.writerow(fields)
        write.writerows(results)
        
    with open('SEQ.py', 'w') as f:
        f.write("hps = ")
        f.write(json.dumps(candidates, indent=1))
        
print_best_params()
