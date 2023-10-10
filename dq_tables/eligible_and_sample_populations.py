import pandas as pd
import params


def initial_merge():
    EligiblePopulation = params.EligiblePopulation
    SALT = params.SALT


    EP_SALT = EligiblePopulation.merge(SALT, on='LaCode', how='left')

    return EP_SALT


def SALT_Stratum(EP_SALT):
    stratums = ["Stratum 1", "Stratum 2", "Stratum 3", "Stratum 4"]
    d = {'LaCode': [1001]}
    #df = pd.DataFrame(data=d)
    new_data = pd.DataFrame([])
    new_england = pd.DataFrame(data=d)
    for s in stratums:
        new_data["LaCode"] = EP_SALT['LaCode']
        new_data["SALT_total"] = EP_SALT['Total']
        new_data[s] = (EP_SALT[s]/EP_SALT['Total']) * 100
        # for england
        new_england[s] = EP_SALT[s].sum()
    new_england['Total'] = new_england['Stratum 1'] + new_england['Stratum 2'] + \
        new_england['Stratum 3'] + new_england['Stratum 4']
    stratums = ["Stratum 1", "Stratum 2", "Stratum 3", "Stratum 4"]
    for s in stratums:
        new_england[s] = (new_england[s]/new_england['Total']) * 100
        new_england['SALT_total'] = new_england['Total']
        new = pd.concat([new_data, new_england])
    del new['Total']
    new_names = ["SALT_Stratum_1", "SALT_Stratum_2",
                 "SALT_Stratum_3", "SALT_Stratum_4"]

    for s, n in zip(stratums, new_names):
        new.rename(columns={s: n}, inplace=True)

    return new


def Stratum_proportion_SS(EP_SALT):
    samples = ["stratum1Sample", "stratum2Sample",
               "stratum3Sample", "stratum4Sample"]
    d = {'LaCode': [1001]}
    new_england = pd.DataFrame(data=d)
    new_data = pd.DataFrame([])
    new_data["LaCode"] = EP_SALT['LaCode']
    new_data['Total'] = EP_SALT['stratum1Sample'] + EP_SALT['stratum2Sample'] + \
        EP_SALT['stratum3Sample'] + EP_SALT['stratum4Sample']

    for s in samples:
        new_data[s] = (EP_SALT[s]/new_data['Total']) * 100
        new_england[s] = EP_SALT[s].sum()
    new_england['Total'] = new_england['stratum1Sample'] + new_england['stratum2Sample'] + \
        new_england['stratum3Sample'] + new_england['stratum4Sample']
    stratums = ["stratum1Sample", "stratum2Sample",
                "stratum3Sample", "stratum4Sample"]
    for s in stratums:
        new_england[s] = (new_england[s]/new_england['Total']) * 100
        new = pd.concat([new_data, new_england])
    #del new['Total']
    new_names = ["Stratum 1 proportion_SS",	"Stratum 2 proportion_SS",
                 "Stratum 3 proportion_SS",	"Stratum 4 proportion_SS"]
    for s, n in zip(stratums, new_names):
        new.rename(columns={s: n}, inplace=True)
    new.rename(columns={'Total': 'Total Sample Size'}, inplace=True)
    return new


def Stratum(EP_SALT):
    samples = ["stratum1Pop", "stratum2Pop", "stratum3Pop", "stratum4Pop"]
    d = {'LaCode': [1001]}
    new_england = pd.DataFrame(data=d)
    new_data = pd.DataFrame([])
    new_data["LaCode"] = EP_SALT['LaCode']
    new_data['Total'] = EP_SALT['stratum1Pop'] + EP_SALT['stratum2Pop'] + \
        EP_SALT['stratum3Pop'] + EP_SALT['stratum4Pop']

    for s in samples:
        new_data[s] = (EP_SALT[s]/new_data['Total']) * 100
        new_england[s] = EP_SALT[s].sum()
    new_england['Total'] = new_england['stratum1Pop'] + new_england['stratum2Pop'] + \
        new_england['stratum3Pop'] + new_england['stratum4Pop']
    stratums = ["stratum1Pop", "stratum2Pop", "stratum3Pop", "stratum4Pop"]
    for s in stratums:
        new_england[s] = (new_england[s]/new_england['Total']) * 100
        new = pd.concat([new_data, new_england])
    new.rename(columns={'Total': 'Eligible population'}, inplace=True)
    new_names = ["Stratum 1 proportion_EP",	"Stratum 2  proportion_EP",
                 "Stratum 3 proportion_EP",	"Stratum 4 proportion_EP"]
    for s, n in zip(stratums, new_names):
        new.rename(columns={s: n}, inplace=True)

    return new


