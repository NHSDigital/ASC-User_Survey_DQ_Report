# Put together and loop
import pandas as pd
import numpy as np
import params
from q2c import q2c_people as calc_q2c


output = params.output


def imports():
    inputs = params.input
    Dataset = 'cleaned_questionnaire.csv'
    AllData = pd.read_csv(inputs+Dataset, header=0, low_memory=False)
    return AllData


def response_rates(AllData):

    unique = AllData['LaCode'].unique()
    question = AllData.filter(regex=("^q"))
    #all_questions = pd.DataFrame([])
    all_response_rates = pd.DataFrame([])

    for la, q in zip(unique, question):

        # for the coucils response rate

        Filtered_council = AllData[AllData['LaCode'] == la]
        Filtered_council = Filtered_council[['LaCode', 'Response']]
        Filtered_council = Filtered_council.fillna(0.0)
        grouped = Filtered_council.groupby(['Response']).sum()
        grouped = grouped.reset_index()
        grouped['Total'] = grouped['LaCode'].sum()
        grouped['Response rate'] = (grouped['LaCode'] / grouped['Total']) * 100

        grouped = grouped[grouped['Response'] == 1]
        
        grouped['Total_proportion'] = grouped['Response rate']
        grouped['Question'] = 'ResponseRate'
        grouped['LaCode'] = la
        grouped = grouped[['LaCode', 'Question',
                           'Total_proportion', 'Response rate']]
        all_response_rates = pd.concat([all_response_rates, grouped])

    return all_response_rates


def council_question_response_rates(AllData):
    # now for the rest of the individual council x question response rates

    unique = AllData['LaCode'].unique()
    question = AllData.filter(regex=("^q"))
    all_questions = pd.DataFrame([])
    

    for la in unique:

        filtered_council = AllData[AllData['LaCode'] == la]
        response_filtered_council = filtered_council[filtered_council['Response'] == 1]

        for q in question:
            question_filtered_council = response_filtered_council[[
                'LaCode', q]]
            na_filtered_council = question_filtered_council.fillna(0.0)

            Grouped = na_filtered_council.groupby([q]).sum()
            Grouped = Grouped.reset_index()
            Grouped['Total'] = Grouped['LaCode'].sum()
            Grouped['Proportion'] = (
                Grouped['LaCode'] / Grouped['Total']) * 100
            Grouped = Grouped[Grouped[q] != 0.0]
            Grouped['Total_proportion'] = Grouped['Proportion'].sum()

            Grouped['Question'] = q
            Grouped['LaCode'] = la
            new_group = Grouped[[
                'LaCode', 'Total_proportion', 'Question']].drop_duplicates()
            all_questions = pd.concat([all_questions, new_group])

    return all_questions


def q2c(all_questions, AllData):

    all_questions = all_questions[all_questions['Question'] != "q2c"]

    q2c_numbers = calc_q2c(AllData)

    all_questions = pd.concat([all_questions, q2c_numbers])

    return all_questions


def England(AllData):
    AllData['England'] = 1001
    Response_and_england = AllData[['Response', 'England']]
    grouped_england = Response_and_england.groupby(['Response']).sum()
    grouped_england = grouped_england.reset_index()
    grouped_england['Total'] = grouped_england['England'].sum()
    grouped_england['Total_proportion'] = (
        grouped_england['England'] / grouped_england['Total']) * 100
    grouped_england['LaCode'] = 1001
    grouped_england['Question'] = 'ResponseRate'
    grouped_england = grouped_england[grouped_england['Response'] == 1]
    grouped_england['Response_Rate'] = grouped_england['Total_proportion']

    # calculating the council response rates

    unique = AllData['LaCode'].unique()
    all_council = pd.DataFrame([])
    for u in unique:
        single_council = AllData[AllData['LaCode'] == u]
        single_council = single_council[['Response', 'LaCode']]
        grouped_council = single_council.groupby(['Response']).sum()
        grouped_council = grouped_council.reset_index()
        grouped_council['Total'] = grouped_council['LaCode'].sum()
        grouped_council['Total_proportion'] = (
            grouped_council['LaCode'] / grouped_council['Total']) * 100
        grouped_council['LaCode'] = u
        grouped_council['Question'] = 'ResponseRate'
        grouped_council = grouped_council[grouped_council['Response'] == 1]
        grouped_council['Response_Rate'] = grouped_council['Total_proportion']

        all_council = pd.concat([all_council, grouped_council])
    all_council['Mean'] = all_council['Total_proportion'].mean()
    all_council['STD'] = all_council['Total_proportion'].std()

    # modifying england
    grouped_england['Mean'] = all_council['Mean'].mean()
    grouped_england['STD'] = all_council['STD'].mean()
    all_england_council = pd.concat([grouped_england, all_council])
    return all_england_council[["Total_proportion", "LaCode", "Question", "Response_Rate", "Mean", "STD"]]

    



def mean_and_std(concat, AllData):

    question = AllData.filter(regex=("^q"))

    all_questions = pd.DataFrame([])
    for q in question:

        filter_question = concat[concat['Question'] == q]
        filter_question['Mean'] = filter_question['Total_proportion'].mean()
        filter_question['STD'] = filter_question['Total_proportion'].std()
        all_questions = pd.concat([all_questions, filter_question])
    filter_response = concat[concat['Question'] == 'ResponseRate']
    response = pd.concat([filter_response, all_questions])

    return response


def add_proportions_last_year(response_and_question):
    # edit for the previous year's data
    inputs = params.last_years_files
    Dataset = 'SURV_RESP_RATES_ASCS.csv'
    last_years_data = pd.read_csv(inputs+Dataset, header=0, low_memory=False)
    last_years_data['LaCode'].astype(float)
    last_years_data = last_years_data[['Question', 'LaCode', 'Proportions']]
    response_and_question['LaCode'].astype(float)

    last_years_data.rename(
        columns={'Proportions': 'Proportions_last_year'}, inplace=True)
    all_prop = response_and_question.merge(
        last_years_data, on=['Question', 'LaCode'], how='outer')
    # add upper and lower limit

    all_prop['upper'] = all_prop['Mean'] + (2 * all_prop['STD'])
    all_prop['lower'] = all_prop['Mean'] - (2 * all_prop['STD'])

    #####
    # calculate if flagged

    all_prop['Flagged'] = all_prop['Total_proportion'].between(
        all_prop['lower'], all_prop['upper'])
    all_prop.rename(columns={'Total_proportion': 'Proportions'}, inplace=True)

    all_prop['Flagged'] = np.where((all_prop['Flagged'] == False), 1, 0)

    all_prop.fillna(0, inplace=True)
    all_prop.loc[all_prop['Proportions'] == 0, ["Flagged"]] = 0

    # merge council

    return all_prop[['LaCode', 'Question', 'Proportions', 'Proportions_last_year', 'Response_Rate', 'Mean', 'STD', 'Flagged']]


def main():
    import_data = imports()
    questions = council_question_response_rates(import_data)
    Eng = England(import_data)
    calculation_q2c = q2c(questions, import_data)
    concat = pd.concat([Eng, calculation_q2c])
    mean = mean_and_std(concat, import_data)
    proportions = add_proportions_last_year(mean)
    proportions[['Proportions', 'Response_Rate', 'Mean', 'STD']] = proportions[[
        'Proportions', 'Response_Rate', 'Mean', 'STD']].round(1)
    return proportions


create = main()
create.to_csv(output+"SURV_RESP_RATES_ASCS.csv")
