# from MultiThread import Helper
import threading
import random
import time

MAX_NUM = 10


class Producer(threading.Thread):
    '''
    生产者线程类
    '''

    def __init__(self, storage, consumedCon, producedCon):
        super(Producer, self).__init__()
        self.storage = storage
        self.consumedCon = consumedCon
        self.producedCon = producedCon
        self.round_by_notify = False

    def run(self):
        while True:
            self.do_round()
            time.sleep(1)

    def do_round(self):
        '''
        round_by_notify标志是否被notify唤醒的
        若是，notify唤醒回自动acquire
        否则，需要再次主动acquire
        '''
        if not self.round_by_notify:
            self.consumedCon.acquire()
        else:
            pass
        if len(self.storage) < MAX_NUM:
            d = random.randint(1, 99)
            self.storage.append(d)
            # Helper.SafeShow("_".join(('produce:', str(threading._get_ident()), str(d), str(len(self.storage)))))
            print("_".join(('produce:', str(d), str(len(self.storage)))))
            self.producedCon.notify()
            self.consumedCon.release()
            self.round_by_notify = False
        else:
            # Helper.SafeShow('storage full,waiting...' + str(threading._get_ident()))
            print('storage full,waiting...')
            self.consumedCon.wait()
            self.round_by_notify = True


class Consumer(threading.Thread):
    '''
    消费者线程类
    '''

    def __init__(self, storage, consumedCon, producedCon):
        super(Consumer, self).__init__()
        self.storage = storage
        self.consumedCon = consumedCon
        self.producedCon = producedCon
        self.round_by_notify = False

    def run(self):
        while True:
            self.do_round()
            time.sleep(1)

    def do_round(self):
        '''
        round_by_notify标志是否被notify唤醒的
        若是，notify唤醒回自动acquire
        否则，需要再次主动acquire
        '''
        if not self.round_by_notify:
            self.producedCon.acquire()
        else:
            pass

        if len(self.storage) > 0:
            # Helper.SafeShow('_'.join(
            #     ('     Consumer:', str(threading._get_ident()), str(self.storage.pop()), str(len(self.storage)))))
            print('_'.join(
                ('     Consumer:', str(self.storage.pop()), str(len(self.storage)))))
            self.consumedCon.notify()
            self.producedCon.release()
            self.round_by_notify = False
        else:
            # Helper.SafeShow('       storage empty, waiting...' + str(threading._get_ident()))
            print('       storage empty, waiting...')
            self.producedCon.wait()
            self.round_by_notify = True


def Test():
    CONSUMER_NUM = 3
    PRODUCER_NUM = 5
    storageList = []

    storageLock = threading.Lock()
    consumedCon = threading.Condition(lock=storageLock)
    producedCon = threading.Condition(lock=storageLock)

    tAllList = []
    tConsumerList = []
    for _ in range(CONSUMER_NUM):
        tConsumer = Consumer(storageList, consumedCon, producedCon)
        tConsumerList.append(tConsumer)
        tAllList.append(tConsumer)

    tProducerList = []
    for _ in range(PRODUCER_NUM):
        tProduce = Producer(storageList, consumedCon, producedCon)
        tProducerList.append(tProduce)
        tAllList.append(tProduce)

    for t in tAllList:
        t.start()


if __name__ == '__main__':
    Test()