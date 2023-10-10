###this reoslves the pecularity of people who are asked the Question 2c in the ASCA survey.
import pandas as pd
import numpy as np
import params


output = params.output


def imports():
    inputs = params.input
    Dataset = 'cleaned_questionnaire.csv'
    AllData = pd.read_csv(inputs+Dataset, header=0, low_memory=False)
    return AllData


def q2c_people(AllData):
    needed_stratum = [2,4]
    AllData = AllData[AllData["SupportSetting"] == 1]
    AllData =  AllData[AllData['PSR'] != 4]
    AllData =  AllData[AllData['Stratum'].isin(needed_stratum)]

    councils = AllData['LaCode'].unique()
    all_q2c = pd.DataFrame([])
    for council in councils:
        AlData = AllData[AllData['LaCode']== council]
        ResponseData = AlData[AlData['Response']== 1]
        Data =  ResponseData[["LaCode","q2c"]]
        counts = ResponseData.count()
        response_rate = (counts["q2c"]/counts['LaCode']) * 100
        del Data['q2c']
        Data['LaCode'] = council
        Data['Total_proportion'] = response_rate
        Data['Question'] = "q2c"
        newdata = Data.drop_duplicates()
        all_q2c = pd.concat([all_q2c,newdata])
    return all_q2c
        

      
    
    
def main():
    import_data = imports()
    q2c = q2c_people(import_data)
    
    return q2c
