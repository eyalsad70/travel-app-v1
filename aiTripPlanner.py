
import keys_loader
import rapidApi_client
import my_json_repository
from my_logger import print_info, print_error


ai_trip_planner_host_url = "ai-trip-planner.p.rapidapi.com"

def get_activities(file_name, request_url = None):
    private_key = keys_loader.load_private_key("ai_trip_planner")
    ai_trip_planner_header = keys_loader.RapidApiRequestHeader(private_key, ai_trip_planner_host_url)
    file_path = "./data"

    my_plan = my_json_repository.read_json_data(file_name, file_path)

    if not my_plan: # file isn't cached yet. retreive data from API and save it
        my_plan = rapidApi_client.get_rapidApi_data(ai_trip_planner_header, request_url)
        if not my_plan:
            print_error(f"get_activities :: Cant find destination {request_url}")
            return None
        else:
            my_json_repository.save_json_data(file_name, file_path, my_plan)
            
    sample_plan = my_plan['plan']

    # print(sample_plan)

    # sample plan include list of dictionaries - each representing day and activity list (per time)

    # I want to extract list of all activities
    activity_list = []
    for day_plan in sample_plan:
        activities = day_plan['activities']
        for activity in activities:
            specific_activity = activity['description']
            if specific_activity not in activity_list:
                activity_list.append(specific_activity)
    print(activity_list)
    return activity_list


def get_destination_attractions(destination_name:str, country:str, number_of_days:int, file_name_for_saving:str):
    request_url = f"/?days={number_of_days}&destination={destination_name}%2C{country}"
    get_activities(file_name_for_saving, request_url)


if __name__ == "__main__":
    # run few destination examples
    # get_destination_attractions("poprad", "slovakia", 7, "poprad.json")
    get_destination_attractions("zakopane", "poland", 8, "zakopane2.json")
    # get_destination_attractions("high-tatras", "slovakia", 7, "high-tatras.json")
