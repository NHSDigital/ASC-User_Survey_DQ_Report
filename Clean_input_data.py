
import params
import pandas as pd


def import_data():
    inputs = params.to_be_cleaned_input
    Dataset = 'cleaned_questionnaire.csv'
    AllData = pd.read_csv(inputs+Dataset, header=0, low_memory=False)
    return AllData


def rename(AllData):
    try:
        AllData = AllData.rename(
            columns={"MechOfDelivery": "MechanismofDelivery"})
        AllData["Translated_Recoded"] = AllData["Translated_Grouped"].replace([
                                                                              "Yes", "No"], [1, 2])
        del AllData["Ethnicity"]
        AllData["Ethnicity"] = AllData["Ethnicity_Grouped"].replace(
            ["White", "Mixed", "Asian or Asian British", "Black or Black British", "Other", "Not Stated"], [1, 2, 3, 4, 5, 6])
        AllData['PSR'] = AllData["PrimarySupportReason_Grouped"].replace(
            ["Physical Support", "Sensory Support", "Support with Memory and Cognition", "Learning Disability Support", "Mental Health Support", "Social Support"], [1, 2, 3, 4, 5, 6])
        AllData["AgeBand"] = AllData["Age_Grouped"].replace(
            ["18-24", "25-34", "35-44", "45-54", "55-64", "65-74", "75-84", "85-inf"], [1, 2, 3, 4, 5, 6, 7, 8])
    except:
        print("Data is already clean")
    else:
        AllData

    return AllData


# replace alphanumeric councils with numbers
def remove_alphanumeric_councils(AllData):
    try:
        AllData['LaCode'] = AllData['LaCode'].replace(
            ["Z9D4Z", "U6Q5Z"], [101, 100])
    except:
        print("no alphanumeric value in column")

    else:
        AllData
    return AllData



def main():
    imports = import_data()
    names = rename(imports)
    remove_alphanumeric = remove_alphanumeric_councils(names)
    remove_alphanumeric.to_csv(params.input+"cleaned_questionnaire.csv")
    return remove_alphanumeric


main()
