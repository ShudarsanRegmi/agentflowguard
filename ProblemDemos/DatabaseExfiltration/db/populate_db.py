import pymysql
import random

# Connection configuration
db_config = {
    'host': 'localhost',
    'user': 'aparichit',
    'password': 'letmelogin',
    'database': 'company_db',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# Sample lists for generating fake company data
first_names = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", 
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", 
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa", 
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley", 
    "Steven", "Dorothy", "Paul", "Kimberly", "Andrew", "Emily", "Joshua", "Donna"
]

last_names = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", 
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", 
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", 
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", 
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores"
]

departments = [
    "Engineering", "Human Resources", "Sales", "Marketing", "Finance", 
    "Product Management", "Legal", "Operations"
]

dept_salary_ranges = {
    "Engineering": (85000, 160000),
    "Human Resources": (55000, 95000),
    "Sales": (60000, 120000),
    "Marketing": (58000, 110000),
    "Finance": (75000, 140000),
    "Product Management": (90000, 150000),
    "Legal": (100000, 190000),
    "Operations": (50000, 90000)
}

projects_list = [
    ("Project Apollo", 250000.00, "In Progress"),
    ("Project Phoenix", 150000.00, "Completed"),
    ("Project Titan", 500000.00, "Planning"),
    ("Project Genesis", 180000.00, "In Progress"),
    ("Project Nebula", 95000.00, "On Hold"),
    ("Project Odyssey", 320000.00, "In Progress"),
    ("Project Aurora", 120000.00, "Planning"),
    ("Project Orion", 450000.00, "Completed")
]

review_comments = {
    1: [
        "Consistent performance issues. Fails to meet project deadlines.",
        "Needs immediate improvement in communication and teamwork.",
        "Has struggled to adapt to new technologies and processes."
    ],
    2: [
        "Sometimes misses deliverables. Needs closely managed guidance.",
        "Technical skills are adequate, but collaboration can be improved.",
        "Meets some goals but often requires assistance to finish tasks."
    ],
    3: [
        "Solid performer. Consistently delivers work on time.",
        "Good team member. Communicates well and works efficiently.",
        "Meets all expectations and contributes positively to the team."
    ],
    4: [
        "Exceeds expectations. Takes initiative on new projects.",
        "Strong technical skills and excellent team collaborator.",
        "Highly reliable and often helps team members solve problems."
    ],
    5: [
        "Outstanding performance. A key pillar of the department.",
        "Demonstrates exceptional leadership and technical excellence.",
        "Consistently delivers high-impact results ahead of schedule."
    ]
}

def populate():
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # 1. Populate Projects
            print("Populating projects...")
            for idx, proj in enumerate(projects_list):
                project_id = 201 + idx
                name, budget, status = proj
                sql = "INSERT INTO projects (project_id, project_name, budget, status) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (project_id, name, budget, status))
            
            # 2. Populate Employees
            print("Populating employees...")
            employees_data = []
            used_emails = set()
            
            # Generate 45 employees
            for i in range(45):
                emp_id = 101 + i
                
                # Make sure names are relatively unique
                first = random.choice(first_names)
                last = random.choice(last_names)
                name = f"{first} {last}"
                
                email = f"{first.lower()}.{last.lower()}@nexustech.com"
                counter = 1
                while email in used_emails:
                    email = f"{first.lower()}.{last.lower()}{counter}@nexustech.com"
                    counter += 1
                used_emails.add(email)
                
                dept = random.choice(departments)
                min_sal, max_sal = dept_salary_ranges[dept]
                salary = round(random.uniform(min_sal, max_sal), 2)
                
                phone = f"+1-555-{random.randint(100,999):03d}-{random.randint(1000,9999):04d}"
                credit_card = f"{random.randint(4000, 4999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
                
                sql = "INSERT INTO employees (employee_id, name, email, department, salary, phone, credit_card) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (emp_id, name, email, dept, salary, phone, credit_card))
                employees_data.append(emp_id)
                
            # 3. Populate Performance Reviews
            print("Populating performance reviews...")
            # Give reviews to about 30 random employees
            reviewed_employees = random.sample(employees_data, 30)
            for idx, emp_id in enumerate(reviewed_employees):
                review_id = 301 + idx
                rating = random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.15, 0.40, 0.30, 0.10])[0]
                comment = random.choice(review_comments[rating])
                
                sql = "INSERT INTO performance_reviews (review_id, employee_id, rating, comments) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (review_id, emp_id, rating, comment))
                
        connection.commit()
        print("Database population completed successfully!")
        
    except Exception as e:
        connection.rollback()
        print(f"Error during population: {e}")
        raise e
    finally:
        connection.close()

if __name__ == '__main__':
    populate()
