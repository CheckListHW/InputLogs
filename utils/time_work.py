import time


class MyTimer:
    start_time = 0
    pre_time = 0
    checks = {}
    total_checks = {}

    @staticmethod
    def step():
        print("--- {0} start || {1} pre ---".format(time.time() - MyTimer.start_time, time.time() - MyTimer.pre_time))
        MyTimer.pre_time = time.time()

    @staticmethod
    def start():
        MyTimer.start_time = time.time()
        MyTimer.pre_time = time.time()

    @staticmethod
    def chek_start(index: str = 'a'):
        if MyTimer.total_checks.get(index) is None:
            MyTimer.total_checks[index] = 0
        MyTimer.checks[index] = time.time()

    @staticmethod
    def chek_finish(index: str = 'a'):
        MyTimer.total_checks[index] += (time.time()-MyTimer.checks[index])

    @staticmethod
    def finish():
        finis_time = time.time() - MyTimer.start_time
        for index in MyTimer.total_checks:
            print("--- {0} = {1} seconds   {2} percent ---".format(index, round(MyTimer.total_checks[index], 6), round(MyTimer.total_checks[index]/finis_time, 5)*100))
            MyTimer.total_checks[index] = 0
        print("--- Total = {0} seconds ---".format(finis_time))
        print()
