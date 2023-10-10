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
    all_councils = pd.DataFrame(columns=['LaCode', 'Proportion', 'Admin_item'])
    for c in councils:

        per_council = AllData[AllData['LaCode'] == c]
        all = pd.DataFrame(columns=['LaCode', 'Proportion', 'Admin_item'])
        variables = params.demographic_variables
        for v in variables:
            per_council_variables = per_council[['LaCode', v]]
            per_council_grouped = per_council_variables.groupby([v]).sum()
            per_council_grouped = per_council_grouped.reset_index()
            per_council_grouped['Total'] = per_council_grouped['LaCode'].sum()
            per_council_grouped['Proportion'] = (
                per_council_grouped['LaCode'] / per_council_grouped['Total']) * 100
            # now format
            per_council_grouped[v] = per_council_grouped[v].astype(int)
            per_council_grouped['Admin_item'] = v + \
                per_council_grouped[v].astype(str)
            per_council_grouped['LaCode'] = c
            per_council_grouped = per_council_grouped[[
                'LaCode', 'Proportion', 'Admin_item']]
            all = pd.concat([all, per_council_grouped])
        all_councils = pd.concat([all_councils, all])
    return all_councils


def add_proportions_last_year(all_mean):
    # edit for the previous year's data
    inputs = params.last_years_files
    Dataset = 'SURV_ADMIN_DATA_PROP.csv'
    last_years_data = pd.read_csv(inputs+Dataset, header=0, low_memory=False)

    last_years_data['Proportions'] = last_years_data['Proportions'].round(1)

    last_years_data = last_years_data[[
        'LaCode', 'Proportions', 'Admin_Data_Item']]
    last_years_data.rename(columns={
                           'Proportions': 'Proportions_last_year', 'Admin_Data_Item': 'Admin_item'}, inplace=True)

    all_prop = pd.merge(all_mean, last_years_data, on=[
                        'LaCode', 'Admin_item'], how='outer')

    return all_prop


def mean(all_councils):
    all_councils = all_councils[[
        "LaCode", "Proportion", "Admin_item", "Proportions_last_year"]]
    all_councils = all_councils[~all_councils['LaCode'].
                                isin(params.council_to_remove)]
    denominator = all_councils['LaCode'].nunique()
    items = all_councils['Admin_item'].unique()
    all_mean = pd.DataFrame(
        columns=['LaCode', 'Proportion', 'Admin_item', "Mean", "STD"])
    for i in items:
        filtered_mean = all_councils[all_councils["Admin_item"] == i]
        filtered_mean['tot'] = filtered_mean['Proportion'].sum()
        filtered_mean['Mean'] = filtered_mean['tot']/denominator
        filtered_mean['STD'] = filtered_mean['Proportion'].std()
        filtered_mean = filtered_mean.drop(columns=['tot'])
        all_mean = pd.concat([all_mean, filtered_mean])
        all_mean[['Proportion', 'STD', 'Mean']] = all_mean[[
            'Proportion', 'STD', 'Mean']].round(1)

    all_mean['upper'] = all_mean['Mean'] + (2 * all_mean['STD'])
    all_mean['lower'] = all_mean['Mean'] - (2 * all_mean['STD'])

    all_mean.fillna(0.0, inplace=True)
    all_mean['Flagged'] = all_mean['Proportion'].between(
        all_mean['lower'], all_mean['upper'])
    all_mean['Flagged'] = np.where((all_mean['Flagged'] == False), 1, 0)
    all_mean = all_mean[['LaCode', 'Admin_item', 'Proportion',
                         'Proportions_last_year', 'Mean', 'STD', 'Flagged']]
    all_mean.rename(columns={'Admin_item': 'Admin_Data_Item',
                             'Proportion': 'Proportions'}, inplace=True)
    all_mean.fillna(0.0, inplace=True)

    return all_mean


def england_level(all_prop):

    all_prop = all_prop[['Admin_Data_Item', 'Mean', 'STD']]

    all_prop = all_prop.drop_duplicates()
    all_prop['LaCode'] = 1001

    all_prop.fillna(0, inplace=True)
    all_prop = all_prop[all_prop["STD"] != 0]
    return all_prop[['LaCode', 'Admin_Data_Item', 'Mean', 'STD']]


def main():
    imports = import_data()
    filters = filter(imports)

    proportion = add_proportions_last_year(filters)
    means = mean(proportion)
    means.to_csv(output+"SURV_ADMIN_DATA_PROP.csv")
    englands = england_level(means)
    englands.to_csv(output+"SURV_ADMIN_MEAN_STD.csv")
    return englands


create = main()
create
