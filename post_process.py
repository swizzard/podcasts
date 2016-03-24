import numpy as np


def get_freqs(a):
    raw = dict(zip(*np.unique(a, return_counts=True)))
    return {k: v for k, v in raw.items()}


def pub_schedule(pod_info):
    out = {}
    try:
        pubs = pod_info['pubs']
    except KeyError:
        print(pubs)
        raise
    if not pubs:
        return out
    wkdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
              'Saturday']
    week_days = np.array([pub.weekday() for pub in pubs])
    month_days = np.array([pub.day for pub in pubs])
    wd_freqs = get_freqs(week_days)
    md_freqs = get_freqs(month_days) 
    # if len(wd_freqs) >= 5:
    #     out['schedule'] = 'daily'
    # if wdf_std < mdf_std:
    #     wdf_std = np.std(np.array(list(wd_freqs.values())))
    #     mdf_std = np.std(np.array(list(md_freqs.values())))
    out['week_days'] = wd_freqs
    out['month_days'] = md_freqs
    return out


def reject_outliers(data, m=2.):
    """
    Taken from http://stackoverflow.com/questions/11686720/is-there-a-numpy-builtin-to-reject-outliers-from-a-list
    """
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d/mdev if mdev else 0.
    try:
        out = data[s < m]
    except IndexError:
        out = None
    return out


def expected_dur(pod_info):
    try:
        durs = [d for d in pod_info['durs'] if d is not None]
    except KeyError:
        print(pod_info)
        raise
    if not durs:
        return None
    else:
        durs = np.array(durs)
        normed = reject_outliers(durs, 1)
        if normed is None:
            return None
        med = np.median(normed)
        mean = normed.mean()
        avg_mins = (med + mean) / 120
        if avg_mins < 15:
            return 'mini'
        elif avg_mins <= 28:
            return 'short'
        elif avg_mins <= 44:
            return '30'
        elif avg_mins <= 58:
            return '45'
        elif avg_mins <= 74:
            return 'hour'
        elif avg_mins <= 88:
            return '75'
        elif avg_mins <= 116:
            return '90'
        elif avg_mins <= 140:
            return '2hours'
        else:
            return 'long'

