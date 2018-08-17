import math
import logging


__all__ = ["futu"]


class Bourse:
    def __init__(self, stamp, commission, communication):
        self.stamp = stamp
        self.commission = commission
        self.communication = communication

    def buy(self, hand, share_in_hand, price):
        quantity = hand * share_in_hand * price

        com_temp = self.commission * quantity
        com_fee = com_temp if com_temp >= 5 else 5

        if hand * share_in_hand > 1000:
            base = math.floor(1000 / share_in_hand)
            transfer_fee = 1.0 + 0.1 * (hand - base)
        else:
            transfer_fee = 1.0

        communication = 1.0

        return com_fee + transfer_fee + communication

    def sell(self, hand, share_in_hand, price):
        quantity = hand * share_in_hand * price

        stamp_fee = self.stamp * quantity

        com_temp = self.commission * quantity
        com_fee = com_temp if com_temp >= 5 else 5

        if hand * share_in_hand > 1000:
            base = math.floor(1000 / share_in_hand)
            transfer_fee = 1.0 + 0.1 * (hand - base)
        else:
            transfer_fee = 1.0

        communication = 1.0

        return stamp_fee + com_fee + transfer_fee + communication

futu = Bourse(stamp=0.001, commission=0.003, communication=0.0)

riskfree = 1.0002

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s')
