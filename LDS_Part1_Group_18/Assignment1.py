import csv


# ------------------------------ Opening files ------------------------------
''' 
Splitting into lists of lists
Each list inside 'answers_split' and 'subjects_split' is a row 
'''

# Path 
path_answers = "H:/Il mio Drive/Università/Progetto LDS/answerdatasetnew/answerdatacorrect.csv"
path_subjects = "H:/Il mio Drive/Università/Progetto LDS/answerdatasetnew/subject_metadata.csv"

answers_split = [] 
subjects_split = []

with open(path_answers, 'r') as answers:
    answers = csv.reader(answers, delimiter=',', quotechar='"')
    for row in answers:
        answers_split.append(row)
        
with open(path_subjects, 'r') as subjects:
    subjects = csv.reader(subjects, delimiter=',', quotechar='"')
    for row in subjects:
        subjects_split.append(row)



# -------------------- Converting columns into the right data type --------------------
'''
csv module imports everything as a string, including the list in column "subjectid".
'''

def convertToInt(table, list_of_col_idx):
    for row in table[1:]: # Skip header
        for e in list_of_col_idx:
            try:
                row[e] = int(row[e])
            except ValueError:  # To avoid problems with 'NULL'
                continue
    return table

def convertToList(table, idx): # Useful for subject id
    for row in table[1:]: # Skip header
        row[idx] = row[idx][1:-1] # Removing square brackets
        row[idx] = row[idx].split(',') # Splitting into a list
        row[idx] = [int(num) for num in row[idx]] # Converting str to int
    return table

def convertToFloat(table, list_of_col_idx):
    for row in table[1:]: # Skip header
        for e in list_of_col_idx:
            try:
                row[e] = float(row[e])
            except ValueError:  # To avoid problems with 'NULL'
                continue
    return table


answers_split = convertToInt(answers_split, [0, 1, 2, 3, 4, 5, 10, 11])
subjects_split = convertToInt(subjects_split, [0, 2, 3])
answers_split = convertToList(answers_split, 13)
answers_split = convertToFloat(answers_split, [7,9,12]) # str into float, then...
answers_split = convertToInt(answers_split, [7,9,12]) # float into int




# --------------------------------- Attaching Continent to answers file -----------------------------------
''' 
Importing file obtained from Excel (Dati > Recupera dati > Da altre origini > Da Web)
Source: https://country-code.cl/ 
'''

path_continent = 'H:/Il mio Drive/Università/Progetto LDS/LDS PART1 Group_18/data/countrycode_continent.csv'
continent_split = []  # Each list inside this is a row

with open(path_continent, 'r') as continent:
    lines_continent = continent.readlines()
    for e in lines_continent[1:]: # removing header
        e = e.split(';')
        e[-1] = e[-1][:-1] # removing '\n' at the end of each country code
        continent_split.append(e)

def getContinent(table, table_column_index, continent_table, country_index, continent_index):
    table[0].append('Continent')  # Updating header
    for row1 in table: 
        for row2 in continent_table: # For each row in the obtained country-continent file
            if row1[table_column_index] == row2[country_index]: # If the countries coincide
                row1.append(row2[continent_index])
            elif row1[table_column_index] == 'uk': # missing
                row1.append('EU')
            
    return table


answers_split = getContinent(answers_split, -1, continent_split, -1, 0)



# ---------------------------------- Creating the attribute "isCorrect" -----------------------------------
'''
Checks correspondence btw answer given and corret answer
'''

def checkCorrectness(table, idx_col1, idx_col2):
    table[0].append('isCorrect') # Updating header
    for row in table[1:]:
        if row[idx_col1] == row[idx_col2]: # If AnswerValue = CorrectAnswer
            row.append(1)
        else:
            row.append(0)
    return table


answers_split = checkCorrectness(answers_split, 3, 4)



# ------------------------------------ Getting subject description ------------------------------------
''' 
Every topic has 4 levels of depth (e.g. Maths > Geometry > Triangles > Pythagoras).
'Description' should be a string that contains the levels from 0 to 3, sorted 
'''

