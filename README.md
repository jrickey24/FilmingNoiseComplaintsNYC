PROJECT: Filming Permit & Noise Complaint CLI Correlation Tool

NOTE: The requested file, 2023Q3_results.csv is provided in the data\output directory.

PURPOSE:
This tool analyzes correlations between filming permits and noise complaints in New York City. It utilizes data from Socrata Open Data APIs, pandas for analysis, and provides insights into potential noise disruptions caused by filming activities.

PREREQUISITES:

OPTION #1:  Python & package dependency installations. Note that when running in Docker, a paid subscription is needed to access the output files from within the Volumes tab of the Docker desktop application.

1. If you prefer to run the script directly in Python, you should install Python 3.9 along with executing pip install against the dependencies listed in the requirements.txt file.
2. Open command prompt window
3. Navigate to the project folder: \FilmingNoiseComplaintsNyc\src
4. Provide the following command where the date args represent desired start & end:
   python main.py YYYY-MM-DD YYYY-MM-DD

EXAMPLE EXECUTION:

C:\Users\$USER\Documents\FilmingNoiseComplaintsNyc\src>python main.py 2023-07-01 2023-09-30
Please note: The maximum allowed date range is 92 days.
Extracting dataset: filming_permits for the provided date range.
Extracting dataset: noise_complaints for the provided date range.
Filtering noise complaints based on zipcodes & created date within filming permit start & end dates.
Data analysis complete for the provided date range, results.csv added to output folder.


OPTION #2:  Docker installed (see installation instructions below)

1. Docker Installation:
Docker allows you to run the application in a containerized environment.
Here are the links to install Docker for your operating system:

Windows: https://docs.docker.com/desktop/install/windows-install/

macOS: https://docs.docker.com/desktop/install/mac-install/

Linux: https://docs.docker.com/desktop/install/linux-install/


2. Build the Docker image:

cd project_directory
docker build -t filming_noise_correlation .

3. Run the container:

docker run filming_noise_correlation 2023-07-01 2023-09-30

NOTE: Replace 2023-07-01 and 2023-09-30 with your desired start and end dates in YYYY-MM-DD format.


OUTPUT:

NOTE: To access the output files in the Docker container:
1. Open the Volumes tab from within the Docker desktop
2. Navigate to the volume with the associated IMAGE name = filming_noise_correlation 
3. From within the corresponding volume, navigate to the DATA tab
4. Expand the data folder, followed by the ouput folder
5. Click on the elipses next to the result.csv file & any other files you want to view
6. Select Save As & specify the target location on your local machine

The script will generate(or overwrite) three CSV files in the data/output directory:

* filming_permits.csv: Contains details of filming permits within the specified date range.
* noise_complaints.csv: Contains noise complaint data filtered based on the specified date range and columns needed.
* results.csv: Contains the correlation results, as specified in the following requirements:

1. The results should be sorted by the number of complaints in descending order.

2. In case of ties, sort first by the permit start date in ascending order, and then by the event ID in ascending order.

3. The sorted list should be exported to a CSV file containing all filming permits for the user-specified date range. 

4. The format should match the original Filming Permit data, with the addition of a column named NumNoiseComplaints to represent the number of correlated noise complaints.

ADDITIONAL CONSIDERATIONS:

1. The script has a maximum allowed date range of 92 days (equivalent to one quarter). This information is displayed during execution. The purpose of this is to allow for effectively fetching and processing the data within an optimal timeframe.

2. The script extracts only the necessary columns from the noise complaints dataset to improve efficiency.

3. Socrata Pagination: The sodapy library automatically handles pagination for large datasets, ensuring that all relevant data is retrieved.