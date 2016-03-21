import numpy as np


def fd(arr):
    return dict(zip(*np.unique(np.array(arr), return_counts=True)))


def pub_schedule(pod_info):
    out = {}
    pubs = pod_info['pubs']
    if not pubs:
        return out
    wkdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
              'Saturday']
    pub_days = {pub.weekday() for pub in pubs}
    out['week_days'] = np.array([wkdays[day] for day in pub_days])
    out['month_days'] = np.array(list({pub.day for pub in pubs}))
    return out


def reject_outliers(data, m = 2.):
    """
    Taken from http://stackoverflow.com/questions/11686720/is-there-a-numpy-builtin-to-reject-outliers-from-a-list
    """
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d/mdev if mdev else 0.
    return data[s<m]


def expected_dur(pod_info):
    durs = pod_info['durs']
    if not durs:
        return None
    else:
        durs = np.array(durs)
        normed = reject_outliers(durs, 1)
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

