import pandas as pd
import numpy as np
from pathlib import Path
import re

# set base variables
proj_path = Path.cwd().parent / 'finance_viz'
transaction_file_path = proj_path / 'input_files' / 'sample_transaction_data.xls'


class AugmentTransactionData():

    def __init__(self, proj_path:str):
        self.proj_path = proj_path

    def get_transaction_data(self):
        """Returns transaction data

        Returns:
            pd.DataFrame: transaction data with all the fields
        """
        transaction_data = pd.read_excel(transaction_file_path)

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
            

        default_cols = ['accountNumber', 'mutationcode', 'transactiondate', 'valuedate', 'startsaldo', 'endsaldo','amount']
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
    
    def get_transaction_details(self,optional_input:pd.DataFrame=None, remove_sensitive_data:bool=False):
        """_summary_. Apple Pay and SEPA transactions were the most frequent transaction identifiers/ types.

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
            
        if remove_sensitive_data:
            transactions_with_identifiers = self.remove_sensitive_data(optional_input=transactions_with_identifiers)

        # get most frequent transaction types
        # most_frequent_tr_type = self.get_most_freq_transaction_types()

        # get series objects to iterate through later
        # identifiers = transactions_with_identifiers['identifier']
        descriptions = transactions_with_identifiers['description']

        # list for collecting all companies
        companies = []
        locations = []

        for description in descriptions:
            if 'Apple Pay' in description:
                company_match = re.search(r'Apple Pay\s+(.+?),PAS', description)
                location_match = re.search(r'PAS\d+\s+NR:.+?,\s+\d{2}\.\d{2}\.\d{2}/\d{2}:\d{2}\s+(\w+)', description)
                
                company = company_match.group(1) if company_match else 'misc.'
                location = location_match.group(1) if location_match else 'unknown'
            elif 'SEPA' in description:
                company_match = re.search(r'Naam:\s+(.+?)\s{2,}', description)
                company = company_match.group(1) if company_match else 'misc.'
                location = 'unknown' # SEPA transactions do not have location info
            else:
                company = 'misc.'
                location = 'unknown'
            
            companies.append(company)
            locations.append(location)

       
        transactions_with_identifiers['company'] = companies
        transactions_with_identifiers['location'] = locations
        transactions_with_companies = transactions_with_identifiers

        return transactions_with_companies
    


if __name__ == '__main__':

    # initialize class
    atd = AugmentTransactionData(proj_path)

    # get transactions with company details and locations
    transactions_with_companies = atd.get_transaction_details(remove_sensitive_data=True)

    print(transactions_with_companies.head(20))



    