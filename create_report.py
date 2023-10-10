# -*- coding: utf-8 -*-
"""
Created on Mon Nov  8 21:18:49 2021

@author: makh2
"""


from datetime import datetime
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
import docx
import pandas as pd
import csv
import matplotlib.pyplot as plt
import os
import params


# Where all required input files (below) are stored
filepath = params.filepath
# Base template report
DQ_report_template = params.DQ_report_template
word_templates = [filepath+DQ_report_template]
# Where DQ reports will be saved to
output_filepath = params.output_filepath
todays_date = datetime.today().strftime('%d %B %Y')


col_list = ["LaCode", "LaName"]
CASSR_csv_data = pd.read_csv(
    params.CASSR_csv_data, usecols=col_list)
CASSR_csv_data = CASSR_csv_data.set_index('LaCode')
CASSR_csv_data = CASSR_csv_data.to_dict('index')

CASSR_to_run_for = input(
    "\nPlease enter the codes of the CASSRs that you would like to create validation report for, separated by commas, and hit return.\nTo run for all CASSRs, enter *\n\n")
current_year = int(input("\nWhat is the end year you'd like?  (YYYY)\n\n"))
previous_year = current_year - 1
current_string = str(current_year-1) + '-' + str(current_year)[-2:]
previous_string = str(previous_year-1) + '-' + str(previous_year)[-2:]

CASSR_data = {}  # Empty dictionary, to be filled with relevant information for each LA

print('\nPulling data from CSV files into python.')

# This section is gathering CASSR code and name only
if CASSR_to_run_for == '*':  # If running the script for all CASSRs
    # List of CASSRs (empty, will populate below)
    CASSR_code_list = list(CASSR_csv_data.keys())

    for cassr in CASSR_code_list:
        CASSR_data[cassr] = {}
        # Is assigning CASSR_data[102] to {'CASSR name': 'Cumbria'}
        CASSR_data[cassr]['CASSR name'] = CASSR_csv_data[cassr]['LaName']

else:   # If running the script for select CASSRs
    # Splitting the CASSRs that the user has been prompted to provide into a list
    CASSR_code_list = CASSR_to_run_for.split(",")
    # Converting each CASSR code into integer format
    CASSR_code_list = [int(x) for x in CASSR_code_list]
    CASSR_check = []
    for x in CASSR_code_list:  # Pulling data from SQL for each CASSR in turn
        CASSR_data[int(x)] = {}
        CASSR_data[int(x)]['CASSR name'] = CASSR_csv_data[int(x)]['LaName']
        # Appending CASSR code to list IF that CASSR ID exists. If invalid number entered, it won't be added to this list
        CASSR_check.append(int(x))
    for x in CASSR_code_list:
        if x in CASSR_check:  # All CASSRs that correspond to a CASSR code that the users has provided
            continue
        else:  # If the provided CASSR ID doesn't correspond to a CASSR in the database.
            print('\nA CASSR with code ' + str(x) +
                  ' is not in the CSV file. Please check the number.')

    if len(CASSR_check) == 0:
        exit  # Cancelling the script if no correct CASSR codes have been provided

    CASSR_code_list = CASSR_check


####################################Gathering data for each CASSR#####################
Lot_Previous, Lot_Current, Lot_Mean_STD = {}, {}, {}
Lot_England = {}
CASSR_code_list = [str(x) for x in CASSR_code_list]

csv_2 = [params.SURV_ADMIN_DATA_PROP, params.SURV_MISSING_ADMIN_DATA,
         params.SURV_RESP_RATES_ASCS, params.SURV_QUESTION_RESP_PROP]

csv_3 = [params.SURV_ADMIN_MEAN_STD, params.SURV_MISSING_ADMIN_MEAN_STD,
         params.SURV_RESP_RATES_ASCS, params.SURV_QUESTION_RESP_PROP]

csv_4 = [params.SURV_ADMIN_MEAN_STD,
         params.SURV_MISSING_ADMIN_MEAN_STD]

# Tables 1 - 4 Data
csv_1 = pd.read_csv(
    params.SURV_ELIGIBLE_POP_SAMPLE_SIZE, index_col='LaCode')
csv_1 = csv_1.fillna(0.0)
table1_4_csv = csv_1.to_dict('index')
England_table1_4_csv = table1_4_csv[1001]
table1_4_csv = {k: table1_4_csv[int(k)] for k in CASSR_code_list}


# England Data
for csv_doc in csv_4:
    Lot_England[csv_doc] = {}
    new_csv_dict = {}
    with open(csv_doc, 'r') as data_file:
        data = csv.DictReader(data_file, delimiter=",")
        for row in data:
            item = new_csv_dict.get(row['LaCode'], dict())
            item[row['Admin_Data_Item']] = row['Mean'], row['STD']
            new_csv_dict[row['LaCode']] = item
    Lot_England[csv_doc] = new_csv_dict

