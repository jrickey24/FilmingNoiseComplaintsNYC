#!/usr/bin/env python

from datetime import datetime, timedelta
import pandas as pd
import argparse
import sodapy

def is_valid_date_format(input_date):
    try:
        datetime.strptime(input_date, "%Y-%m-%d")
        return True
    except ValueError:
        return False
    
def add_day(end_time): 
    end_datetime = datetime.strptime(end_time, "%Y-%m-%d")
    end_time_plus_one = end_datetime + timedelta(days=1)
    end_time_str = end_time_plus_one.strftime("%Y-%m-%d")
    return end_time_str

def get_days_between(start_time, end_time):
   start_datetime = datetime.strptime(start_time, "%Y-%m-%d")
   end_datetime = datetime.strptime(end_time, "%Y-%m-%d")
   delta = end_datetime - start_datetime
   return delta.days

def is_valid_date_range(start_date, end_date):
    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
    current_datetime = datetime.now()
    return start_datetime < end_datetime < current_datetime
     
def extract_dataset(start_date, end_date, file_name, dataset_id, where_clause, select_cols=None, limit=10000):
  """
  Fetches data from a Socrata dataset. Stores in a csv for reference/troubleshooting. API call returns the data as JSON
  & sodapy converts to list of dictionaries which gets converted to pandas dataframe. Note that specifying app_token 
  bypasses low throttling thresholds(status code 429)/low request pool limit.
  Args:
      start_date (str): The starting date
      end_date (str): The ending date
      file_name (str): The name used to store the output csv file & referenced impacted dataset if error occurs 
      dataset_id (str): The Socrata dataset identifier
      where_clause (str): The query clause to filter the data
      select_cols (str, optional): A string of column names can be specified separated by commas (default: all columns)
      limit (int, optional): The max number of records to retrieve (default: 10000)
  Returns:
      pd.DataFrame: The fetched data as a Pandas DataFrame.
  Raises:
      sodapy.SocrataError: If an error occurs with the Socrata API call.
      Exception: If an unexpected error occurs during data extraction.
  """
  try:
    print(f"Extracting dataset: {file_name} for the provided date range.")
    client = sodapy.Socrata("data.cityofnewyork.us", app_token="{app_token}", timeout=150)
    results = client.get(dataset_id, where=where_clause, select=select_cols, limit=limit)
    df = pd.DataFrame.from_records(results)
    df.to_csv(f"./data/output/{file_name}.csv", index=False)
    return df
  except sodapy.SocrataError as e:
    print(f"Socrata API error encountered while fetching dataset: {file_name}: {e}")
    raise  # Re-raise to signal failure
  except Exception as e:
    print(f"Unexpected error extracting dataset: {file_name}: {e}")
    raise
    
def correlate_datasets(fp_df, nc_df): 
    if fp_df.empty:
        print("No filming permits found for the provided date range. Unable to evaluate related noise complaints.")
        return
    if nc_df.empty:
        print("No noise complaints found for the provided date range. Unable to evaluate related filming permits.")
        return
    print("Filtering noise complaints based on zipcodes & created date within filming permit start & end dates.")
    results = []
    for index, row in fp_df.iterrows():  # Iterrate to account for multiple zipcode_s values when evaluating correlation
        zip_codes = row['zipcode_s'].split(',')
        start_date = row['startdatetime']
        end_date = row['enddatetime']
        num_complaints = 0
        for zip_code in zip_codes:
           filtered_complaints = nc_df[(nc_df['incident_zip'] == zip_code.strip()) &
                                       (nc_df['created_date'] >= start_date) &
                                       (nc_df['created_date'] < end_date)]
           num_complaints = len(filtered_complaints) + num_complaints
        results.append({
            **row,
            'NumNoiseComplaints': num_complaints
        })
    results_df = pd.DataFrame(results)
    results_df.sort_values(by=['NumNoiseComplaints', 'startdatetime', 'eventid'], ascending=[False, True, True], inplace=True)
    results_df.to_csv('./data/output/results.csv', index=False)
    print(f"Data analysis complete for the provided date range, results.csv added to output folder.")


def main():
    parser = argparse.ArgumentParser(description="Tool to analyze filming permit and noise complaint correlations.")
    parser.add_argument("start_date", help="Start date in YYYY-MM-DD format")
    parser.add_argument("end_date", help="End date in YYYY-MM-DD format")
    args = parser.parse_args()

    # Validate date formats
    if not is_valid_date_format(args.start_date):
        print("Error: Invalid start_date format. Please use YYYY-MM-DD.")
        return
    if not is_valid_date_format(args.end_date):
        print("Error: Invalid end_date format. Please use YYYY-MM-DD.")
        return
                        
    max_date_range = 92 # Maximum allowed date range (92 days) which is the max number of days in a quarter - EX: 2023Q3
    print(f"Please note: The maximum allowed date range is {max_date_range} days.")  # Proactively inform user of max date range

    # Convert the end_date input string to datetime object, add 1 day, & convert back to string for query use
    end_date_inclusive = add_day(args.end_date)
    
    # Validate date range constraints
    if not is_valid_date_range(args.start_date, args.end_date):
        print("Error: Invalid date range. Please ensure start_date < end_date < current_date.")
        return
    if get_days_between(args.start_date, end_date_inclusive) > max_date_range:
        print(f"Error: Date range cannot exceed: {max_date_range} days.")
        exit(1)

    # Provide dataset & query info for extracting filming permits
    filming_permits_df = extract_dataset(start_date=args.start_date, end_date=end_date_inclusive, file_name="filming_permits",
        dataset_id="tg4x-b46p", where_clause=f"startdatetime >= '{args.start_date}' and enddatetime < '{end_date_inclusive}'",
        limit=10000)
    
    # Provide dataset & query info for extracting noise complaints * we only extract 3 needed columns to reduce size
    noise_complaints_df = extract_dataset(start_date=args.start_date, end_date=end_date_inclusive,
        file_name="noise_complaints", dataset_id="p5f6-bkga",
        where_clause=f"created_date >= '{args.start_date}' and created_date < '{end_date_inclusive}'",
        select_cols="unique_key, created_date, incident_zip", limit=500000)
    
    correlate_datasets(filming_permits_df, noise_complaints_df)


if __name__ == '__main__':
   main()