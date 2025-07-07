import re
import email
import email.header
import requests
import imaplib
from loguru import logger
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta, timezone
from core.utils.decorators import retry


@retry
def get_accesstoken(refresh_token, client_id):
    logger.info(f"Attempting to get access token, client id: {client_id}")

    data = {
        "client_id": client_id,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    ret = requests.post(
        "https://login.microsoftonline.com/consumers/oauth2/v2.0/token", data=data
    )

    access_token = ret.json()["access_token"]
    logger.success(f"Client id: {client_id} - got access token!")

    return access_token


def generate_auth_string(user, token):
    logger.info(f"User: {user} - generating auth string")

    auth_string = f"user={user}\1auth=Bearer {token}\1\1"

    logger.success(f"User: {user} - got auth string!")

    return auth_string


def tuple_to_str(tuple_):

    if tuple_[1]:
        out_str = tuple_[0].decode(tuple_[1])
    else:
        if isinstance(tuple_[0], bytes):
            out_str = tuple_[0].decode("gbk")
        else:
            out_str = tuple_[0]
    return out_str


def get_latest_email_by_date(mail):
    logger.info("Searching for the latest message...")

    emails = []

    mail.select("JUNK")
    _, messages = mail.search(
        None, "SINCE", datetime.now(timezone.utc).strftime("%d-%b-%Y")
    )

    message_ids = messages[0].split()

    for msg_id in message_ids:
        try:
            ret, data = mail.fetch(msg_id, "(BODY[HEADER])")
            raw_header = data[0][1].decode("utf-8")

            date_match = re.search(r"^Date: (.+)$", raw_header, re.MULTILINE)
            if date_match:
                date_header = date_match.group(1).strip()
                logger.debug(f"Processing email {msg_id}: Date Header - {date_header}")

                email_date = parsedate_to_datetime(date_header)
                emails.append((msg_id, email_date))
            else:
                logger.warning(f"Email {msg_id} has no valid Date header.")

        except Exception as e:
            logger.error(f"Error processing email {msg_id}: {str(e)}")

    emails.sort(key=lambda x: x[1])

    if emails:
        latest_email_id, latest_email_date = emails[-1]
        logger.success(f"Latest Email ID: {latest_email_id}, Date: {latest_email_date}")

        latest_email_date_utc2 = latest_email_date.astimezone(
            latest_email_date.tzinfo
        ).replace(tzinfo=None) + timedelta(hours=2)
        logger.info(f"Latest Email Date (UTC+2): {latest_email_date_utc2}")
        return latest_email_id, latest_email_date
    else:
        logger.warning("No emails found.")
        return None, None


def fetch_email_body(mail, item):
    try:
        ret, data = mail.fetch(item, "(RFC822)")
        msg = email.message_from_string(data[0][1].decode("utf-8"))

        email_date = msg.get("Date")
        logger.debug(f"Processing email with Date: {email_date}")

        sub = msg.get("subject")
        sub_text = email.header.decode_header(str(sub))
        sub_detail = ""
        if sub_text[0]:
            sub_detail = tuple_to_str(sub_text[0])
            matches = re.findall(r"\b\d{6}\b", sub_detail)
            if matches:
                return matches[0]
        logger.debug(sub_detail)

        for part in msg.walk():
            if not part.is_multipart():
                content_type = part.get_content_type()
                name = part.get_filename()
                if not name:
                    txt = str(part.get_payload(decode=True))
                    if content_type == "text/html":
                        matches = re.findall(r"\b\d{6}\b", txt)
                        if matches:
                            return matches[0]
                        logger.info(txt)

        return None
    except Exception as e:
        logger.error(str(e))
        return None


def utc_to_utc_plus_2(date_time_utc):
    # Convert UTC datetime to UTC+2
    utc_plus_2 = timezone(timedelta(hours=2))
    return date_time_utc.astimezone(utc_plus_2)


def getmail(sel, mail):
    mail.select(sel)
    _, messages = mail.search(None, "ALL")
    all_emails = messages[0].split()

    all_emails = sorted(all_emails, reverse=True)

    for item in all_emails:
        fetch_email_body(mail, item)
    return None


def connect_imap(emailadr, access_token):
    mail = imaplib.IMAP4_SSL("outlook.live.com")
    mail.authenticate("XOAUTH2", lambda x: generate_auth_string(emailadr, access_token))
    latest_email_id, latest_email_date = get_latest_email_by_date(mail)

    if latest_email_date:
        result = fetch_email_body(mail, latest_email_id)
        mail.logout()
        return result
    mail.logout()
    return None
