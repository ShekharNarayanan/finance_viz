import pandas as pd
import numpy as np
from pathlib import Path
import os, sys


def load_transaction_data():
    proj_path = Path().cwd().parent
    file_path = os.path.join(proj_path,'files','transaction_data.xls')

    transaction_data = pd.read_excel(file_path)

    return transaction_data