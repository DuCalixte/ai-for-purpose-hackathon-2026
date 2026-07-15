# AI4Purpose 2026 Hackathon
# Hospital Financial Analytics Engine
## Vaginal Delivery Case Report: 2021-2024 NYC Births
## The Privately Insured Birthing Individuals

### Project Summary
The purpose of this project is to evaluate factors that are associated with hospital billings and reimbursement among New York City (NYC) Area Hospitals for female patients admitted for routine vaginal birth.  This Analysis is restricted to privately insured patients.  Dues to limitation in the publicly available data, we could only identified those insured with Blue Cross/Blue Shield (assumed to be private) and those explicitely labeled as private insurance (no information on which propriatary company).  We further restrict the data to only include low mortality risk patients and those with extreme illness description.  Lastly, due to the low number of birth among those younder than 18, we excluded them from the analysis.  Of note, due to data privacy, the actual maternal age is not included.  For those under 18, they are grouped as 0-17.  Thus, they were removed.  Furthermore, while some birthing individual were lsited as 50 and older, they were excluded from the analysis due to increase risk of SMM in the aging maternal population. Of particular interest, is a comparison of cost distribution by hospital types (public, private, or community). 

For this project, we tackled 4 outcomes:  total charges (Total charges for the discharge), total costs (Total estimated cost for the discharge), cost differential (derived as total costs - total charges), and total costs ≥ 50% total charges.  

## Project Analytic Steps
### Data Source
We extracted 2021 to 2024 Statewide Planning and Research Cooperative System (SPARCS) Inpatient De-identified File from (https://healthdata.gov/).  The files contains discharge level detail on patient characteristics, diagnoses, treatments, services, and charges. Each extracted .csv file contains at least 2.1M unique discharges.  Due to limitation of the data, it is not possible to link dischages from the same individuals within and across the multiple years.  However, due to the nature of the project (Vaginal Delivery Cost Analysis), we do not anticipate to have many instances of multiple delivery fromt he same person within the same year as multiple pregnancy in a 12-month period is extremely rare (0.2%).  Also, we expect those events to be independent of each other even if they came from the same individual.
### Data Pre-Processing
Data pre-processing was implemented in R/Rsudio using rmarkdown for better code flow.  We use the readr package to import the extracted .csv files.  We use the clean_names function from janitor to clean the name of the variables.  We convert numeric data such as lengh of hospital stay, total charges, birth weight, and total cost from character to numeric when necessary and create a sparcs master file.  

For this project, we tackled 4 outcomes:  total charges (Total charges for the discharge), total costs (Total estimated cost for the discharge), cost differential (derived as total costs - total charges), and total costs ≥ 50% total charges.  We created an indicator variable from the ratio of total costs to total charges to identify those cases where the total costs was at least 50% of the total charges.

Hospitals were recategorized based on their name and confirmed affiliation.  All H+H hospitals along with University Hospital at Brooklyn (SUNY Downstate) were recategorized as Public, Hospitals belonging to NYU Langone Health, Mount Sinai System, Montefiore, Northwell, Columbia/Cornell Presbyterian etc. were categorized as Private.  All others hospitals (Brookdale, Interfaith, etc.) were categorized Community.  

The final analytic database comprises of 96,387 vaginal delivery discharge across the 5 boroughs of NYC.  Hospitals in New York (Manhattan) county were listed as either New York or Manhattan.   We recode all Manhattan as New York for consistent county names across the data.  This dataset was extracted as a .csv file to be used with the shinyapp to provide the use as ummary of the data behind the engine pre-splitting.

### Data Summary
We summarize the full analytic sample using mean with standard deviation and frequency with percentage across the 4 years and compraed characteristics across years using chi-square test and one-way analysis of variance (ANOVA).

We filter out the variables of interest out of the final analytic dataset to facilitate data modeling using the ML engine.

### Machine Learning
We randomly split the data into training set (70%) and test set (30%).  Using tidymodels, we create a set of surpervise machine learning model (linear regression, ridge regression, regression tree, random forest, and gradient boosting) for continuous variables and a classification set of models (logistic regression, decision tree, random forest, and gradient boosting) for the binary variable.  Models were compared to find a champiom model (RMSE for continous, accurary and ROC for binary).  The champion model across each outcome was retained and using the vetiver and pins packages.

### Shiny App Case Simulator
We then create and launch a shinyapp that display the result of the champion models and summarize the full analytic sample.  The shinyapp can be accessed at https://rcalixte.shinyapps.io/Maternal_Health_Simulation_Report/.  The app can simulate different case scenario and provide the predicted financial outcome based on the input categories and generate a report for the end-user.

### Project Replication

The project can be replicated across different types of inpatient services for New York City by filtering the variable APR DRG Description (The APR-DRG Classification Code Description) diagnosis of interest. And run the main project rmarkdown code (sparcs_data_analysis.Rmd) to save and deploy champion models for these cost-related outcomes.

### Analytic Worklow
The rmarkdown (sparcs_data_analysis.Rmd) file can be knitted as one file or in chunk in the order the chuncks appears in the code.  The end user should make sure that the data loading code chunck links to the appropriate folder location for their sparcs data.  It is imperative the the end user check the variable types before running the code to make sure that they don't accidentally/unnecessarily corrupt/change their data.

Once they run the code and identify and store their champion model, they can run the shinyapp (app.R) code to create the shinyapp dashboard for the project.  Lastly, the local file interact with report.Rmd to create a report for their finalcial report case simulator.

### Future LLM Chatbot
We plan to use a lightweight API microservice in R to host the ML models, and use Python's Gemini Function Calling to let the LLM talk to the API.