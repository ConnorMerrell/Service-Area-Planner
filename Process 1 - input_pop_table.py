import pandas as pd

#read census areas data
outputareas_table = pd.read_csv("Middle_layer_Super_Output_Areas_December_2021_Boundaries_EW_BFC_V7_2014755402551514493.csv")
#read population data
pop_table = pd.read_csv("sapemsoasyoatablefinal.csv", thousands = "," )
#merge population to census areas
input_area_table = pd.merge(outputareas_table, pop_table, left_on="MSOA21CD", right_on="MSOA 2021 Code")
#select columns
input_area_table = input_area_table[["MSOA21CD", "MSOA21NM", "BNG_E", "BNG_N", "LAT", "LONG", "Shape__Area", "Shape__Length", "Total"]]
#rename population column
input_area_table = input_area_table.rename(columns={"Total":"Total_Population"})
#convert population to numbers
input_area_table["Total_Population"] = pd.to_numeric(input_area_table["Total_Population"])

input_area_table = input_area_table.sort_values("Total_Population", ascending=False)

input_area_table.to_csv("input_area_table.csv")

print(input_area_table.head())

print("Done")