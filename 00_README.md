# CIP_FS25_209
Github Repository for the project "Crystals in Switzerland"

Within this repository the following content is available which was used for the whole Project Process. All Datasets are stored in the subfolder "Data". All datasets, Python-files and Output for each research question is in an own subfolder. The Documentation is also stored in a subfolder. 

**00 Info and Structure:**
    - 00_README: This README file gives a short overview of how the Github Repository is set up and organized. 

**01 Scraping:**
    - 01-1_Initial_Scraping-Code: First try to fetch data from Mindat, in directory "Unused Code Dump".
    - 01-2_Final_Scraping-Code: Code which was used to scrape the data from Mindat.
    - 01-3_Initial_Dataset: Dataset with the scraped data from Mindat, used for further processing in later steps.

**02 API *(tried to access data of mindat.org via API as well - did not come to the same extent of data as we reached through Scraping)*:**
    - 02-1_Mindat-API-test: Tried to fetch the Swiss localities via API (Beta) provided by Mindat, but data does not seem to be tagged sufficiently on the website (only 10 results), in directory "Unused Code Dump".
    - 02-2_swiss_localities: Result from the API request which was not used for further processing, in directory "Data/Unused Data Dump".


**03 Preprocessing of Dataset *(was done seperately for different cleaning end enrichment topics)*:**
    - 03-1_Minerals_Preprocessing: Normalizing the dataset to create a new location-mineral pair on each line rather than multiple minerals on one locality row (in directory "Unused Data Dump).
    - 03-2_Minerals_Cleaned-dataset: Cleansed the mineral names as described in the documentation (in directory "Unused Data Dump).
    - 03-3_Coordinates_Preprocessing: Code for cleaning of column "Latitude & Longitude" to receive the same format for every entry and to enhance the dataset with a new column for the "Altitude". The altitude was entered with different API's. 
    - 03-4_Coordinates_Cleaned-dataset: Dataset based on 03-2_Minerals_Cleaned-dataset and cleaned with the code 03-3_Coordinates_Preprocessing for a new dataset. 
    - 03-5_Minerals_Preprocessing: Python script which includes the code for the normalization, the cleansing of names and the categorization.
    - 03-6_Minerals-Categorization_Cleaned-dataset: Resulting dataset from the operations performed in 03-5_Minerals_Preprocessing.
    - 03-7_Finalization_Preprocessing: Code for final cleaning of column names and introducing a new column for the Categorization of the Altitude. 
    - 03-8_Finalized_Dataset: This is the finalized dataset which was used for the Analysis. 

**04 Analysis of Dataset:**
    - 04_RQ1_Spatial-Distribution: This is the code and analysis of the first Research Question regarding the spatial Distribution. 
            - app.py: includes the code for the streamlit app to create the heatmap and the filtering - enter "streamlit run app.py" in the respective directory to run the web app.
            - data_for_analysis: Dataset on which the web app is built, copy of 03-2_Minerals_Cleaned-dataset.
            - requirements.txt: Build file for the streamlit cloud service to specifiy the dependencies.
    - 04_RQ2_Occurence-Frequency: This is the code and analysis of the second Research Question regarding the highest frequency of occurence of the crystal types. 
    - 04_RQ3-1_Statistical-Correlation: This is the code and analysis of the third Research Question regarding the statistical correlation between crystal occurences and elevation levels. 
        - 04_RQ3-2_Visualization-Scatterplots: 2x2 Visualization of Scatterplots for all 4 combinations of 'Minerals' and 'Altitude' and their categories. 
        - 04_RQ3-3_Visualization-Boxplots: 2x1 Visualization of Boxplots for the 'Altitude' and 'Altitude Category' with the 'Mineral Category'. 
        - 04_RQ3-4_Viszualization-Histogram: 1x1 Visualization with a Histogram on the 'Mineral Category' by 'Altitude Category'.

**05 Documentation:**
    - 05-1_CIP02_209_Feasability-Study: This is the submitted Feasability Study for the Project. 
    - 05-2_CIP02_209_Documentation: This is the final Project Documentation. 
