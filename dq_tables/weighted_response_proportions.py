
import pandas as pd
import numpy as np
import params


output = params.output


def epop():
    EligiblePopulation = params.EligiblePopulation
    stratum = EligiblePopulation[[
        "LaCode", "stratum1Pop", "stratum2Pop", "stratum3Pop", "stratum4Pop"]]
    return stratum


def imports():
    inputs = params.input
    Dataset = 'cleaned_questionnaire.csv'
    AllData = pd.read_csv(inputs+Dataset, header=0, low_memory=False)
    return AllData


def weights(AllData, epop):
    questions = AllData.filter(regex=("^q"))
    all_councils = pd.DataFrame([])
    for q in questions:
        new_data = AllData[["LaCode", q, "Stratum"]]
        new_data = new_data.fillna(0)
        #unliked_numbers = [-9,0]
        cleaned_data = new_data
        unique_council = AllData['LaCode'].unique()

        for council in unique_council:
            per_council = cleaned_data[cleaned_data['LaCode'] == council]
            per_council = per_council[per_council[q] != 0]
            count_strata = per_council.groupby(["Stratum"]).count()
            count_strata = count_strata.reset_index()
            count_strata['LaCode'] = council

            epop_strat = epop[epop['LaCode'] == council]

            epop_melt = pd.melt(epop_strat, id_vars=['LaCode'])
            weights = pd.DataFrame(columns=['weights'])

            #   for x,y in zip(count_strata[q],epop_melt['value']):

            # ADDED STRATUM 5 TO REP STRATUM Q2C
            epop_melt['Stratum'] = [1, 2, 3, 4]

            merge = count_strata.merge(epop_melt, on="Stratum", how='left')

            merge['w'] = merge['value']/merge[q]

            per_council = per_council.groupby([q, 'Stratum']).count()

            per_council = per_council.reset_index()

            per_council.rename(columns={"LaCode": "count"}, inplace=True)

            per_council['LaCode'] = council

            to_be_mergde_with_responses = merge[["Stratum", "w", "LaCode_x"]]

            merged_with_responses = per_council.merge(
                to_be_mergde_with_responses, on="Stratum", how="left")

            merged_with_responses['weighted_count'] = merged_with_responses['count'] * \
                merged_with_responses['w']

            merged_no_zeros = merged_with_responses[merged_with_responses[q] != 0]

            merged_no_zeros_groupby = merged_no_zeros.groupby([q]).sum()

            merged_no_zeros_groupby = merged_no_zeros_groupby.reset_index()

            merged_no_zeros_groupby['sum'] = merged_no_zeros_groupby['weighted_count'].sum(
            )

            merged_no_zeros_groupby['Proportion'] = (
                merged_no_zeros_groupby['weighted_count']/merged_no_zeros_groupby['sum']) * 100

            final_merge = merged_no_zeros_groupby[[q, 'Proportion']]

            final_merge['LaCode'] = council

            final_merge['Question'] = q

            final_merge.rename(columns={q: "response_numbers"}, inplace=True)

            final_merge["response_numbers"] = final_merge["response_numbers"].astype(
                int)

            final_merge["Admin_Data_Item"] = final_merge["Question"] + \
                "response" + final_merge["response_numbers"].astype(str)
            all_councils = pd.concat([final_merge, all_councils])

    return all_councils

# CREATING NEW FUNCTION FOR Q2C


def q2c(all_councils, AllData):
    all_q2c = pd.DataFrame([])

    all_councils = all_councils[all_councils['Question'] != "q2c"]

    needed_stratum = [2, 4]
    AllData = AllData[AllData["SupportSetting"] == 1]
    AllData = AllData[AllData['PSR'] != 4]
    AllData = AllData[AllData['Stratum'].isin(needed_stratum)]

    new_data = AllData[["LaCode", "q2c", "Stratum"]]
    new_data = new_data.fillna(0)
    #unliked_numbers = [-9,0]
    cleaned_data = new_data
    unique_council = AllData['LaCode'].unique()
    for council in unique_council:
        per_council = cleaned_data[cleaned_data['LaCode'] == council]
        per_council = per_council[per_council["q2c"] != 0]
        count_strata = per_council.groupby(["Stratum"]).count()
        count_strata = count_strata.reset_index()
        count_strata['LaCode'] = council

        EligiblePopulation = params.EligiblePopulation

        EligiblePopulation['Stratum_2c'] = EligiblePopulation[["m1864PhysSuppCommunity", "m1864SensSuppCommunity", "m1864MemCogSuppCommunity", "m1864MentHealthCommunity", "m1864SocSuppCommunity",
                                                               "f1864PhysSuppCommunity", "f1864SensSuppCommunity", "f1864MemCogSuppCommunity", "f1864MentHealthCommunity",
                                                               "f1864SocSuppCommunity", "o1864PhysSuppCommunity", "o1864SensSuppCommunity", "o1864MemCogSuppCommunity", "o1864MentHealthCommunity",
                                                               "o1864SocSuppCommunity"]].sum(axis=1)

        epop = EligiblePopulation[["LaCode", "stratum4Pop", "Stratum_2c"]]

        epop_strat = epop[epop['LaCode'] == council]

        epop_melt = pd.melt(epop_strat, id_vars=['LaCode'])
        weights = pd.DataFrame(columns=['weights'])


        # ADDED STRATUM 5 TO REP STRATUM Q2C
        epop_melt['Stratum'] = [4, 2]

        merge = count_strata.merge(epop_melt, on="Stratum", how='left')

        merge['w'] = merge['value']/merge["q2c"]

        per_council = per_council.groupby(["q2c", 'Stratum']).count()

        per_council = per_council.reset_index()

        per_council.rename(columns={"LaCode": "count"}, inplace=True)

        per_council['LaCode'] = council

        to_be_mergde_with_responses = merge[["Stratum", "w", "LaCode_x"]]

        merged_with_responses = per_council.merge(
            to_be_mergde_with_responses, on="Stratum", how="left")

        merged_with_responses['weighted_count'] = merged_with_responses['count'] * \
            merged_with_responses['w']

        merged_no_zeros = merged_with_responses[merged_with_responses["q2c"] != 0]

        merged_no_zeros_groupby = merged_no_zeros.groupby(["q2c"]).sum()

        merged_no_zeros_groupby = merged_no_zeros_groupby.reset_index()

        merged_no_zeros_groupby['sum'] = merged_no_zeros_groupby['weighted_count'].sum(
        )

        merged_no_zeros_groupby['Proportion'] = (
            merged_no_zeros_groupby['weighted_count']/merged_no_zeros_groupby['sum']) * 100

        final_merge = merged_no_zeros_groupby[["q2c", 'Proportion']]

        final_merge['LaCode'] = council

        final_merge['Question'] = "q2c"

        final_merge.rename(columns={"q2c": "response_numbers"}, inplace=True)

        final_merge["response_numbers"] = final_merge["response_numbers"].astype(
            int)

        final_merge["Admin_Data_Item"] = final_merge["Question"] + \
            "response" + final_merge["response_numbers"].astype(str)
        all_q2c = pd.concat([final_merge, all_q2c])

        all = pd.concat([all_q2c, all_councils])

    return all