# Previous Years Data
for csv_doc in csv_2:
    Lot_Previous[csv_doc] = {}
    new_csv_dict = {}
    if ((csv_doc == csv_2[0]) or (csv_doc == csv_2[1])):
        with open(csv_doc, 'r') as data_file:
            data = csv.DictReader(data_file, delimiter=",")
            for row in data:
                if (row['LaCode'] in CASSR_code_list):
                    item = new_csv_dict.get(row['LaCode'], dict())
                    if not row['Proportions_last_year']:
                        row['Proportions_last_year'] = '0.0'
                        item[row['Admin_Data_Item']
                             ] = row['Proportions_last_year']
                    else:
                        item[row['Admin_Data_Item']
                             ] = row['Proportions_last_year']
                    new_csv_dict[row['LaCode']] = item
        Lot_Previous[csv_doc] = new_csv_dict
    elif ((csv_doc == csv_2[2])):
        with open(csv_doc, 'r') as data_file:
            data = csv.DictReader(data_file, delimiter=",")
            for row in data:
                if (row['LaCode'] in CASSR_code_list):
                    item = new_csv_dict.get(row['LaCode'], dict())
                    if not row['Proportions_last_year']:
                        row['Proportions_last_year'] = '0.0'
                        item[row['Question']] = row['Proportions_last_year']
                    else:
                        item[row['Question']] = row['Proportions_last_year']
                    new_csv_dict[row['LaCode']] = item
        Lot_Previous[csv_doc] = new_csv_dict
    elif ((csv_doc == csv_2[3])):
        with open(csv_doc, 'r') as data_file:
            data = csv.DictReader(data_file, delimiter=",")
            for row in data:
                if (row['LaCode'] in CASSR_code_list):
                    item = new_csv_dict.get(row['LaCode'], dict())
                    if not row['Proportions_last_year']:
                        row['Proportions_last_year'] = '0.0'
                        item[row['Admin_Data_Item']
                             ] = row['Proportions_last_year']
                    else:
                        item[row['Admin_Data_Item']
                             ] = row['Proportions_last_year']
                    new_csv_dict[row['LaCode']] = item
        Lot_Previous[csv_doc] = new_csv_dict


# Current Years Data
for csv_doc in csv_2:
    Lot_Current[csv_doc] = {}
    new_csv_dict = {}
    if ((csv_doc == csv_2[0]) or (csv_doc == csv_2[1])):
        with open(csv_doc, 'r') as data_file:
            data = csv.DictReader(data_file, delimiter=",")
            for row in data:
                if (row['LaCode'] in CASSR_code_list):
                    item = new_csv_dict.get(row['LaCode'], dict())
                    if not row['Proportions']:
                        row['Proportions'] = '0.0'
                        item[row['Admin_Data_Item']
                             ] = row['Proportions'], row['Flagged']
                    else:
                        item[row['Admin_Data_Item']
                             ] = row['Proportions'], row['Flagged']
                    new_csv_dict[row['LaCode']] = item
        Lot_Current[csv_doc] = new_csv_dict
    elif ((csv_doc == csv_2[2])):
        with open(csv_doc, 'r') as data_file:
            data = csv.DictReader(data_file, delimiter=",")
            for row in data:
                if (row['LaCode'] in CASSR_code_list):
                    item = new_csv_dict.get(row['LaCode'], dict())
                    if not row['Proportions']:
                        row['Proportions'] = '0.0'
                        item[row['Question']] = row['Proportions'], row['Flagged']
                    else:
                        item[row['Question']] = row['Proportions'], row['Flagged']
                    new_csv_dict[row['LaCode']] = item
        Lot_Current[csv_doc] = new_csv_dict
    elif ((csv_doc == csv_2[3])):
        with open(csv_doc, 'r') as data_file:
            data = csv.DictReader(data_file, delimiter=",")
            for row in data:
                if (row['LaCode'] in CASSR_code_list):
                    item = new_csv_dict.get(row['LaCode'], dict())
                    if not row['Proportions']:
                        row['Proportions'] = '0.0'
                        item[row['Admin_Data_Item']
                             ] = row['Proportions'], row['Flagged']
                    else:
                        item[row['Admin_Data_Item']
                             ] = row['Proportions'], row['Flagged']
                    new_csv_dict[row['LaCode']] = item
        Lot_Current[csv_doc] = new_csv_dict

# Mean and STD Data
for csv_doc in csv_3:
    Lot_Mean_STD[csv_doc] = {}
    new_csv_dict = {}
    if ((csv_doc == csv_3[0]) or (csv_doc == csv_3[1])):
        with open(csv_doc, 'r') as data_file:
            data = csv.DictReader(data_file, delimiter=",")
            for row in data:
                if (row['LaCode'] in CASSR_code_list):
                    item = new_csv_dict.get(row['LaCode'], dict())
                    if not row['Mean']:
                        row['Mean'] = '0.0'
                        item[row['Admin_Data_Item']] = row['Mean'], row['STD']
                    elif not row['STD']:
                        row['STD'] = '0.0'
                        item[row['Admin_Data_Item']] = row['Mean'], row['STD']
                    else:
                        item[row['Admin_Data_Item']] = row['Mean'], row['STD']
                    new_csv_dict[row['LaCode']] = item
        Lot_Mean_STD[csv_doc] = new_csv_dict
    elif ((csv_doc == csv_3[2])):
        with open(csv_doc, 'r') as data_file:
            data = csv.DictReader(data_file, delimiter=",")
            for row in data:
                if (row['LaCode'] in CASSR_code_list):
                    item = new_csv_dict.get(row['LaCode'], dict())
                    if not row['Mean']:
                        row['Mean'] = '0.0'
                        item[row['Question']] = row['Mean'], row['STD']
                    elif not row['STD']:
                        row['STD'] = '0.0'
                        item[row['Question']] = row['Mean'], row['STD']
                    else:
                        item[row['Question']] = row['Mean'], row['STD']
                    new_csv_dict[row['LaCode']] = item
        Lot_Mean_STD[csv_doc] = new_csv_dict
    elif ((csv_doc == csv_3[3])):
        with open(csv_doc, 'r') as data_file:
            data = csv.DictReader(data_file, delimiter=",")
            for row in data:
                if (row['LaCode'] in CASSR_code_list):
                    item = new_csv_dict.get(row['LaCode'], dict())
                    if not row['Mean']:
                        row['Mean'] = '0.0'
                        item[row['Admin_Data_Item']] = row['Mean'], row['STD']
                    elif not row['STD']:
                        row['STD'] = '0.0'
                        item[row['Admin_Data_Item']] = row['Mean'], row['STD']
                    else:
                        item[row['Admin_Data_Item']] = row['Mean'], row['STD']
                    new_csv_dict[row['LaCode']] = item
        Lot_Mean_STD[csv_doc] = new_csv_dict

