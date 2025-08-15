def fetch_csv_emails(date_str):
    from datetime import datetime

    try:
        targetdate = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        logger.error(f"Invalid date format: {date_str}. Expected YYYY - MM - DD.")
        return

    logger.info(f"Fetching CSV emails for date: {target_date}")

    config = load_config()
    globalfilter = config.get("global_email_filter", {})
    attachment_rules = config.get("attachments", {})

    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    inbox = outlook.GetDefaultFolder(6)  # Inbox
    messages = inbox.Items
    messages.Sort("[ReceivedTime]", True)

    for msg in messages:
        try:
            receiveddate = msg.ReceivedTime.date()
            if received_date != target_date:
                continue

            if not is_valid_email(msg, global_filter):
                logger.info(f"Skipping email from {msg.SenderEmailAddress} with subject: {msg.Subject}")
                continue

            for i in range(1, msg.Attachments.Count + 1):
                attachment = msg.Attachments.Item(i)
                filename = attachment.FileName

                if not filename.lower().endswith(".csv"):
                    logger.info(f"Skipping non - CSV attachment: {filename}")
                    continue

                rule = get_attachment_rule(filename, attachment_rules)
                if not rule:
                    logger.info(f"Skipping attachment '{filename}' — no matching config rule")
                    continue

                # Append date to filename
                base_name, extension = os.path.splitext(filename)
                newfilename = f"{sanitize_filename(base_name)}__{target_date}{extension}"
                os.makedirs(SAVE_DIR, exist_ok=True)
                savepath = os.path.join(SAVE_DIR, new_filename)
                attachment.SaveAsFile(save_path)

                logger.info(f"Saved: {new_filename} | From: {msg.SenderName} | Received: {received_date} | Rule Range: {rule['range']}")

        except Exception as e:
            logger.error(f"Failed to process email: {e}", exc_info=True)