import sys, os, numpy as np, pandas as pd
from scipy import stats

R, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
# Folder names in the replication repository, with the original repository names as fallback
MRCNN = next(f for f in ('models_maskrcnn', 'LSTM_Paper_RCnn') if os.path.isdir(os.path.join(R, f)))
DETR = next(f for f in ('models_detr', 'LSTM_Paper_transformer') if os.path.isdir(os.path.join(R, f)))

def rmse(e): return float(np.sqrt(np.mean(np.square(e))))
def mae(e): return float(np.mean(np.abs(e)))

def dm_test(e1, e2):
    """Diebold-Mariano test, squared-error loss, Newey-West variance with Bartlett weights."""
    d = np.square(e1) - np.square(e2); n = len(d); dc = d - d.mean()
    lag = int(np.floor(4 * (n / 100) ** (2 / 9)))
    lrv = np.dot(dc, dc) / n
    for k in range(1, lag + 1):
        lrv += 2 * (1 - k / (lag + 1)) * np.dot(dc[k:], dc[:-k]) / n
    s = d.mean() / np.sqrt(lrv / n)
    return float(s), float(2 * (1 - stats.norm.cdf(abs(s)))), lag

# Historical profile: mean speed by camera, day type (weekday, Saturday, Sunday) and five-minute slot,
# from the training weeks (March and April). Speeds in whole km/h as in the modelling notebooks.
raw = pd.read_csv(os.path.join(R, MRCNN, 'output_test_septem_v1 - Copy.csv'))
raw = raw[raw.Route.isin(['b_PIE', 'b_Woodlands'])].copy()
raw['Timestamp'] = pd.to_datetime(raw['Timestamp'])
raw['kmh'] = (raw['Y_Speed'] * 3.6).astype(int)
def keys(df):
    df['slot'] = df.Timestamp.dt.strftime('%H:%M')
    dow = df.Timestamp.dt.day_name()
    df['daytype'] = np.where(dow.isin(['Saturday', 'Sunday']), dow, 'Weekday')
    return df
raw = keys(raw)
train = raw[raw.X14_Month.isin([3, 4])]
profile = train.groupby(['Route', 'Camera_id', 'daytype', 'slot'])['kmh'].mean().rename('profile').reset_index()

acc, tests, sub, cur = [], [], [], []
for det, folder in [('Mask R-CNN', MRCNN), ('DETR', DETR)]:
    for route, name in [('b_Woodlands', 'North'), ('b_PIE', 'South')]:
        d = pd.read_csv(os.path.join(R, folder, f'{route}_best_models', f'{route}_june_speed_result.csv'))
        d['Timestamp'] = pd.to_datetime(d['Timestamp'])
        d = keys(d).merge(profile, on=['Route', 'Camera_id', 'daytype', 'slot'], how='left')
        y = d['Y_Speed'].to_numpy(float); h = d['profile'].to_numpy(float)
        assert not np.isnan(h).any()
        cur.append(pd.DataFrame(dict(detector=det, direction=name, Timestamp=d['Timestamp'], Camera_id=d['Camera_id'],
                                     observed=y, profile=h, xgb=d['xgb_m2'], lstm=d['lstm_m2'])))
        for k, suf in [(0, ''), (1, '_1'), (3, '_3'), (6, '_6')]:
            n = len(d) - k
            yt, ht = y[k:k + n], h[k:k + n]
            preds = {'XGB': d[f'xgb_m2{suf}'].to_numpy(float)[:n], 'LSTM': d[f'lstm_m2{suf}'].to_numpy(float)[:n]}
            err = {m: yt - p for m, p in preds.items()}
            err['Profile'] = yt - ht
            if k > 0:
                err['Persistence'] = yt - y[:n]          # last observed speed at the time of the latest image
            for m, e in err.items():
                if det == 'DETR' and m in ('Profile', 'Persistence'):
                    continue
                acc.append(dict(detector=det, direction=name, k=k, method=m, RMSE=rmse(e), MAE=mae(e), n=n))
            s, p, lag = dm_test(err['XGB'], err['LSTM'])
            tests.append(dict(detector=det, direction=name, k=k, test='XGB vs LSTM', stat=s, p=p, lag=lag))
            for m in ('XGB', 'LSTM'):
                s, p, lag = dm_test(err[m], err['Profile'])
                tests.append(dict(detector=det, direction=name, k=k, test=f'{m} vs profile', stat=s, p=p, lag=lag))
                comb = yt - 0.5 * (preds[m] + ht)
                s, p, lag = dm_test(comb, err['Profile'])
                tests.append(dict(detector=det, direction=name, k=k, test=f'{m}+profile vs profile', stat=s, p=p, lag=lag,
                                  RMSE_comb=rmse(comb), RMSE_profile=rmse(err['Profile']), MAE_comb=mae(comb)))
                if k > 0:
                    s, p, lag = dm_test(err[m], err['Persistence'])
                    tests.append(dict(detector=det, direction=name, k=k, test=f'{m} vs persistence', stat=s, p=p, lag=lag))
                if k == 0:
                    atyp = np.abs(err['Profile']) > 10
                    sub.append(dict(detector=det, direction=name, model=m, share_atypical=atyp.mean(),
                                    RMSE_model_atyp=rmse(err[m][atyp]), RMSE_profile_atyp=rmse(err['Profile'][atyp]),
                                    RMSE_model_typ=rmse(err[m][~atyp]), RMSE_profile_typ=rmse(err['Profile'][~atyp])))

acc, tests, sub = pd.DataFrame(acc), pd.DataFrame(tests), pd.DataFrame(sub)
acc.to_csv(os.path.join(OUT, 'benchmark_accuracy.csv'), index=False)
tests.to_csv(os.path.join(OUT, 'diebold_mariano_tests.csv'), index=False)
sub.to_csv(os.path.join(OUT, 'typical_atypical_intervals.csv'), index=False)
# Current-speed estimates of the test week, used by make_figures.py for the error-by-departure figure
pd.concat(cur).to_csv(os.path.join(OUT, 'test_week_current_speed.csv'), index=False)
pd.set_option('display.width', 220); pd.set_option('display.max_columns', 20)
print(acc.round(2).to_string()); print(tests.round(4).to_string()); print(sub.round(3).to_string())
