import pandas as pd
import numpy as np
from pathlib import Path
import os

class AugmentTransactionData():

    def __init__(self, proj_path:str):
        self.proj_path = proj_path

    def get_transaction_data(self):
        """Returns transaction data

        Returns:
            pd.DataFrame: transaction data with all the fields
        """
        file_path = os.path.join(self.proj_path,'files','transaction_data.xls')

        transaction_data = pd.read_excel(file_path)

        return transaction_data

    def get_transactions_with_identifiers(self):

        """Identify transaction type using method of payment. 
        The first two string elements in the transaction_description indicate type of transaction, 
        the payment method, or the institution facilitating the transaction (SEPA or BEA for instance)
        
        """
        # get transaction data
        transaction_data = self.get_transaction_data()
        
        # initialize identifier list
        identifiers = [] 

        for transaction_description in transaction_data['description']:
            elements = transaction_description.split()[:2]
            if ',' in elements[0]:
                elements[0] = elements[0].split(',')[0]

            identfier = elements[0] + '_' + elements[1]
            identifiers.append(identfier)

        transaction_data['identifier'] = identifiers
        transactions_with_identifiers = transaction_data

        return transactions_with_identifiers
    
    def remove_sensitive_data(self,optional_input:pd.DataFrame=None,extra_cols:list=[]):

        """Removes requested column info from the dataset

        Args:
            transaction_data (pd.DataFrame): _description_
            optional_input: transaction data fed by the user. Can be used for visualizing this step.
            extra_cols (_type_): _description_

        Returns:
            _type_: _description_
        """
        if optional_input is None:
            transaction_data = self.get_transaction_data()           
        else:
            transaction_data = optional_input
            

        default_cols = ['accountNumber', 'mutationcode', 'transactiondate', 'valuedate', 'startsaldo', 'endsaldo']
        modified_cols = default_cols + extra_cols

        if not extra_cols:
            transaction_data.drop(columns=default_cols,inplace=True)
        else:
            transaction_data.drop(columns=modified_cols,inplace=True)
        
        return transaction_data
    
    def get_most_freq_transaction_types(self,misc_company_threshold=0.05):
        """_summary_

        Args:
            transaction_data (pd.DataFrame): _description_
            misc_company_threshold (float, optional): threshold for tr_type(s) that occur in less than x% of the transactions  
                                                    Companies assigned to these transactions are labelled "misc.". Defaults to 0.05.
        
        """
        #
        transactions_with_identifiers = self.get_transactions_with_identifiers()


        # find most frequent transaction types
        freq_info_transaction_type = transactions_with_identifiers['identifier'].value_counts() # all info

        # Extract transaction types and their frequencies
        tr_type = freq_info_transaction_type.index # Transaction types
        tr_type_count = freq_info_transaction_type.values  # counts

        # get relative freq of transaction types
        tr_type_relative_freq = tr_type_count / np.sum(tr_type_count) 

        # get the most frequent transaction types and their counts
        tr_type_most_freq = tr_type[tr_type_relative_freq > misc_company_threshold]

        return tr_type_most_freq
    
    def get_transactions_with_company_labels(self,optional_input:pd.DataFrame=None):
        """_summary_

        Args:
            transaction_data (pd.DataFrame): _description_
            most_frequent_tr_type (list): _description_

        Returns:
            _type_: _description_
        """
        if optional_input is None:
            transactions_with_identifiers = self.get_transactions_with_identifiers()
        else:
            transactions_with_identifiers = optional_input        
            if 'identifier' not in transactions_with_identifiers.columns:
                raise KeyError(
                    "The transaction data used in this function requires the 'identifier' field."
                    "Consider using the output of get_transactions_with_identifiers() function."
                    "Alternatively, use the function with no input arguments."
                )



        # get most frequent transaction types
        most_frequent_tr_type = self.get_most_freq_transaction_types()

        # get series objects to iterate through later
        identifiers = transactions_with_identifiers['identifier']
        descriptions = transactions_with_identifiers['description']

        # list for collecting all companies
        companies = []

        for identifier, description in zip(identifiers,descriptions):
            if identifier in most_frequent_tr_type:
                description_split = description.split()
                if 'SEPA' in description_split[0]:
                    for i_str, str in enumerate(description_split):
                            if str == 'Naam:' :
                                companies.append(description_split[i_str + 1])
                elif 'BEA' in description_split[0]:
                    for i_str, str in enumerate(description_split):
                        if str == 'Pay':
                            companies.append(description_split[i_str + 1])
            else:
                companies.append('misc.')
       
        transactions_with_identifiers['company'] = companies
        transactions_with_companies = transactions_with_identifiers

        return transactions_with_companies