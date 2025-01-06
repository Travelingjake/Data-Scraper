import pandas as pd
import re


def depivot_data(data):
    # depends on parties being listed in all caps and metadata being listed with lowercase
    metadata_columns = [c for c in data.columns if not re.search(r'\b[A-Z]+\b', c)]
    data = pd.melt(data, id_vars=metadata_columns, var_name='Party')
    return data