def SALT_EP(EP_SALT):
    elig_pop = ["stratum1Pop", "stratum2Pop", "stratum3Pop", "stratum4Pop"]
    salt_pop = ["Stratum 1", "Stratum 2", "Stratum 3", "Stratum 4"]



    salt_data = pd.DataFrame([])
    ep_data = pd.DataFrame([])
    new_data = pd.DataFrame([])

    salt_data["LaCode"] = EP_SALT['LaCode']
    ep_data["LaCode"] = EP_SALT['LaCode']

    for s in salt_pop:
        salt_data[s] = EP_SALT[s]
    salt_data['Total'] = salt_data["Stratum 1"] + salt_data["Stratum 2"] + \
        salt_data["Stratum 3"] + salt_data["Stratum 4"]

    for e in elig_pop:
        ep_data[e] = EP_SALT[e]
    ep_data['Total'] = ep_data["stratum1Pop"] + ep_data["stratum2Pop"] + \
        ep_data["stratum3Pop"] + ep_data["stratum4Pop"]

   

    new_data['LaCode'] = EP_SALT['LaCode']
    new_data['SALT_EP'] = ep_data['Total'] - salt_data['Total']
    new_data['Rounded percentage'] = (
        ep_data['Total'] - salt_data['Total'])/salt_data['Total'] * 100

    # for diff_to_SALT

    new_names = ["Stratum_1_Diff_to_SALT", "Stratum_2_Diff_to_SALT",
                 "Stratum_3_Diff_to_SALT", "Stratum_4_Diff_to_SALT"]
    for n, s, e in zip(new_names, salt_pop, elig_pop):
        new_data[n] = ((((ep_data[e]/ep_data['Total']) * 100)) -
                       (salt_data[s]/salt_data['Total']) * 100)
        new_data["Diff_to_SALT"] = (
            ep_data['Total'] - salt_data['Total'])/ep_data['Total'] * 100

    

    return new_data


def stratum_sample(EP_SALT):

    samples = ["stratum1Sample", "stratum2Sample",
               "stratum3Sample", "stratum4Sample"]
    elig_pop = ["stratum1Pop", "stratum2Pop", "stratum3Pop", "stratum4Pop"]

    sample_data = pd.DataFrame([])
    ep_data = pd.DataFrame([])
    new_data = pd.DataFrame([])

    new_data['LaCode'] = EP_SALT['LaCode']
    sample_data['LaCode'] = EP_SALT['LaCode']
    ep_data['LaCode'] = EP_SALT['LaCode']

    for s in samples:
        sample_data[s] = EP_SALT[s]

    for e in elig_pop:
        ep_data[e] = EP_SALT[e]

    new_names = ["Stratum_1_Sample", "Stratum_2_Sample",
                 "Stratum_3_Sample", "Stratum_4_Sample"]

    # get totals
    sample_data['Total'] = sample_data["stratum1Sample"] + sample_data["stratum2Sample"] + \
        sample_data["stratum3Sample"] + sample_data["stratum4Sample"]
    ep_data['Total'] = ep_data["stratum1Pop"] + ep_data["stratum2Pop"] + \
        ep_data["stratum3Pop"] + ep_data["stratum4Pop"]

    for n, s, e in zip(new_names, samples, elig_pop):
        new_data[n] = ((sample_data[s]/sample_data['Total']) *
                       100) - ((ep_data[e]/ep_data['Total']) * 100)

    return new_data


