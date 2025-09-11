from src.load_data.station_route_data_load import load_route_summary_data, load_station_summary_data

route_df = load_route_summary_data()
station_df = load_station_summary_data()

route_df.info()