from finance_viz.utils.transaction_data_utils import AugmentTransactionData, PROJECT_ROOT

atd = AugmentTransactionData() # initialize class

# get prepared data
prepared_transaction_data = atd.get_prepared_transaction_data()

# show header column
prepared_transaction_data.head()

# save data
prepared_transaction_data.to_csv(PROJECT_ROOT / 'input_data' / 'prepared_transaction_data.csv', index=False)