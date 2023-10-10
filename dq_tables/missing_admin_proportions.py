import pandas as pd
import numpy as np
import params

output = params.output


def import_data():
    inputs = params.input
    Dataset = 'cleaned_questionnaire.csv'
    AllData = pd.read_csv(inputs+Dataset, header=0, low_memory=False)
    return AllData


def filter(AllData):
    councils = AllData['LaCode'].unique()
    all_councils = pd.DataFrame(
        columns=['LaCode', 'Proportion', 'Admin_data_item'])
    for c in councils:

        per_council = AllData[AllData['LaCode'] == c]
        all = pd.DataFrame(
            columns=['LaCode', 'Admin', 'Admin_data_item', 'Proportions'])
        variables = params.demographic_variables
        for v in variables:
            per_council_variables = per_council[['LaCode', v]]
            # replace blank
            per_council_variables[v] = per_council_variables[v].fillna(0)
            per_council_grouped = per_council_variables.groupby([v]).sum()
            per_council_grouped = per_council_grouped.reset_index()
            per_council_grouped['Total'] = per_council_grouped['LaCode'].sum()
            per_council_grouped['Proportion'] = (
                per_council_grouped['LaCode'] / per_council_grouped['Total']) * 100
            per_council_grouped = per_council_grouped[per_council_grouped[v] != 0.0]

            # to account for missing measures (blanks in the data)
            zeros = {v: [0], 'LaCode': [0], 'Total': [0], "Proportion": [0]}
            per_council_zeros = pd.DataFrame(data=zeros)
            per_council_grouped = pd.concat(
                [per_council_zeros, per_council_grouped])

            per_council_grouped['Total_proportion'] = per_council_grouped['Proportion'].sum(
            )
            per_council_grouped['Sub_total_proportions'] = 100 - \
                per_council_grouped['Total_proportion']
            # format
            per_council_grouped['LaCode'] = c
            per_council_grouped[v] = v
            per_council_grouped['Missing'] = 'Missing'
            per_council_grouped['Admin_data_item'] = per_council_grouped['LaCode'].astype(
                str) + per_council_grouped[v].astype(str) + per_council_grouped['Missing'].astype(str)
            per_council_grouped['Admin'] = per_council_grouped[v].astype(
                str) + per_council_grouped['Missing'].astype(str)
            per_council_grouped['Proportions'] = per_council_grouped['Sub_total_proportions']
            per_council_grouped = per_council_grouped[[
                'LaCode', 'Admin', 'Admin_data_item', 'Proportions']]

            per_council_grouped = per_council_grouped.drop_duplicates()
            all = pd.concat([all, per_council_grouped])
        all_councils = pd.concat([all_councils, all])
    return all_councils


def mean(all_councils):
    items = all_councils['Admin'].unique()
    all_mean = pd.DataFrame(
        columns=['LaCode', 'Proportions', 'Admin_data_item', "Mean", "STD"])
    for i in items:
        filtered_mean = all_councils[all_councils["Admin"] == i]
        filtered_mean['Mean'] = filtered_mean['Proportions'].mean()
        filtered_mean['STD'] = filtered_mean['Proportions'].std()

        all_mean = pd.concat([all_mean, filtered_mean])
        all_mean[['Proportions', 'STD', 'Mean']] = all_mean[[
            'Proportions', 'STD', 'Mean']].round(1)
    return all_mean


def add_proportions_last_year(all_mean):
    # edit for the previous year's data
    inputs = params.last_years_files
    Dataset = 'SURV_MISSING_ADMIN_DATA.csv'
    last_years_data = pd.read_csv(inputs+Dataset, header=0, low_memory=False)

    last_years_data['Proportions'] = last_years_data['Proportions'].round(
        1).abs()

    last_years_data.rename(
        columns={'Admin_Data_Item': 'Admin_data_item'}, inplace=True)
    last_years_data = last_years_data[['Admin_data_item', 'Proportions']]
    last_years_data.rename(
        columns={'Proportions': 'Proportions_last_year'}, inplace=True)
    all_prop = all_mean.merge(
        last_years_data, on='Admin_data_item', how='left')
    # add upper and lower limit
    all_prop['upper'] = all_prop['Mean'] + (2 * all_prop['STD'])
    all_prop['lower'] = all_prop['Mean'] - (2 * all_prop['STD'])
    #####
    # calculate if flagged
    all_prop['Flagged'] = all_prop['Proportions'].between(
        all_prop['lower'], all_prop['upper'])
    all_prop['Flagged'] = np.where((all_prop['Flagged'] == False), 1, 0)
    all_prop.rename(
        columns={'Admin_data_item': 'Admin_Data_Item'}, inplace=True)

    all_prop['Proportions'] = all_prop['Proportions'].abs()

    return all_prop[['LaCode', 'Admin_Data_Item', 'Proportions_last_year', 'Proportions', 'Mean', 'STD', 'Flagged']]


def england_level(all_prop):
    all_prop.rename(columns={'Admin': 'Admin_Data_Item'}, inplace=True)
    all_prop = all_prop[['Admin_Data_Item', 'Mean', 'STD']]
    all_prop['Mean'] = all_prop['Mean'].round(1).abs()
    all_prop['STD'] = all_prop['STD'].round(1)
    all_prop = all_prop.drop_duplicates()
    all_prop['LaCode'] = 1001
    return all_prop


def main():
    imports = import_data()
    filters = filter(imports)
    means = mean(filters)
    proportions = add_proportions_last_year(means)
    proportions.to_csv(output+"SURV_MISSING_ADMIN_DATA.csv")
    englands = england_level(means)
    englands.to_csv(output+"SURV_MISSING_ADMIN_MEAN_STD.csv")
    return englands


create = main()
create