def calculate_mean_and_STD(all_councils):
    unique_admin = all_councils['Admin_Data_Item'].unique()
    denominator = all_councils['LaCode'].nunique()

    appended = pd.DataFrame([])
    appended_v = pd.DataFrame([])

    all_councils_v = all_councils[all_councils["Question"].isin(
        params.voluntary_questions)]

    for u in unique_admin:
        Admin_Data_Item_Data = all_councils_v[all_councils_v['Admin_Data_Item'] == u]

        Admin_Data_Item_Data['Mean'] = Admin_Data_Item_Data['Proportion'].mean()
        Admin_Data_Item_Data['STD'] = Admin_Data_Item_Data['Proportion'].std()

        appended_v = pd.concat([Admin_Data_Item_Data, appended_v])

    all_councils = all_councils[~all_councils["Question"].isin(
        params.voluntary_questions)]

    for u in unique_admin:
        Admin_Data_Item_Data = all_councils[all_councils['Admin_Data_Item'] == u]

        Admin_Data_Item_Data['tot'] = Admin_Data_Item_Data['Proportion'].sum()
        Admin_Data_Item_Data['Mean'] = Admin_Data_Item_Data['tot']/denominator
        Admin_Data_Item_Data['STD'] = Admin_Data_Item_Data['Proportion'].std()
        del Admin_Data_Item_Data['tot']

        appended = pd.concat([Admin_Data_Item_Data, appended])

        a = pd.concat([appended, appended_v])

    return a


def add_proportions_last_year(appended):
    # edit for the previous year's data
    inputs = params.last_years_files

    Dataset = 'SURV_QUESTION_RESP_PROP.csv'
    last_years_data = pd.read_csv(inputs+Dataset, header=0, low_memory=False)
    last_years_data = last_years_data[[
        'LaCode', 'Admin_Data_Item', 'Proportions']]
    all_prop = appended.merge(
        last_years_data, on=['LaCode', 'Admin_Data_Item'], how='outer')

    all_prop.fillna(0, inplace=True)
    del all_prop["Mean"]
    del all_prop["STD"]
    Mean_STD = appended[["Admin_Data_Item", "Mean", "STD"]]
    all_prop = all_prop.merge(Mean_STD, on=["Admin_Data_Item"], how="left")

    all_prop.rename(
        columns={'Proportions': 'Proportions_last_year'}, inplace=True)
    all_prop['upper'] = all_prop['Mean'] + (2 * all_prop['STD'])
    all_prop['lower'] = all_prop['Mean'] - (2 * all_prop['STD'])
    all_prop['Flagged'] = all_prop['Proportion'].between(
        all_prop['lower'], all_prop['upper'])
    all_prop['Flagged'] = np.where((all_prop['Flagged'] == False), 1, 0)
    all_prop.rename(columns={'Proportion': 'Proportions'}, inplace=True)

    return all_prop[['LaCode', 'Question', 'Admin_Data_Item', 'Proportions', 'Proportions_last_year', 'Mean', 'STD', 'Flagged']]


def main():
    eligible = epop()
    importing = imports()
    stratum = weights(importing, eligible)
    two_c = q2c(stratum, importing)
    mean = calculate_mean_and_STD(two_c)
    last_year_data = add_proportions_last_year(mean)
    last_year_data[['Proportions', 'Mean', 'STD']
                   ] = last_year_data[['Proportions', 'Mean', 'STD']].round(1)
    last_year_data.drop_duplicates(inplace=True)
    last_year_data.to_csv(output+"SURV_QUESTION_RESP_PROP.csv")
    return last_year_data


create = main()
create
