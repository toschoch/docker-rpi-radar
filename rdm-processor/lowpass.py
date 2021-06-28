import datetime


class Filter:
    def __init__(self, tau):
        self.tau = tau
        self.tn1 = datetime.datetime(1970, 1, 1)
        self.vn1 = None

    def __call__(self, tn, vn):
        if self.vn1 is None:
            self.vn1 = vn
            self.tn1 = tn
            return vn
        else:
            dt = (tn - self.tn1).total_seconds()
            self.vn1 = self.vn1 + (vn - self.vn1) * dt / self.tau
            self.tn1 = tn
            return self.vn1
