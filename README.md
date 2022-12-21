# Job openings scrapper

### Aim: 

Get a random sample of job openings from the API reed dot co dot uk from specific locations and using specific concepts for search. The code allows to exclude jobs depending from a variety of criteria, such as not applying twice to the same company or branch, or above a specific salary. The code also allows to insert empty or pre-filled columns in the final file.

### Context: 

I developed this code to conduct an online correspondence audit field experiment. Feel free to reach me if you would like to talk about how to implement it in a similar experiment.

This work was supported by the British Academy [PF19\100020]; the European Union-NextGenerationEU, Ministry of Universities and Recovery, Transformation and Resilience Plan, through a call from Pompeu Fabra University [Maria Zambrano Fellowship]; and the Oxford’s Sociology Department ‘Inspiration Fund 2022’.

### Requirements: 

Excel file entitled offers_previously_applied.xlsx with columns Jobid (id from the job opening), employerName (name of the company), location_original (location from which the job has been searched) and a column called ('Reapply?'). This last column should be filled manually with a 'Yes' if he wants that the code choose other jobs from the company/branch (e.g. because the job opening selected is not  suitable from the needs of the researcg) or 'No' if no other job from the company/branch should be chosen. A sample of the file can be seen in the Github page also containing this code.

There is also need of a file entitled api_reed_password.txt in the Working Directory including the password for the reed dot co dot uk API.

### Outputs: 

· CSV file with all emails downloaded (CRUK_job_offers_population.csv) and a file with the jobs to apply to (applications + date.csv).

· This is one the first code code I share publicly. Please, feel free to reach me to suggest any improvements.
