import argparse
import csv
from email.message import EmailMessage
import os
import random
import smtplib
from string import Template

from dotenv import load_dotenv

load_dotenv()

# change this template as necessary
email_template = Template("""Hi $your_name,
Thanks for being a Secret Santa!

You are giving a gift to:

$their_name
$their_address

Remember, keep it under $$25 total!

- Nerding Santa's fascinating email robot
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
    """
    Return a dict of pairings, where each key and value is a position in the list of people
    """
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
                print(f"Giving a gift to {recipient}!")
                recipients.remove(recipient)

    return assignments

def make_templates(people, assignments):
    """
    Build email templates. Returns a list of {to: "email address", body: "email body"}
    """
    emails_to_send = []

    for s, r in assignments.items():
        sender = people[s]
        recipient = people[r]
        email = {
            "to": sender["email"],
            "body": email_template.substitute(
                your_name=sender["name"],
                their_name=recipient["name"],
                their_address=recipient["address"]
            )
        }
        emails_to_send.append(email)

    return emails_to_send

def send_emails(emails_to_send, dry_run):
    """
    Actually send emails
    """

    if dry_run:
        for email in emails_to_send:
            print(email)
        return

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_address = os.getenv("SMTP_ADDRESS")
    smtp_password = os.getenv("SMTP_PASSWORD")

    s = smtplib.SMTP(smtp_host, smtp_port)
    s.starttls()
    s.login(smtp_address, smtp_password)

    for email in emails_to_send:
        msg = EmailMessage()
        msg.set_content(email["body"])
        msg["Subject"] = "Nerding Secret Santa!"
        msg["From"] = smtp_address
        msg["To"] = email["to"]

        s.send_message(msg)

    s.quit()

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
                        default=False,
                        help='Do not actually send emails')
    args = parser.parse_args()
    main(args.participants, args.dry_run)
