import numpy as np


def absolute_trajectory_error(gt, est):
    gt=np.asarray(gt)
    est=np.asarray(est)
    return float(np.sqrt(np.mean(np.sum((gt-est)**2,axis=1))))


def relative_pose_error(gt, est):
    gt=np.asarray(gt)
    est=np.asarray(est)
    if len(gt)<2:
        return 0.0
    dgt=np.diff(gt,axis=0)
    dest=np.diff(est,axis=0)
    return float(np.sqrt(np.mean(np.sum((dgt-dest)**2,axis=1))))
