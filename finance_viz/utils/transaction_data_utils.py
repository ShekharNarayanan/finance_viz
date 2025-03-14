import pandas as pd
import numpy as np
from pathlib import Path
import re
import os

# Compute the project root from the current file.
# __file__ is something like: /path/to/finance_viz/finance_viz/utils/transaction_data_utils.py
PROJECT_ROOT = Path(__file__).resolve().parents[2]
transaction_file_path = PROJECT_ROOT / 'input_data' / 'sample_transaction_data.xls'


class AugmentTransactionData():

    def get_transaction_data(self):
        """Returns transaction data

        Returns:
            pd.DataFrame: transaction data with all the fields
        """
        transaction_data = pd.read_excel(transaction_file_path)

        return transaction_data
    
    def get_prepared_transaction_data(self):
        """Prepares transaction data with companies for further processing
        """
        transaction_data = self.get_transactions_with_company_details()

        # restructure date as yyyy-mm-dd 
        transaction_data['valuedate'] = transaction_data['valuedate'].astype(str)
        transaction_data['valuedate'] = transaction_data['valuedate'].str.replace(
            r"(\d{4})(\d{2})(\d{2})", r"\1-\2-\3", regex=True
        )

        # Create a new column based on the sign of the "amount" column
        transaction_data["expense/income"] = np.where(transaction_data["amount"] < 0, "expense", "income")

        # Convert all values in the "amount" column to positive (absolute values)
        transaction_data["amount"] = transaction_data["amount"].abs()

        # drop unnecessary columns
        transaction_data.drop(columns=["description","accountNumber", "mutationcode",	"transactiondate", "startsaldo", "endsaldo"], inplace=True)

        # remove all transactions with "Unknown" company
        transaction_data = transaction_data[transaction_data["company"] != "Unknown"]

        return transaction_data


    
    def get_transactions_with_company_details(self):
        
        """
        Processes the description to output the company name or the name of the entity involved in the transaction.
        Apologies for the vague criteria, but the idea is to generalize it to as many transaction descriptions in NL as possible.
        Args:
            desc (str): description of the transaction

        Returns:
            str: company or entity name
        """
        companies = []

        transaction_data = self.get_transaction_data()

        for desc in transaction_data["description"]:
            # 1) Apple Pay logic
            if "Apple Pay" in desc:
                companies.append(desc.split("Apple Pay")[1].split(",PAS")[0].strip())                

            # 2) Different SEPA logic with "Naam:" / "Machtiging" / "Omschrijving:" / "Kenmerk:"
            elif "Naam:" in desc:
                remainder = desc.split("Naam:")[1]

                if "Machtiging:" in remainder:
                    companies.append(remainder.split("Machtiging:")[0].strip())
                
                elif "Machtiging:" not in remainder and "Omschrijving:" in remainder:
                    companies.append(remainder.split("Omschrijving:")[0].strip())
                
                elif "Machtiging:" not in remainder and "Omschrijving:" not in remainder and "Kenmerk:" in remainder:
                    companies.append(remainder.split("Kenmerk:")[0].strip()  )
                else:
                    companies.append(remainder)
                

            # 3) Fallback or unknown structure
            else:
                 companies.append("Unknown")

        transaction_data["company"] = companies

        return transaction_data
    


if __name__ == '__main__':

    # initialize class
    atd = AugmentTransactionData()

    # get transactions with company details and locations
    transactions_with_companies = atd.get_transactions_with_companies(remove_sensitive_data=True)

    print(transactions_with_companies.head(20))



    