def england_ep(EP_SALT):

    England_EP = pd.DataFrame([])

    eligible = ["stratum1Pop", "stratum2Pop", "stratum3Pop", "stratum4Pop"]

    England_new_names = ["stratum1", "stratum2", "stratum3", "stratum4"]

    for e, E in zip(eligible, England_new_names):

        England_EP[E] = EP_SALT[e]

        England_EP[E] = England_EP[E].sum()


    England_EP["Total"] = England_EP["stratum1"] + England_EP["stratum2"] + \
        England_EP["stratum3"] + England_EP["stratum4"]

    for E in England_EP:

        England_EP[E] = (England_EP[E]/England_EP["Total"]) * 100

    council_population = pd.DataFrame([])

    new_names = ["Stratum_1_diff_to_Eng", "Stratum_2_diff_to_Eng",
                 "Stratum_3_diff_to_Eng", "Stratum_4_diff_to_Eng"]

    council_population = EP_SALT[[
        "LaCode", "stratum1Pop", "stratum2Pop", "stratum3Pop", "stratum4Pop"]]
    council_population['Total'] = EP_SALT["stratum1Pop"] + \
        EP_SALT["stratum2Pop"] + EP_SALT["stratum3Pop"] + \
        EP_SALT["stratum4Pop"]

    for e, n, E in zip(eligible, new_names, England_new_names):

        council_population[n] = (
            (council_population[e]/council_population["Total"]) * 100) - England_EP[E]

    return council_population[['LaCode', "Stratum_1_diff_to_Eng", "Stratum_2_diff_to_Eng", "Stratum_3_diff_to_Eng", "Stratum_4_diff_to_Eng"]]


def england_strat(EP_SALT):

    England_EP = pd.DataFrame([])

    eligible = ["stratum1Sample", "stratum2Sample",
                "stratum3Sample", "stratum4Sample"]

    England_new_names = ["stratum1", "stratum2", "stratum3", "stratum4"]

    for e, E in zip(eligible, England_new_names):

        England_EP[E] = EP_SALT[e]

        England_EP[E] = England_EP[E].sum()


    England_EP["Total"] = England_EP["stratum1"] + England_EP["stratum2"] + \
        England_EP["stratum3"] + England_EP["stratum4"]

    for E in England_EP:

        England_EP[E] = (England_EP[E]/England_EP["Total"]) * 100

    council_population = pd.DataFrame([])

    new_names = ["Stratum_1_diff_to_Eng _sample",	"Stratum_2_diff_to_Eng _sample",
                 "Stratum_3_diff_to_Eng _sample",	"Stratum_4_diff_to_Eng_sample"]

    council_population = EP_SALT[["LaCode", "stratum1Sample",
                                  "stratum2Sample", "stratum3Sample", "stratum4Sample"]]
    council_population['Total'] = EP_SALT["stratum1Sample"] + \
        EP_SALT["stratum2Sample"] + EP_SALT["stratum3Sample"] + \
        EP_SALT["stratum4Sample"]

    for e, n, E in zip(eligible, new_names, England_new_names):

        council_population[n] = (
            (council_population[e]/council_population["Total"]) * 100) - England_EP[E]

    return council_population[['LaCode', 'Stratum_1_diff_to_Eng _sample', 'Stratum_2_diff_to_Eng _sample', 'Stratum_3_diff_to_Eng _sample', 'Stratum_4_diff_to_Eng_sample']]


def merge_all(salt_strata, stratum_samples, stratum_population, salt_ep_difference, stratum_proportions, eng, eng_strat):
    list = [salt_strata, stratum_samples, stratum_population,
            salt_ep_difference, stratum_proportions, eng, eng_strat]
    all_data = pd.DataFrame([])
    all_data['LaCode'] = stratum_samples['LaCode']
    for l in list:

        all_data = all_data.merge(l, on='LaCode', how='left')

    all_data['Difference_sample_EP'] = (
        all_data['Total Sample Size']/all_data['Eligible population']) * 100
    return all_data


def create_salt_population_table():
    merge = initial_merge()
    salt_strata = SALT_Stratum(merge)
    stratum_samples = Stratum_proportion_SS(merge)
    stratum_population = Stratum(merge)
    salt_ep_difference = SALT_EP(merge)
    stratum_proportions = stratum_sample(merge)
    eng = england_ep(merge)
    eng_strat = england_strat(merge)
    all_data = merge_all(salt_strata, stratum_samples, stratum_population,
                         salt_ep_difference, stratum_proportions, eng, eng_strat)
    for column in params.sample_and_eligible_population_columns:
        all_data[column] = all_data[column].round(1)

    return all_data


create = create_salt_population_table()
create.to_csv(params.output+'SURV_ELIGIBLE_POP_SAMPLE_SIZEss.csv')
