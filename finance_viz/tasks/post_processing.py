if __name__ == "__main__":
    import pandas as pd
    from finance_viz.utils.transaction_data_utils import PROJECT_ROOT

    # Load the data
    categorized_expenses = pd.read_excel(
        PROJECT_ROOT / "input_data" / "transactions_categorized.xlsx"
    )

    # Specify income sources as "Salary"
    income_sources = ["radboud universiteit", "tilburg university"]

    # copy dataframe and make all companies lowercase
    df_copy = categorized_expenses.copy()
    df_copy["company_lower"] = df_copy["company"].str.lower()

    # get transactions which are classified as income and check whether they match the income sources
    income_mask = df_copy["expense/income"] == "income"
    salary_mask = df_copy["company_lower"].isin(income_sources)

    # assign the "Salary" to the corresponding transactions
    df_copy.loc[income_mask & salary_mask, "Category"] = "Salary"
    df_copy.drop(columns="company_lower", inplace=True)

    df_copy.to_excel(
        PROJECT_ROOT / "input_data" / "transactions_categorized_salary_copy.xlsx",
        index=False,
    )

    print("Post processing completed successfully.")