for CASSR_code in CASSR_code_list:

    CASSR_data[int(CASSR_code)]['tbl_1'], CASSR_data[int(CASSR_code)]['tbl_2'], CASSR_data[int(
        CASSR_code)]['tbl_3'], CASSR_data[int(CASSR_code)]['tbl_4'] = [], [], [], []
    CASSR_data[int(CASSR_code)]['tbl_1_1'], CASSR_data[int(
        CASSR_code)]['tbl_2_1'] = [], []
    CASSR_data[int(CASSR_code)]['tbl_5a'], CASSR_data[int(CASSR_code)]['tbl_5b'], CASSR_data[int(
        CASSR_code)]['tbl_6a'], CASSR_data[int(CASSR_code)]['tbl_6b'] = [], [], [], []
    CASSR_data[int(CASSR_code)]['tbl_7a'], CASSR_data[int(
        CASSR_code)]['tbl_7b'] = [], []
    CASSR_data[int(CASSR_code)]['tbl_8a'], CASSR_data[int(CASSR_code)]['tbl_8b'], CASSR_data[int(
        CASSR_code)]['tbl_8c'], CASSR_data[int(CASSR_code)]['tbl_8d'] = [], [], [], []

    # Table 1

    positions = ['SALT_total', 'Eligible population']
    for position in positions:
        value = int(table1_4_csv[CASSR_code][position])
        CASSR_data[int(CASSR_code)]['tbl_1'].append(
            {'Measure': position, 'Value': value})

    positions = ['SALT_Stratum_1', 'SALT_Stratum_2', 'SALT_Stratum_3', 'SALT_Stratum_4', 'Stratum 1 proportion_EP', 'Stratum 2  proportion_EP', 'Stratum 3 proportion_EP',
                 'Stratum 4 proportion_EP', 'Stratum_1_Diff_to_SALT', 'Stratum_2_Diff_to_SALT', 'Stratum_3_Diff_to_SALT', 'Stratum_4_Diff_to_SALT', 'Rounded percentage']
    for position in positions:
        value = float(table1_4_csv[CASSR_code][position])
        CASSR_data[int(CASSR_code)]['tbl_1_1'].append(
            {'Measure': position, 'Value': value})
    if ((CASSR_data[int(CASSR_code)]['tbl_1_1'][12]['Value'] < -20) or (CASSR_data[int(CASSR_code)]['tbl_1_1'][12]['Value'] > 20)):
        CASSR_data[int(CASSR_code)]['tbl_1_1'][12]['cell_colour'] = 'FF0000'

    # Table 2

    positions = ['Eligible population', 'Total Sample Size']
    for position in positions:
        value = int(table1_4_csv[CASSR_code][position])
        CASSR_data[int(CASSR_code)]['tbl_2'].append(
            {'Measure': position, 'Value': value})

    positions = ['Stratum 1 proportion_EP', 'Stratum 2  proportion_EP', 'Stratum 3 proportion_EP', 'Stratum 4 proportion_EP', 'Stratum 1 proportion_SS', 'Stratum 2 proportion_SS',
                 'Stratum 3 proportion_SS', 'Stratum 4 proportion_SS', 'Stratum_1_Sample', 'Stratum_2_Sample', 'Stratum_3_Sample', 'Stratum_4_Sample', 'Difference_sample_EP']
    for position in positions:
        value = float(table1_4_csv[CASSR_code][position])
        CASSR_data[int(CASSR_code)]['tbl_2_1'].append(
            {'Measure': position, 'Value': value})

    # Table 3
    positions = ['Stratum 1 proportion_EP', 'Stratum 2  proportion_EP', 'Stratum 3 proportion_EP', 'Stratum 4 proportion_EP',
                 'Stratum_1_diff_to_Eng', 'Stratum_2_diff_to_Eng', 'Stratum_3_diff_to_Eng', 'Stratum_4_diff_to_Eng']
    for position in positions:
        value = float(table1_4_csv[CASSR_code][position])
        CASSR_data[int(CASSR_code)]['tbl_3'].append(
            {'Measure': position, 'Value': value})
    eng_positions = ['Stratum 1 proportion_EP', 'Stratum 2  proportion_EP',
                     'Stratum 3 proportion_EP', 'Stratum 4 proportion_EP']
    for position in eng_positions:
        value = float(England_table1_4_csv[position])
        CASSR_data[int(CASSR_code)]['tbl_3'].append(
            {'Measure': position, 'Value': value})

    # Table 4
    positions = ['Stratum 1 proportion_SS', 'Stratum 2 proportion_SS', 'Stratum 3 proportion_SS', 'Stratum 4 proportion_SS',
                 'Stratum_1_diff_to_Eng _sample', 'Stratum_2_diff_to_Eng _sample', 'Stratum_3_diff_to_Eng _sample', 'Stratum_4_diff_to_Eng_sample']
    for position in positions:
        value = float(table1_4_csv[CASSR_code][position])
        CASSR_data[int(CASSR_code)]['tbl_4'].append(
            {'Measure': position, 'Value': value})
    eng_positions = ['Stratum 1 proportion_SS', 'Stratum 2 proportion_SS',
                     'Stratum 3 proportion_SS', 'Stratum 4 proportion_SS']
    for position in eng_positions:
        value = float(England_table1_4_csv[position])
        CASSR_data[int(CASSR_code)]['tbl_4'].append(
            {'Measure': position, 'Value': value})

    # Graph
    salt_total = CASSR_data[int(CASSR_code)]['tbl_1'][0]['Value']
    eligibility_total = CASSR_data[int(CASSR_code)]['tbl_1'][1]['Value']

    # Table 5a Whites

    link_c_p = params.SURV_ADMIN_DATA_PROP
    link_m = params.SURV_ADMIN_MEAN_STD
    positions = ['MethodCollection1', 'MethodCollection2', 'MethodCollection3', 'MethodCollection4', 'AgeBand1', 'AgeBand2', 'AgeBand3', 'AgeBand4', 'AgeBand5', 'AgeBand6', 'AgeBand7', 'AgeBand8',
                 'Questionnaire1', 'Questionnaire2', 'Questionnaire3', 'Sexuality1', 'Sexuality2', 'Sexuality3', 'Sexuality4', 'Sexuality5', 'Sexuality6', 'PSR1', 'PSR2', 'PSR3', 'PSR4', 'PSR5', 'PSR6',
                 'MechanismofDelivery1', 'MechanismofDelivery2', 'MechanismofDelivery3', 'MechanismofDelivery4', 'MechanismofDelivery5', 'RHC_asperger1', 'RHC_asperger2', 'Interpreter1', 'Interpreter2', 'Translated_Recoded1', 'Translated_Recoded2']
    for position in positions:
        if position not in Lot_Previous[link_c_p][CASSR_code].keys():
            value = '0.0'
            CASSR_data[int(CASSR_code)]['tbl_5a'].append(
                {'Measure Previous': position, 'Value': value, 'cell_colour': 'FFFFFF'})
        else:
            value = float(Lot_Previous[link_c_p][CASSR_code][position])
            CASSR_data[int(CASSR_code)]['tbl_5a'].append(
                {'Measure Previous': position, 'Value': value, 'cell_colour': 'FFFFFF'})

    for position in positions:
        if position not in Lot_Current[link_c_p][CASSR_code].keys():
            value = '0.0'
            CASSR_data[int(CASSR_code)]['tbl_5a'].append(
                {'Measure Current': position, 'Value': value, 'cell_colour': 'FFFFFF'})
        else:
            if (Lot_Current[link_c_p][CASSR_code][position][1] == '1'):
                colour = 'FF0000'
            else:
                colour = 'FFFFFF'
            value = float(Lot_Current[link_c_p][CASSR_code][position][0])
            CASSR_data[int(CASSR_code)]['tbl_5a'].append(
                {'Measure Current': position, 'Value': value, 'cell_colour': colour})

    for position in positions:
        if position not in Lot_England[link_m]['1001'].keys():
            value = '0.0'
            CASSR_data[int(CASSR_code)]['tbl_5a'].append(
                {'Measure Mean': position, 'Value': value, 'cell_colour': 'FFFFFF'})
            CASSR_data[int(CASSR_code)]['tbl_5a'].append(
                {'Measure STD': position, 'Value': value, 'cell_colour': 'FFFFFF'})
        else:
            value = float(Lot_England[link_m]['1001'][position][0])
            value1 = float(Lot_England[link_m]['1001'][position][1])
            CASSR_data[int(CASSR_code)]['tbl_5a'].append(
                {'Measure Mean': position, 'Value': value, 'cell_colour': 'FFFFFF'})
            CASSR_data[int(CASSR_code)]['tbl_5a'].append(
                {'Measure STD': position, 'Value': value1, 'cell_colour': 'FFFFFF'})

    # Table 5b Greys

    link_c_p = params.SURV_ADMIN_DATA_PROP
    link_m = params.SURV_ADMIN_MEAN_STD
    positions = ['Response1', 'Response2', 'Response3', 'Gender1', 'Gender2', 'Gender3', 'Ethnicity1', 'Ethnicity2', 'Ethnicity3', 'Ethnicity4', 'Ethnicity5', 'Ethnicity6',
                 'Religion1', 'Religion2', 'Religion3', 'Religion4', 'Religion5', 'Religion6', 'Religion7', 'Religion8', 'Religion99', 'SupportSetting1', 'SupportSetting2', 'SupportSetting3',
                 'RHC_autism1', 'RHC_autism2', 'Advocate1', 'Advocate2', 'Replacement1', 'Replacement2']

    for position in positions:
        if position not in Lot_Previous[link_c_p][CASSR_code].keys():
            value = '0.0'
            CASSR_data[int(CASSR_code)]['tbl_5b'].append(
                {'Measure Previous': position, 'Value': value, 'cell_colour': 'D9D9D9'})
        else:
            value = float(Lot_Previous[link_c_p][CASSR_code][position])
            CASSR_data[int(CASSR_code)]['tbl_5b'].append(
                {'Measure Previous': position, 'Value': value, 'cell_colour': 'D9D9D9'})

    for position in positions:
        if position not in Lot_Current[link_c_p][CASSR_code].keys():
            value = '0.0'
            CASSR_data[int(CASSR_code)]['tbl_5b'].append(
                {'Measure Current': position, 'Value': value, 'cell_colour': 'D9D9D9'})
        else:
            if (Lot_Current[link_c_p][CASSR_code][position][1] == '1'):
                colour = 'FF0000'
            else:
                colour = 'D9D9D9'
            value = float(Lot_Current[link_c_p][CASSR_code][position][0])
            CASSR_data[int(CASSR_code)]['tbl_5b'].append(
                {'Measure Current': position, 'Value': value, 'cell_colour': colour})

    for position in positions:
        if position not in Lot_England[link_m]['1001'].keys():
            value = '0.0'
            CASSR_data[int(CASSR_code)]['tbl_5b'].append(
                {'Measure Mean': position, 'Value': value, 'cell_colour': 'D9D9D9'})
            CASSR_data[int(CASSR_code)]['tbl_5b'].append(
                {'Measure STD': position, 'Value': value, 'cell_colour': 'D9D9D9'})
        else:
            value = float(Lot_England[link_m]['1001'][position][0])
            value1 = float(Lot_England[link_m]['1001'][position][1])
            CASSR_data[int(CASSR_code)]['tbl_5b'].append(
                {'Measure Mean': position, 'Value': value, 'cell_colour': 'D9D9D9'})
            CASSR_data[int(CASSR_code)]['tbl_5b'].append(
                {'Measure STD': position, 'Value': value1, 'cell_colour': 'D9D9D9'})

    # Table 6 White
    link_c_p = params.SURV_MISSING_ADMIN_DATA
    link_m = params.SURV_MISSING_ADMIN_MEAN_STD
    positions = ['MethodCollectionMissing', 'AgeBandMissing', 'EthnicityMissing', 'ReligionMissing',
                 'QuestionnaireMissing', 'PSRMissing', 'RHC_aspergerMissing', 'Translated_RecodedMissing', 'InterpreterMissing']
    for position in positions:
        if CASSR_code + str(position) not in Lot_Previous[link_c_p][CASSR_code].keys():
            value = '0.0'
            CASSR_data[int(CASSR_code)]['tbl_6a'].append(
                {'Measure Previous': position, 'Value': value, 'cell_colour': 'FFFFFF'})
        else:
            value = float(Lot_Previous[link_c_p]
                          [CASSR_code][CASSR_code + str(position)])
            CASSR_data[int(CASSR_code)]['tbl_6a'].append(
                {'Measure Previous': position, 'Value': value, 'cell_colour': 'FFFFFF'})

    for position in positions:
        if CASSR_code + str(position) not in Lot_Current[link_c_p][CASSR_code].keys():
            value = '0.0'
            CASSR_data[int(CASSR_code)]['tbl_6a'].append(
                {'Measure Current': position, 'Value': value, 'cell_colour': 'FFFFFF'})
        else:
            if (Lot_Current[link_c_p][CASSR_code][CASSR_code + str(position)][1] == '1'):
                colour = 'FF0000'
            else:
                colour = 'FFFFFF'
            value = float(Lot_Current[link_c_p][CASSR_code]
                          [CASSR_code + str(position)][0])
            CASSR_data[int(CASSR_code)]['tbl_6a'].append(
                {'Measure Current': position, 'Value': value, 'cell_colour': colour})

    for position in positions:
        if position not in Lot_England[link_m]['1001'].keys():
            value = '0.0'
            CASSR_data[int(CASSR_code)]['tbl_6a'].append(
                {'Measure Mean': position, 'Value': value, 'cell_colour': 'FFFFFF'})
            CASSR_data[int(CASSR_code)]['tbl_6a'].append(
                {'Measure STD': position, 'Value': value, 'cell_colour': 'FFFFFF'})
        else:
            value = float(Lot_England[link_m]['1001'][position][0])
            value1 = float(Lot_England[link_m]['1001'][position][1])
            CASSR_data[int(CASSR_code)]['tbl_6a'].append(
                {'Measure Mean': position, 'Value': value, 'cell_colour': 'FFFFFF'})
            CASSR_data[int(CASSR_code)]['tbl_6a'].append(
                {'Measure STD': position, 'Value': value1, 'cell_colour': 'FFFFFF'})

    # Table 6 Grey
    link_c_p = params.SURV_MISSING_ADMIN_DATA
    link_m = params.SURV_MISSING_ADMIN_MEAN_STD
    positions = ['ResponseMissing', 'GenderMissing', 'SexualityMissing', 'SupportSettingMissing',
                 'MechanismofDeliveryMissing', 'RHC_autismMissing', 'ReplacementMissing', 'AdvocateMissing']
    for position in positions:
        if CASSR_code + str(position) not in Lot_Previous[link_c_p][CASSR_code].keys():
            value = '0.0'
            CASSR_data[int(CASSR_code)]['tbl_6b'].append(
                {'Measure Previous': position, 'Value': value, 'cell_colour': 'D9D9D9'})
        else:
            value = float(Lot_Previous[link_c_p]
                          [CASSR_code][CASSR_code + str(position)])
            CASSR_data[int(CASSR_code)]['tbl_6b'].append(
                {'Measure Previous': position, 'Value': value, 'cell_colour': 'D9D9D9'})

    for position in positions:
        if CASSR_code + str(position) not in Lot_Current[link_c_p][CASSR_code].keys():
            value = '0.0'
            CASSR_data[int(CASSR_code)]['tbl_6b'].append(
                {'Measure Current': position, 'Value': value, 'cell_colour': 'D9D9D9'})
        else:
            if (Lot_Current[link_c_p][CASSR_code][CASSR_code + str(position)][1] == '1'):
                colour = 'FF0000'
            else:
                colour = 'D9D9D9'
            value = float(Lot_Current[link_c_p][CASSR_code]
                          [CASSR_code + str(position)][0])
            CASSR_data[int(CASSR_code)]['tbl_6b'].append(
                {'Measure Current': position, 'Value': value, 'cell_colour': colour})

    for position in positions:
        if position not in Lot_England[link_m]['1001'].keys():
            value = '0.0'
            CASSR_data[int(CASSR_code)]['tbl_6b'].append(
                {'Measure Mean': position, 'Value': value, 'cell_colour': 'D9D9D9'})
            CASSR_data[int(CASSR_code)]['tbl_6b'].append(
                {'Measure STD': position, 'Value': value, 'cell_colour': 'D9D9D9'})
        else:
            value = float(Lot_England[link_m]['1001'][position][0])
            value1 = float(Lot_England[link_m]['1001'][position][1])
            CASSR_data[int(CASSR_code)]['tbl_6b'].append(
                {'Measure Mean': position, 'Value': value, 'cell_colour': 'D9D9D9'})
            CASSR_data[int(CASSR_code)]['tbl_6b'].append(
                {'Measure STD': position, 'Value': value1, 'cell_colour': 'D9D9D9'})

    # Table 7 White
    link_c_p_m = params.SURV_RESP_RATES_ASCS
    positions = ['ResponseRate', 'q2aComb', 'q2c', 'q3b', 'q4b', 'q5b', 'q6b', 'q7c', 'q8b',
                 'q9b', 'q11', 'q13', 'q15a', 'q16a', 'q16c', 'q17a', 'q17c', 'q18', 'q20a', 'q22']
    for position in positions:
        if position not in Lot_Previous[link_c_p_m][CASSR_code].keys():
            value = '0.0'
            CASSR_data[int(CASSR_code)]['tbl_7a'].append(
                {'Measure Previous': position, 'Value': value, 'cell_colour': 'FFFFFF'})
        else:
            value = float(Lot_Previous[link_c_p_m][CASSR_code][position])
            CASSR_data[int(CASSR_code)]['tbl_7a'].append(
                {'Measure Previous': position, 'Value': value, 'cell_colour': 'FFFFFF'})

    for position in positions:
        if position in ['Q4b', 'Q5b', 'Q6b', 'Q8b', 'Q9b']:
            if position not in Lot_Current[link_c_p_m][CASSR_code].keys():
                value = '0.0'
                CASSR_data[int(CASSR_code)]['tbl_7a'].append(
                    {'Measure Current': position, 'Value': value, 'cell_colour': 'FFFFFF'})
            else:
                if (Lot_Current[link_c_p_m][CASSR_code][position][0] == '0'):
                    value = float(
                        Lot_Current[link_c_p_m][CASSR_code][position][0])
                    CASSR_data[int(CASSR_code)]['tbl_7a'].append(
                        {'Measure Current': position, 'Value': value, 'cell_colour': 'FFFFFF'})

                else:
                    if (Lot_Current[link_c_p_m][CASSR_code][position][1] == '1'):
                        colour = 'FF0000'
                    else:
                        colour = 'FFFFFF'

                    value = float(
                        Lot_Current[link_c_p_m][CASSR_code][position][0])
                    CASSR_data[int(CASSR_code)]['tbl_7a'].append(
                        {'Measure Current': position, 'Value': value, 'cell_colour': colour})

        else:
            if position not in Lot_Current[link_c_p_m][CASSR_code].keys():
                value = '0.0'
                CASSR_data[int(CASSR_code)]['tbl_7a'].append(
                    {'Measure Current': position, 'Value': value, 'cell_colour': 'FFFFFF'})
            else:
                if (Lot_Current[link_c_p_m][CASSR_code][position][1] == '1'):
                    colour = 'FF0000'
                else:
                    colour = 'FFFFFF'
                value = float(Lot_Current[link_c_p_m][CASSR_code][position][0])
                CASSR_data[int(CASSR_code)]['tbl_7a'].append(
                    {'Measure Current': position, 'Value': value, 'cell_colour': colour})

    for position in positions:
        if position not in Lot_Mean_STD[link_c_p_m][CASSR_code].keys():
            value = '0.0'
            CASSR_data[int(CASSR_code)]['tbl_7a'].append(
                {'Measure Mean': position, 'Value': value, 'cell_colour': 'FFFFFF'})
            CASSR_data[int(CASSR_code)]['tbl_7a'].append(
                {'Measure STD': position, 'Value': value, 'cell_colour': 'FFFFFF'})
        else:
            value = float(Lot_Mean_STD[link_c_p_m][CASSR_code][position][0])
            value1 = float(Lot_Mean_STD[link_c_p_m][CASSR_code][position][1])
            CASSR_data[int(CASSR_code)]['tbl_7a'].append(
                {'Measure Mean': position, 'Value': value, 'cell_colour': 'FFFFFF'})
            CASSR_data[int(CASSR_code)]['tbl_7a'].append(
                {'Measure STD': position, 'Value': value1, 'cell_colour': 'FFFFFF'})

    # Table 7 Grey
    link_c_p_m = params.SURV_RESP_RATES_ASCS
    positions = ['q1Comb', 'q2b', 'q3a', 'q4a', 'q5a', 'q6a', 'q7a', 'q8a', 'q9a',
                 'q10', 'q12', 'q14', 'q15b', 'q16b', 'q16d', 'q17b', 'q17d', 'q19', 'q21a', 'q23a']
    for position in positions:
        if position not in Lot_Previous[link_c_p_m][CASSR_code].keys():
            value = '0.0'
            CASSR_data[int(CASSR_code)]['tbl_7b'].append(
                {'Measure Previous': position, 'Value': value, 'cell_colour': 'D9D9D9'})
        else:
            value = float(Lot_Previous[link_c_p_m][CASSR_code][position])
            CASSR_data[int(CASSR_code)]['tbl_7b'].append(
                {'Measure Previous': position, 'Value': value, 'cell_colour': 'D9D9D9'})

    for position in positions:
        if position not in Lot_Current[link_c_p_m][CASSR_code].keys():
            value = '0.0'
            CASSR_data[int(CASSR_code)]['tbl_7b'].append(
                {'Measure Current': position, 'Value': value, 'cell_colour': 'D9D9D9'})
        else:
            if (Lot_Current[link_c_p_m][CASSR_code][position][1] == '1'):
                colour = 'FF0000'
            else:
                colour = 'D9D9D9'
            value = float(Lot_Current[link_c_p_m][CASSR_code][position][0])
            CASSR_data[int(CASSR_code)]['tbl_7b'].append(
                {'Measure Current': position, 'Value': value, 'cell_colour': colour})

    for position in positions:
        if position not in Lot_Mean_STD[link_c_p_m][CASSR_code].keys():
            value = '0.0'
            CASSR_data[int(CASSR_code)]['tbl_7b'].append(
                {'Measure Mean': position, 'Value': value, 'cell_colour': 'D9D9D9'})
            CASSR_data[int(CASSR_code)]['tbl_7b'].append(
                {'Measure STD': position, 'Value': value, 'cell_colour': 'D9D9D9'})
        else:
            value = float(Lot_Mean_STD[link_c_p_m][CASSR_code][position][0])
            value1 = float(Lot_Mean_STD[link_c_p_m][CASSR_code][position][1])
            CASSR_data[int(CASSR_code)]['tbl_7b'].append(
                {'Measure Mean': position, 'Value': value, 'cell_colour': 'D9D9D9'})
            CASSR_data[int(CASSR_code)]['tbl_7b'].append(
                {'Measure STD': position, 'Value': value1, 'cell_colour': 'D9D9D9'})
    # Table 8
    link_c_p_m = params.SURV_QUESTION_RESP_PROP
    positions = ['q1Combresponse1', 'q1Combresponse2', 'q1Combresponse3', 'q1Combresponse4', 'q1Combresponse5', 'q2aCombresponse1', 'q2aCombresponse2', 'q2aCombresponse3', 'q2aCombresponse4', 'q2aCombresponse5',
                 'q2bresponse1', 'q2bresponse2', 'q2cresponse1', 'q2cresponse2', 'q2cresponse3', 'q3aresponse1', 'q3aresponse2', 'q3aresponse3', 'q3aresponse4', 'q3bresponse1', 'q3bresponse2', 'q3bresponse3', 'q4aresponse1',
                 'q4aresponse2', 'q4aresponse3', 'q4aresponse4', 'q4bresponse1', 'q4bresponse2', 'q4bresponse3', 'q5aresponse1', 'q5aresponse2', 'q5aresponse3', 'q5aresponse4', 'q5bresponse1', 'q5bresponse2', 'q5bresponse3', 'q6aresponse1',
                 'q6aresponse2', 'q6aresponse3', 'q6aresponse4', 'q6bresponse1', 'q6bresponse2', 'q6bresponse3', 'q7aresponse1', 'q7aresponse2', 'q7aresponse3', 'q7aresponse4', 'q7cresponse1', 'q7cresponse2', 'q8aresponse1',
                 'q8aresponse2', 'q8aresponse3', 'q8aresponse4', 'q8bresponse1', 'q8bresponse2', 'q8bresponse3', 'q9aresponse1', 'q9aresponse2', 'q9aresponse3', 'q9aresponse4', 'q9bresponse1', 'q9bresponse2', 'q9bresponse3', 'q10response1',
                 'q10response2', 'q10response3', 'q10response4', 'q11response1', 'q11response2', 'q11response3', 'q11response4',

                 'q12response1', 'q12response2', 'q12response3', 'q12response4', 'q12response5',


                 'q13response1', 'q13response2', 'q13response3', 'q13response4', 'q13response5',
                 'q13Exclresponse2', 'q13Exclresponse3', 'q13Exclresponse4', 'q13Exclresponse5',
                 'q14response1', 'q14response2', 'q14response3', 'q14response4', 'q14response5',
                 'q15aresponse1', 'q15aresponse2', 'q15aresponse3', 'q15bresponse1', 'q15bresponse2', 'q15bresponse3',
                 'q16aresponse1', 'q16aresponse2', 'q16aresponse3', 'q16bresponse1', 'q16bresponse2', 'q16bresponse3', 'q16cresponse1', 'q16cresponse2', 'q16cresponse3', 'q16dresponse1', 'q16dresponse2', 'q16dresponse3',
                 'q17aresponse1', 'q17aresponse2', 'q17aresponse3', 'q17bresponse1', 'q17bresponse2', 'q17bresponse3', 'q17cresponse1', 'q17cresponse2', 'q17cresponse3', 'q17dresponse1', 'q17dresponse2', 'q17dresponse3',
                 'q18response1', 'q18response2', 'q18response3', 'q18response4',
                 'q19response1', 'q19response2',  'q19response3', 'q19response4',
                 'q20aresponse1', 'q20bresponse1', 'q20cresponse1',
                 'q21aresponse1', 'q21bresponse1', 'q21cresponse1',
                 'q22response1', 'q22response2', 'q22response3', 'q22response4',
                 'q23aresponse1', 'q23bresponse1', 'q23cresponse1', 'q23dresponse1', 'q23eresponse1', 'q23fresponse1']
    for position in positions:
        if position not in Lot_Previous[link_c_p_m][CASSR_code].keys():
            value = '0.0'
            CASSR_data[int(CASSR_code)]['tbl_8a'].append(
                {'Measure Previous': position, 'Value': value, 'cell_colour': 'FFFFFF'})
        else:
            value = float(Lot_Previous[link_c_p_m][CASSR_code][position])
            CASSR_data[int(CASSR_code)]['tbl_8a'].append(
                {'Measure Previous': position, 'Value': value, 'cell_colour': 'FFFFFF'})

    for position in positions:
        if position not in Lot_Current[link_c_p_m][CASSR_code].keys():
            value = '0.0'
            CASSR_data[int(CASSR_code)]['tbl_8b'].append(
                {'Measure Current': position, 'Value': value, 'cell_colour': 'FFFFFF'})
        else:
            if (Lot_Current[link_c_p_m][CASSR_code][position][1] == '1'):
                colour = 'FF0000'
            else:
                colour = 'FFFFFF'
            value = float(Lot_Current[link_c_p_m][CASSR_code][position][0])
            CASSR_data[int(CASSR_code)]['tbl_8b'].append(
                {'Measure Current': position, 'Value': value, 'cell_colour': colour})

    for position in positions:
        if position not in Lot_Mean_STD[link_c_p_m][CASSR_code].keys():
            value = '0.0'
            CASSR_data[int(CASSR_code)]['tbl_8c'].append(
                {'Measure Mean': position, 'Value': value, 'cell_colour': 'FFFFFF'})
            CASSR_data[int(CASSR_code)]['tbl_8d'].append(
                {'Measure STD': position, 'Value': value, 'cell_colour': 'FFFFFF'})
        else:
            value = float(Lot_Mean_STD[link_c_p_m][CASSR_code][position][0])
            value1 = float(Lot_Mean_STD[link_c_p_m][CASSR_code][position][1])
            CASSR_data[int(CASSR_code)]['tbl_8c'].append(
                {'Measure Mean': position, 'Value': value, 'cell_colour': 'FFFFFF'})
            CASSR_data[int(CASSR_code)]['tbl_8d'].append(
                {'Measure STD': position, 'Value': value1, 'cell_colour': 'FFFFFF'})
