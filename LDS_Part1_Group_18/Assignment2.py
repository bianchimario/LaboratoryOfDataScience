import csv
import pyodbc

# ---------- Connecting to the database and creating the cursor ----------
server = 'tcp:lds.di.unipi.it'
database = 'Group_18_DB'
username = 'Group_18' 
password = 'W19BF2T6'
connectionString = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password
cnxn = pyodbc.connect(connectionString)
cursor = cnxn.cursor()



# ---------------------------- Opening files ----------------------------
'''
We open the 6 tables created in Assignment1.py
'''

answers = []
organization = []
date = []
user = []
geography = []
subject = []


with open('./data/answers.csv','r',newline='') as a:
    a = csv.reader(a, delimiter=',', quotechar='"')
    for row in a:
        answers.append(row)
    
with open('./data/organization.csv','r',newline='') as o:
    o = csv.reader(o, delimiter=',', quotechar='"')
    for row in o:
        organization.append(row)
    
with open('./data/date.csv','r',newline='') as d:
    d = csv.reader(d, delimiter=',', quotechar='"')
    for row in d:
        date.append(row)
    
with open('./data/user.csv','r',newline='') as u:
    u = csv.reader(u, delimiter=',', quotechar='"')
    for row in u:
        user.append(row)
    
with open('./data/geography.csv','r',newline='') as g:
    g = csv.reader(g, delimiter=',', quotechar='"')
    for row in g:
        geography.append(row)
    
with open('./data/subject.csv','r',newline='') as s:
    s = csv.reader(s, delimiter=',', quotechar='"')
    for row in s:
        subject.append(row)



# ------------------------- Changing data types -------------------------
'''
csv module imports everything as a string. 
Since in the clean version of the data we have either strings or integers,
we just need a function to convert attributes from strings to integers.
'''

def convertToInt(table, list_of_col_idx):
    for row in table[1:]: # Skip header
        for e in list_of_col_idx:
            try:
                row[e] = int(row[e])
            except ValueError:  # To avoid problems with 'NULL'
                continue
    return table


answers = convertToInt(answers, [0,1,2,3,4,5,6,7,8,9])
organization = convertToInt(organization, [0,1,2,3])
date = convertToInt(date, [0,2,3,4,5])
user = convertToInt(user, [0,1,2])
geography = convertToInt(geography, [0])




# --------------------------- Uploading files ---------------------------
'''
To avoid FK errors it is important to populate dimension tables first.
'''


def sqlUploader(table, tab_name):
    # Cleaning the table (TRUNCATE returns error because there is a FK constraint)
    # Square brackets to avoid errors with reserved SQL keywords (e.g. User)
    sql_delete = 'DELETE FROM [{}].[{}];'.format(username,tab_name)
    cursor.execute(sql_delete)
    print(tab_name, ': deleted')
    
    for row in table[1:]: # Skipping header
        sql_insert_into = 'INSERT INTO [{}].[{}] VALUES'.format(username,tab_name)
        sql_values = str(tuple([x for x in row]))
        sql_final = sql_insert_into + sql_values
        cursor.execute(sql_final)
    
    cnxn.commit()
    print(tab_name, ': uploaded')
    return table


sqlUploader(geography, 'Geography')
sqlUploader(date, 'Date')
sqlUploader(organization, 'Organization')
sqlUploader(subject, 'Subject')
sqlUploader(user, 'User')
sqlUploader(answers, 'Answers')



# ----------------- Closing cursor and connection -----------------

cursor.close()
cnxn.close()