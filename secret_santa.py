import argparse
import csv
import random
import smtplib
from string import Template


email_template = Template("""Hi $your_name,
Thanks for being a Secret Santa!

You are giving a gift to

$their_name
$their_address

Remember, keep it under $$25 total!

- Cameron's email robot
""")

def read_csv(path_to_csv):
    """
    Returns a list of dicts representing people
    """
    people = []
    with open(path_to_csv, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter="|", quotechar="|")
        for row in reader:
            people.append(row)
    return people

def randomize(people):
    assignments = {}
    recipients = [i for i in range(len(people))]

    for i in range(len(people)):
        found = False
        while not found:
            r = random.randint(0, len(recipients) - 1)
            recipient = recipients[r]
            is_same_person = recipient == i
            reciprocal_assignment = assignments.get(recipient, -1) == i
            if not is_same_person and not reciprocal_assignment:
                found = True
                assignments[i] = recipient
                recipients.remove(recipient)

    return assignments

def make_templates(people, assignments):
    emails_to_send = []

    for s, r in assignments.items():
        sender = people[s]
        recipient = people[r]
        email = {
            "to": sender["email"],
            "message": email_template.substitute(
                your_name=sender["name"],
                their_name=recipient["name"],
                their_address=recipient["address"]
            )
        }
        emails_to_send.append(email)

    return emails_to_send

def send_emails(emails_to_send, dry_run):
    if dry_run:
        for email in emails_to_send:
            print(email)

def main(path_to_csv, dry_run):
    people = read_csv(path_to_csv)
    assignments = randomize(people)
    emails_to_send = make_templates(people, assignments)
    send_emails(emails_to_send, dry_run)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send out Secret Santa pairings')
    parser.add_argument('--participants',
                        default=None,
                        help='Path to a CSV file of participants')
    parser.add_argument('--dry-run',
                        default=True,
                        help='Do not actually send emails')
    args = parser.parse_args()
    main(args.participants, args.dry_run)