import pandas as pd
import numpy as np
from pathlib import Path
import os

class AugmentTransactionData():

    def __init__(self, proj_path):
        self.proj_path = proj_path

    def get_transaction_data(self):
        file_path = os.path.join(self.proj_path,'files','transaction_data.xls')

        transaction_data = pd.read_excel(file_path)

        return transaction_data

    def get_data_with_identifiers(self):

        """Identify transaction type using method of payment. 
        The first two string elements in the transaction_description indicate type of transaction, 
        the payment method, or the institution facilitating the transaction (SEPA or BEA for instance)
        
        """
        identifiers = []
        transaction_data = self.get_transaction_data()

        for transaction_description in transaction_data['description']:
            elements = transaction_description.split()[:2]
            if ',' in elements[0]:
                elements[0] = elements[0].split(',')[0]

            identfier = elements[0] + '_' + elements[1]
            identifiers.append(identfier)

        transaction_data['identifier'] = identifiers

        return transaction_data