#########################################################Graph#################################################

    CASSR_code = int(CASSR_code)

    salt_total = CASSR_data[int(CASSR_code)]['tbl_1'][0]['Value']
    eligibility_total = CASSR_data[int(CASSR_code)]['tbl_1'][1]['Value']

    x_labels = ["Eligibility Total", "SALT Total"]
    y_labels = [eligibility_total, salt_total]
    fig, ax = plt.subplots()

    ax.bar(x_labels, y_labels, color=['#0070C0', 'grey'])
    ax.set_facecolor('white')
    ax.spines['bottom'].set_color(
        'black'), ax.spines['left'].set_color('black')
    ax.spines['top'].set_color('white'), ax.spines['right'].set_color('white')

    ax.set(title="Comparison between eligible population total and SALT LTS001b\n total for " +
           CASSR_data[CASSR_code]['CASSR name'], ylabel="Population Total")
    plt.savefig(filepath+'comparable_metrics_1_' +
                CASSR_data[CASSR_code]['CASSR name']+'.png', bbox_inches='tight')
    plt.close()

######################################################Generating Word Doc######################################

    CASSR_code = int(CASSR_code)
    print('Generating DQ report')
    # Merging template documents
    doc1 = docx.Document(word_templates[0])
    doc1.save(filepath+'tmp.docx')
    doc = DocxTemplate(filepath+"tmp.docx")

    # Each item in context dictionary corresponds to a variable in {{}} in the microsoft word templates
    context = {'CASSR_code': CASSR_code,
               'CASSR_name': CASSR_data[CASSR_code]['CASSR name'],
               'todays_date': todays_date,
               'current_year': current_string,
               'previous_year': previous_string,
               'current': current_year,
               'table1':  CASSR_data[CASSR_code]['tbl_1'],
               'table1_1':  CASSR_data[CASSR_code]['tbl_1_1'],
               'table2':  CASSR_data[CASSR_code]['tbl_2'],
               'table2_1':  CASSR_data[CASSR_code]['tbl_2_1'],
               'table3':  CASSR_data[CASSR_code]['tbl_3'],
               'table4':  CASSR_data[CASSR_code]['tbl_4'],
               'table5a': CASSR_data[CASSR_code]['tbl_5a'],
               'table5b': CASSR_data[CASSR_code]['tbl_5b'],
               'table6a': CASSR_data[CASSR_code]['tbl_6a'],
               'table6b': CASSR_data[CASSR_code]['tbl_6b'],
               'table7a': CASSR_data[CASSR_code]['tbl_7a'],
               'table7b': CASSR_data[CASSR_code]['tbl_7b'],
               'table8a': CASSR_data[CASSR_code]['tbl_8a'],
               'table8b': CASSR_data[CASSR_code]['tbl_8b'],
               'table8c': CASSR_data[CASSR_code]['tbl_8c'],
               'table8d': CASSR_data[CASSR_code]['tbl_8d'],
               'cm_image_1': InlineImage(doc, filepath+'comparable_metrics_1_'+CASSR_data[CASSR_code]['CASSR name']+'.png', width=Mm(120), height=Mm(80))}

    doc.render(context)  # Filling in template
    doc_name = "Surveys Validation Report - "+str(CASSR_code)+".docx"
    doc.save(output_filepath+doc_name)  # Saving DQ report for that CASSR
    print('\nGenerated DQ report: '+doc_name)

    os.remove(filepath+'comparable_metrics_1_' +
              CASSR_data[CASSR_code]['CASSR name']+'.png')
