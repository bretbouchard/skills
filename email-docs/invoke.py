#!/usr/bin/env python3
"""Email files via Gmail SMTP with SSL."""

import argparse
import glob
import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from pathlib import Path


def send_email(to: str, subject: str, files: list[str], body: str = ""):
    gmail_address = "bretbouchard@gmail.com"
    password_path = Path.home() / ".claude" / "secrets" / "gmail_app_password.txt"

    if not password_path.exists():
        print("ERROR: App password file not found at ~/.claude/secrets/gmail_app_password.txt")
        print("Create one at https://myaccount.google.com/apppasswords")
        sys.exit(1)

    app_password = password_path.read_text().strip()

    msg = MIMEMultipart()
    msg["From"] = gmail_address
    msg["To"] = to
    msg["Subject"] = subject

    if body:
        msg.attach(MIMEText(body, "plain"))

    for filepath in files:
        path = Path(filepath)
        if not path.exists():
            print(f"WARNING: {filepath} not found, skipping")
            continue

        part = MIMEBase("application", "octet-stream")
        part.set_payload(path.read_bytes())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename="{path.name}"')
        msg.attach(part)

    if not msg.get_payload():
        print("ERROR: No files to send")
        sys.exit(1)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_address, app_password)
        server.sendmail(gmail_address, to, msg.as_string())

    print(f"Sent {len(files)} file(s) to {to}")


def main():
    parser = argparse.ArgumentParser(description="Email files via Gmail")
    parser.add_argument("--to", default="bretbouchard@gmail.com", help="Recipient email")
    parser.add_argument("--subject", default=None, help="Email subject line")
    parser.add_argument("--body", default="", help="Email body text")
    parser.add_argument("files", nargs="+", help="Files to attach (supports glob patterns)")

    args = parser.parse_args()

    # Expand glob patterns
    all_files = []
    for pattern in args.files:
        matches = glob.glob(pattern)
        if matches:
            all_files.extend(matches)
        else:
            all_files.append(pattern)  # Let send_email warn about missing files

    # Auto-generate subject if not provided
    if args.subject is None:
        if len(all_files) == 1:
            args.subject = Path(all_files[0]).stem.replace("-", " ").replace("_", " ").title()
        else:
            args.subject = f"{len(all_files)} Files — {Path(all_files[0]).parent.name}"

    send_email(args.to, args.subject, all_files, args.body)


if __name__ == "__main__":
    main()
