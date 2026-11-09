"""Forecast-scoring utilities. Input arrays must already meet the study eligibility rule.

These functions do not reconstruct raw logger data or fit forecasting models.
"""
import math
import numpy as np

def _arrays(*arrays):
    result=[np.asarray(x,dtype=float) for x in arrays]
    if not result or not all(x.ndim==1 and len(x)==len(result[0]) for x in result):
        raise ValueError('Provide equally sized one-dimensional arrays')
    if not len(result[0]) or not all(np.isfinite(x).all() for x in result):
        raise ValueError('Provide nonempty finite arrays after applying eligibility')
    return result

def point_metrics(observed,predicted,persistence=None):
    y,p=_arrays(observed,predicted);e=p-y;sse=np.sum(e**2);sst=np.sum((y-y.mean())**2)
    result=dict(n=len(y),MAE=float(np.mean(abs(e))),RMSE=float(np.sqrt(np.mean(e**2))),
      MedianAE=float(np.median(abs(e))),Bias=float(np.mean(e)),
      R2=float(1-sse/sst) if sst>0 else np.nan,
      PearsonR=float(np.corrcoef(y,p)[0,1]) if np.std(y)>0 and np.std(p)>0 else np.nan,
      Within10=float(np.mean(abs(e)<=10)),Within15=float(np.mean(abs(e)<=15)))
    if persistence is not None:
        _,baseline=_arrays(y,persistence);den=np.sum((baseline-y)**2)
        result['MSE_skill']=float(1-sse/den) if den>0 else np.nan
    return result

def interval_metrics(observed,q10,q50,q90,expansion=0):
    y,l,m,u=_arrays(observed,q10,q50,q90)
    if (l>m).any() or (m>u).any():raise ValueError('Quantile order is invalid; do not silently repair')
    if not np.isfinite(expansion) or expansion<0:raise ValueError('Use a finite nonnegative expansion')
    l=l-expansion;u=u+expansion
    interval_score=u-l+10*np.maximum(l-y,0)+10*np.maximum(y-u,0)
    def pinball(q,t):return np.maximum(t*(y-q),(t-1)*(y-q))
    return dict(coverage=float(np.mean((y>=l)&(y<=u))),width=float(np.mean(u-l)),
      interval_score=float(interval_score.mean()),
      WIS=float(np.mean((.5*abs(y-m)+.1*interval_score)/1.5)),
      mean_pinball=float(np.mean((pinball(l,.1)+pinball(m,.5)+pinball(u,.9))/3)))

def conformal_expansion(observed,lower,upper,alpha=.2):
    if not 0<alpha<1:raise ValueError('alpha must be between zero and one')
    y,l,u=_arrays(observed,lower,upper)
    if (l>u).any():raise ValueError('Lower bound exceeds upper bound')
    scores=np.maximum.reduce([l-y,y-u,np.zeros(len(y))]);k=math.ceil((len(y)+1)*(1-alpha))
    # With too few calibration observations the finite-rank upper score is infinite.
    return float(np.sort(scores)[k-1]) if k<=len(scores) else float('inf')

def confusion_metrics(observed_labels,predicted_labels,touched_plot_days=None):
    y,p=_arrays(observed_labels,predicted_labels)
    if not np.isin(y,[0,1]).all() or not np.isin(p,[0,1]).all():raise ValueError('Use binary labels')
    tp=int(np.sum((y==1)&(p==1)));fp=int(np.sum((y==0)&(p==1)))
    fn=int(np.sum((y==1)&(p==0)));tn=int(np.sum((y==0)&(p==0)))
    result=dict(n=len(y),TP=tp,FP=fp,FN=fn,TN=tn,positives=tp+fn,
      precision=tp/(tp+fp) if tp+fp else np.nan,recall=tp/(tp+fn) if tp+fn else np.nan,
      F1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else np.nan,
      FP_per_24_issuance_hours=24*fp/len(y))
    if touched_plot_days is not None:
        if touched_plot_days<=0:raise ValueError('Touched-day count must be positive')
        result['FP_per_touched_plot_day']=fp/touched_plot_days
    return result

def joint_block_mae_difference(frame,block_hours=72,replicates=2000,seed=17,circular=False):
    """Paired MAE uncertainty on dense hourly blocks shared across plots.

    Required columns: origin_timestamp, plot_id, observed, predicted, reference.
    Supply only mutually eligible endpoints for one horizon and split.
    This is a reusable implementation, not the unrecovered original model runner.
    """
    import pandas as pd
    required=['origin_timestamp','plot_id','observed','predicted','reference']
    if not set(required)<=set(frame):raise ValueError('Missing required columns')
    f=frame[required].copy();f['origin_timestamp']=pd.to_datetime(f.origin_timestamp)
    if f.duplicated(['origin_timestamp','plot_id']).any():raise ValueError('Duplicate origin/plot key')
    if f[required].isna().any().any():raise ValueError('Missing endpoint/key values')
    for col in ['observed','predicted','reference']:
        if not np.isfinite(f[col]).all():raise ValueError('Nonfinite endpoint value')
    if not (f.origin_timestamp.dt.floor('h')==f.origin_timestamp).all():raise ValueError('Origins must be hourly')
    grid=pd.date_range(f.origin_timestamp.min(),f.origin_timestamp.max(),freq='h');n=len(grid)
    if not 1<=block_hours<=n or replicates<2:raise ValueError('Invalid block length/replicate count')
    f['difference']=abs(f.predicted-f.observed)-abs(f.reference-f.observed)
    sums=f.groupby('origin_timestamp').difference.sum().reindex(grid,fill_value=0).to_numpy()
    counts=f.groupby('origin_timestamp').size().reindex(grid,fill_value=0).to_numpy()
    rng=np.random.default_rng(seed);draws=[]
    for _ in range(replicates):
        starts=rng.integers(0,n if circular else n-block_hours+1,size=math.ceil(n/block_hours))
        ix=np.concatenate([np.arange(s,s+block_hours) for s in starts])[:n]
        if circular:ix%=n
        den=counts[ix].sum()
        if den:draws.append(sums[ix].sum()/den)
    if not draws:raise ValueError('No evaluated endpoints in bootstrap replicates')
    lower,upper=np.quantile(draws,[.025,.975])
    return dict(difference=float(f.difference.mean()),lower=float(lower),upper=float(upper),
      finite_replicates=len(draws),requested_replicates=replicates,block_hours=block_hours,circular=circular)
