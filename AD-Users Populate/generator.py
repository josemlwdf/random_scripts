import csv
import random

# Define the headers
headers = [
    "FirstName", "Initials", "Lastname", "Username", "Email", "StreetAddress", 
    "City", "ZipCode", "State", "Department", "Telephone", "JobTitle", "Company", "OU"
]

# Define an array of names
names = [
    "Alice", "Bob", "Charlie", "David", "Eva", "Frank", "Grace", "Hannah", "Isaac", "Judy",
    "Kevin", "Laura", "Mike", "Nina", "Oliver", "Paul", "Quincy", "Rachel", "Steve", "Tina",
    "Uma", "Victor", "Wendy", "Xander", "Yvonne", "Zach", "Aaron", "Beth", "Carl", "Diana",
    "Eli", "Fiona", "George", "Helen", "Ian", "Jack", "Karen", "Liam", "Mona", "Nathan",
    "Olivia", "Peter", "Quinn", "Rita", "Sam", "Tracy", "Ursula", "Vincent", "Willow", "Xenia",
    "Yara", "Zane", "Adam", "Bianca", "Cody", "Delia", "Eric", "Faith", "Gavin", "Harper",
    "Ivy", "Jake", "Kylie", "Leo", "Megan", "Noah", "Opal", "Penny", "Quinton", "Rose",
    "Sean", "Tara", "Ulysses", "Violet", "Wyatt", "Ximena", "Yusuf", "Zara", "Aiden", "Bella",
    "Colin", "Daisy", "Ethan", "Felix", "Gloria", "Henry", "Iris", "John", "Kate", "Lila",
    "Mark", "Nora", "Oscar", "Paula", "Quinn", "Reed", "Sophie", "Tom", "Una", "Vera"
]

# Define other possible random values for the fields
streets = ["123 Elm St", "456 Oak St", "789 Pine St"]
cities = ["Springfield", "Rivertown", "Lakeside"]
states = ["CA", "NY", "TX"]
departments = ["HR", "Engineering", "Sales","IT", "Support", "Dev"]
job_titles = ["Manager", "Developer", "Analyst"]
companies = ["CompanyA", "CompanyB", "CompanyC"]

# OU field value
ou = "OU=Users,,DC=soupdecode,DC=local"

# Generate random data for each field
rows = []
for i in range(1000):
    first_name = random.choice(names)
    last_name = random.choice(names)
    username = f"{first_name[0].lower()}{last_name.lower()}{i}"
    email = f"{username}@example.com"
    street_address = random.choice(streets)
    city = random.choice(cities)
    zip_code = f"{random.randint(10000, 99999)}"
    state = random.choice(states)
    department = random.choice(departments)
    telephone = f"{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    job_title = random.choice(job_titles)
    company = random.choice(companies)
    
    row = [
        first_name, f"{first_name[0]}{last_name[0]}", last_name, username, email, 
        street_address, city, zip_code, state, department, telephone, job_title, company, ou
    ]
    rows.append(row)

# Write to CSV file
csv_file = "output.csv"
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    writer.writerows(rows)

print(f"CSV file '{csv_file}' created successfully.")
