import json


def load_users():
    with open("users.json") as f:
        return json.load(f)


def calculate_pay(role, hours):
    rates = {"admin": 80, "user": 50, "manager": 65}
    rate = rates.get(role, 40)
    return rate * hours


def generate_report(users):
    report = []
    for u in users:
        pay = calculate_pay(u["role"], 40)
        report.append({"username": u["username"], "weekly_pay": pay})
    return report


def main():
    users = load_users()
    report = generate_report(users)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
