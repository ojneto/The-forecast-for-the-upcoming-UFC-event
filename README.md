is project aims to calculate the victory probabilities for all fights in the upcoming UFC card, based on fighter statistics obtained from the website ufcstats.com. Specifically, the project focuses on forecasting the first event contained on the site: http://ufcstats.com/statistics/events/upcoming.

Methodology:

Initially, we trained a logistic regression model using fight data from the project 'UFC-Fight historical data from 1993 to 2021' by RAJEEV WARRIER, available on Kaggle (https://www.kaggle.com/datasets/rajeevw/ufcdata).

Next, we adapted parts of the code from the aforementioned project to obtain current statistics of the fighters on the analyzed card.

Project Execution:

To execute the project, follow these steps:

Ensure that the following Python packages are installed:

pandas, 
requests, 
BeautifulSoup, 
tqdm, 
datetime, 
joblib, 

Download the project files and save them in a folder of your choice.

Open the Jupyter Notebook "ufc_event_forecasting.ipynb".

Execute the notebook cell. This will calculate the victory probabilities for the fights in the upcoming UFC event based on fighter statistics.

After execution, the victory probabilities of the fights will be calculated and saved in the same folder where the project files are located.
