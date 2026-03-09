# Mail Provider Notes

## Gmail

Preferred path:
- Enable 2-Step Verification on the Google account.
- Create an App Password for mail access.
- Use IMAP instead of browser automation whenever possible.

Typical IMAP details to verify at setup time:
- IMAP host: `imap.gmail.com`
- IMAP port: `993`
- Security: SSL/TLS
- Username: full Gmail address
- Password: Google App Password

Notes:
- Some accounts or org-managed Google Workspace accounts may restrict app passwords.
- If app passwords are unavailable, OAuth may be required.

## 163 Mail

Preferred path:
- Enable IMAP/SMTP service in mailbox settings.
- Generate a client authorization code.
- Use the authorization code instead of the normal mailbox login password.

Typical IMAP details to verify at setup time:
- IMAP host: `imap.163.com`
- IMAP port: `993`
- Security: SSL/TLS
- Username: full 163 address
- Password: client authorization code

Notes:
- Mail service toggles sometimes live under account / POP3/SMTP/IMAP settings.
- If the provider blocks login attempts, verify service enablement and whether a fresh authorization code is required.

## Recommended setup checklist

For each mailbox, confirm:
- email address
- IMAP enabled
- app password / authorization code created
- whether the user wants read-only monitoring first
- what counts as important mail

OpenClaw config suggestion for 163:
- Primary mailbox:
  - `skills.entries["mail-monitor"].env.MAIL_163_ADDRESS`
  - `skills.entries["mail-monitor"].env.MAIL_163_APP_PASSWORD`
  - `skills.entries["mail-monitor"].env.MAIL_163_IMAP_HOST`
  - `skills.entries["mail-monitor"].env.MAIL_163_IMAP_PORT`
  - `skills.entries["mail-monitor"].env.MAIL_163_IMAP_SECURITY`
- Secondary mailbox:
  - `skills.entries["mail-monitor"].env.MAIL_163_SECONDARY_ADDRESS`
  - `skills.entries["mail-monitor"].env.MAIL_163_SECONDARY_APP_PASSWORD`
  - `skills.entries["mail-monitor"].env.MAIL_163_SECONDARY_IMAP_HOST`
  - `skills.entries["mail-monitor"].env.MAIL_163_SECONDARY_IMAP_PORT`
  - `skills.entries["mail-monitor"].env.MAIL_163_SECONDARY_IMAP_SECURITY`

OpenClaw config suggestion for Gmail:
- `skills.entries["mail-monitor"].env.MAIL_GMAIL_ADDRESS`
- `skills.entries["mail-monitor"].env.MAIL_GMAIL_APP_PASSWORD`
- `skills.entries["mail-monitor"].env.MAIL_GMAIL_IMAP_HOST`
- `skills.entries["mail-monitor"].env.MAIL_GMAIL_IMAP_PORT`
- `skills.entries["mail-monitor"].env.MAIL_GMAIL_IMAP_SECURITY`

## Monitoring advice

Start with manual inbox checks. After login is proven stable, add automation for:
- unread mail summaries
- verification code lookups
- periodic high-priority sender checks

Avoid enabling destructive mailbox actions by default.