def getDescription(table_answer, table_subject, answer_col_idx):
    table_answer[0].append('Description') # Updating header
    for row_answer in table_answer[1:]:
        sorted_list = [] # Use to sort subject ids by level
        description = ''
        
        for e in row_answer[answer_col_idx]:
            
            for row_subject in table_subject:
                if e == row_subject[0]: # If subject id ans. =  subject id sub.
                    y = [e, row_subject[-1]]
                    sorted_list.append(y) # Appending subject and level
                    
        sorted_list.sort(key=lambda x: x[1]) # Sorting by level
        sorted_list = [item[0] for item in sorted_list] # Taking first element only
                    
        row_answer[answer_col_idx] = sorted_list # Sorting subject id column
                
        for f in sorted_list:
            for row_subject in table_subject:
                if row_subject[0] == f: # when the elements in sorted_list match w/ subj. id
                    description += row_subject[1] + ' | '
                  
        row_answer.append(description[:-3]) # Removing the last separator
    
    return table_answer



answers_split = getDescription(answers_split, subjects_split, 13)



# ----------------------------------- Transforming dates into ids -----------------------------------
'''
The date format is transformed from YYYY-MM-DD to YYYYMMDD. 
This new format is used as the id.
'''

def simplifyDate(table, idx):
    for row in table[1:]: # Skip header
        row[idx] = row[idx].split(' ')
        row[idx] = row[idx][0] # Excluding hours and minutes
    return table


def transformDate(table, idx_date): # from YYYY-MM-DD to YYYYMMDD (id format)
    for row in table[1:]:
        if len(row[idx_date]) == 10:
            row[idx_date] = row[idx_date].replace('-','')
    return table


answers_split = simplifyDate(answers_split, 8)
answers_split = transformDate(answers_split, 8)# date answered
answers_split = transformDate(answers_split, 6) # date of birth



# ---------------------------------------------- Gender ----------------------------------------------
'''
Inferring the gender, currently expressed as 1 or 2.
'''

def findMajorityGender(table, column):
    one = 0
    two = 0
    for row in table[1:]:
        if row[column] == 1:
            one += 1
        else:
            two += 1
    return one,two

#print(findMajorityGender(answers_split, 5))

'''
1 = 272630, 2 = 266205

The Users are too young to be in college/university, therefore no argument regarding males and 
females in STEM courses can be made. 

Given the gender ratio in the countries listed in the data (mostly western countries and oceania), 
the majority class should be F.

Source: https://ourworldindata.org/gender-ratio
'''

def getGender(table, column):
    for row in table[1:]:
        if row[column] == 1:
            row[column] = 'F'
        else:
            row[column] = 'M'
    return table

answers_split = getGender(answers_split, 5)



# ---------------------------------------- Generating ids ----------------------------------------
'''
Missing ids: geoid, organizationid
'''


def idCreator(table, cols, id_name):  # cols is a list of columns
    table[0].append(id_name) # Updating header
    
    # Creating a dictionary to generate identifiers
    id_counter = 0
    d = {} # Key = id; Value = grouped attributes that form a distinct entity
    for row in table[1:]:
        values = [row[v] for v in cols]
         
        if values not in d.values(): # If grouped not in d yet
            id_counter += 1  # Generating new id 
            d[id_counter] = values  # The list is the value of d
            
    # Assigning id to each row
    for row in table[1:]:
        values = [row[v] for v in cols]
        
        for key, value in d.items():
            if values == value:
                row.append(key)
                
    return table


answers_split = idCreator(answers_split, [15], 'geoid') # Using Region as reference
answers_split = idCreator(answers_split, [10,11,12], 'organizationid') # groupid + quizid + sch.ofworkid



# ----------------------------- Transforming subjectid into a string -----------------------------
'''
Subject id is currently a list of integers. We need to transform it into an id (string).
'''

def listToString(table, idx):
    for row in table[1:]:
        row[idx] = [str(x) for x in row[idx]]
        row[idx] = '-'.join(row[idx])
    return table


answers_split = listToString(answers_split, 13)



# ---------------------------------------- Exporting csv ----------------------------------------

with open('./data/answers_fulldata_clean.csv','w',newline='') as f:
    writer = csv.writer(f)
    writer.writerows(answers_split)



# ------------------------------- Splitting data into different tables ------------------------------
'''
Every table is a list of lists (rows).
'''

