import pandas as pd
import numpy as np

input_area_table = pd.read_csv("input_area_table.csv")
area_population_table = input_area_table[["MSOA21CD","Total_Population"]].copy()

#total_areas = input_area_table.shape[0]




asset_list = []




def haversine_np(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)

    All args must be of equal length.

    """

    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2

    c = 2 * np.arcsin(np.sqrt(a))
    km = 6378.137 * c
    return km



def get_nearby_areas(current_area, asset_range):
    other_areas_list = []
    for other_area in input_area_table.itertuples():
        if current_area.MSOA21CD == other_area.MSOA21CD:
            continue
        elif abs(current_area.LONG-other_area.LONG) * 111 > asset_range:
            continue
        else:
            dist = haversine_np(lat1=current_area.LAT, lon1=current_area.LONG, lat2=other_area.LAT, lon2=other_area.LONG)
            if dist <= asset_range:
                dict1 = {"MSOA21CD": other_area.MSOA21CD, "MSOA21NM": other_area.MSOA21NM, "LAT": other_area.LAT, "LONG": other_area.LONG, "Users": other_area.Total_Population, "Distance": dist}
                other_areas_list.append(dict1)
            else:
                pass

    closest_areas_dataframe = pd.DataFrame(other_areas_list)
    if closest_areas_dataframe.empty == False:
        closest_areas_dataframe = closest_areas_dataframe.sort_values("Distance", ascending=True)

    return closest_areas_dataframe



def place_assets(asset_capacity, asset_range):
    progress = 0
    total_progress = len(input_area_table)

    #asset_range_lat = asset_range / 100
    asset_index = 0

    for current_area in input_area_table.itertuples(): #for each area, starting with the largest
        print("Current Area: ", current_area.MSOA21NM)

        #check against population table to see if fully served
        current_area_index = area_population_table.index[area_population_table['MSOA21CD'] == current_area.MSOA21CD].tolist()[0]
        if area_population_table.loc[current_area_index, "Total_Population"] == 0:
            print(current_area[2], " skipped as fully served")

            progress += 1

            print("Progress: ", round((progress / total_progress) * 100, 3), "%")
            continue



        #add required assets if more than one are required
        assets_required = current_area.Total_Population // asset_capacity
        for i in range(assets_required):
            asset_index += 1
            asset_name = "Asset" + str(asset_index)
            dict1 = {"Asset Name": asset_name, "Asset Capacity": asset_capacity, "Asset Range": asset_range, "MSOA21CD": current_area.MSOA21CD, "MSOA21NM": current_area.MSOA21NM,
                     "LAT": current_area.LAT, "LONG": current_area.LONG, "Served Areas": [{current_area.MSOA21CD:current_area.Total_Population}] }
            asset_list.append(dict1)
            area_population_table.loc[current_area_index, "Total_Population"] -= asset_capacity
        #print(assets_required, " assets created for ", current_area.MSOA21CD)





        #Resolve remaining capacity
        capacity_remaining = np.mod(current_area.Total_Population, asset_capacity)
        print("Capacity Remaining: ", capacity_remaining)
        if capacity_remaining > 0: #if there is capacity remaining in the current asset
            asset_index += 1
            #empties current area and adds it to served list
            area_population_table.loc[current_area_index, "Total_Population"] = 0
            asset_served_areas_list = [{current_area.MSOA21CD:current_area.Total_Population}]

            nearby_areas = get_nearby_areas(current_area, asset_range)


            for i in nearby_areas.itertuples(): #for other nearest areas
                nearby_area_index = area_population_table.index[area_population_table['MSOA21CD'] == i.MSOA21CD].tolist()[0]

                if capacity_remaining > 0:
                    if capacity_remaining > i.Users: #if more capacity then next nearest area, empty it, add it to list, check for next area
                        capacity_remaining -= i.Users
                        area_population_table.loc[nearby_area_index, "Total_Population"] = 0
                        asset_served_areas_list.append({i.MSOA21CD: i.Users})
                    elif capacity_remaining == i.Users: #if remaining capacity is the same as next nearest area, empty it, add to list, move on.
                        capacity_remaining -= i.Users
                        area_population_table.loc[nearby_area_index, "Total_Population"] = 0
                        asset_served_areas_list.append({i.MSOA21CD: i.Users})
                        break
                    else: #if capacity remaining is less than next nearest area, take capacity from next nearest area, add to list, move on.
                        area_population_table.loc[nearby_area_index, "Total_Population"] = i.Users - capacity_remaining
                        print(capacity_remaining)
                        asset_served_areas_list.append({i.MSOA21CD: int(capacity_remaining)})
                        break
                else:
                    break



            asset_name = "Asset" + str(asset_index)  # assigns asset name


            print (asset_name, " created")
            dict2 = {"Asset Name": asset_name,  "Asset Capacity": asset_capacity, "Asset Range": asset_range, "MSOA21CD": current_area.MSOA21CD, "MSOA21NM": current_area.MSOA21NM,
                     "LAT": current_area.LAT, "LONG": current_area.LONG, "Served Areas": asset_served_areas_list}
            asset_list.append(dict2)

        progress += 1

        print("Progress: ", round((progress/total_progress)*100, 3), "%")






    asset_dataframe = pd.DataFrame(asset_list)
    asset_dataframe.to_csv("assets.csv", index=False)


place_assets(30000, 3)
print("Finished")