data = answers_split # to avoid confusion

#  Function to create dimension tables 
def createDimensionTable(data, id_col, cols_to_include, header):
    output = set() # set to avoid duplicates
    
    # Inserting rows
    for row in data[1:]:
        subset = [row[c] for c in cols_to_include] # subset of attributes to be included in output
        subset = tuple(subset)
        output.add(subset)  # cannot add lists to set (lists are mutable)
    
    # Transforming immutable objects into mutable ones
    output = list(output) # set to list
    output = [list(t) for t in output] # tuples to lists
    
    # Sorting by id
    output.sort(key=lambda x: x[id_col])
    
    # Inserting header
    output.insert(0, header)
    
    return output
    

# Function to create fact table
def createFactTable(data, cols_to_include):
    output = []
    # Inserting rows
    for row in data:
        subset = [row[c] for c in cols_to_include] # subset of attributes to be included in output
        output.append(subset)  
    
    return output


# Creating tables
answers = createFactTable(data, [2,0,1,21,8,13,4,3,18,9]) # fact table
organization = createDimensionTable(data, 0, [21,10,11,12], ['organizationid','groupid','quizid','schemeofworkid'])
date = createDimensionTable(data, 0, [8], ['dateid'])
user = createDimensionTable(data, 0, [1,6,20,5], ['userid','dateofbirth','geoid','gender'])
geography = createDimensionTable(data, 0, [20,15,16,17], ['geoid','region','country_name','continent'])
subject = createDimensionTable(data, 0, [13,19], ['subjectid','description'])


# For date we create a second table (date of birth) and we append it to the previous one
date_of_birth = createDimensionTable(data, 0, [6], ['dateid'])

for el in date_of_birth[1:]:
    date.append(el)
date = sorted(date)
date.insert(0, date.pop(-1)) # Putting header back to the top
    


# ------------------------------------ Adding attributes to date column -----------------------------------
'''
Obtaining day, month, year and quarter. Adding them to the date table.
'''

def getDate(table, idx): #get back date format from id
    table[0].append('date') # updating header
    for row in table[1:]:
        result = row[idx]
        result = result[:6] + '-' + result[6:]
        result = result[:4] + '-' + result[4:]
        row.append(result)
    return table


def getDayMonthYear(table, idx_date):
    table[0].append('Day')
    table[0].append('Month')
    table[0].append('Year')
    for row in table[1:]:
        date_splitted = row[idx_date].split('-')
        day = date_splitted[2]
        month = date_splitted[1]
        year = date_splitted[0]
        
        if day[0] == '0': # Problems converting days or months starting with zero
            day = day[1:] # If first char = 0 remove it
        row.append(int(day))
        
        if month[0] == '0':
            month = month[1:] # If first char = 0 remove it
        row.append(int(month))
        
        row.append(int(year))
    return table


def getQuarter(table, idx_month):
    table[0].append('Quarter')
    for row in table[1:]:
        if row[idx_month] in range(1,4):
            row.append(1)
        elif row[idx_month] in range(4,7):
            row.append(2)
        elif row[idx_month] in range(7,10):
            row.append(3)
        elif row[idx_month] in range(10,13):
            row.append(4)
    return table


date = getDate(date, 0)
date = getDayMonthYear(date, 1)
date = getQuarter(date, 3)



# ------------------------------------ Exporting tables as csv -----------------------------------
'''
Exporting as csv, therefore the data types will be converted to strings.
'''

with open('./data/answers.csv','w',newline='') as a:
    writer = csv.writer(a)
    writer.writerows(answers)
    
with open('./data/organization.csv','w',newline='') as o:
    writer = csv.writer(o)
    writer.writerows(organization)
    
with open('./data/date.csv','w',newline='') as d:
    writer = csv.writer(d)
    writer.writerows(date)
    
with open('./data/user.csv','w',newline='') as u:
    writer = csv.writer(u)
    writer.writerows(user)
    
with open('./data/geography.csv','w',newline='') as g:
    writer = csv.writer(g)
    writer.writerows(geography)
    
with open('./data/subject.csv','w',newline='') as s:
    writer = csv.writer(s)
    writer.writerows(subject)