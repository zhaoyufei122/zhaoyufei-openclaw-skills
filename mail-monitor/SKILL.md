---
name: mail-monitor
description: Connect to and monitor personal email inboxes over IMAP, especially Gmail and 163 mail. Use when the user wants to read unread mail, check verification codes, summarize recent inbox activity, search messages by sender or subject, or set up recurring email monitoring with app passwords or authorization codes.
---

# Mail Monitor

Use this skill for mailbox access and inbox triage.

## Default approach

Prefer IMAP with app passwords / client authorization codes over web scraping.

Supported priority providers for this skill:
- Gmail
- 163 Mail

## Safety rules

- Treat mailbox credentials, app passwords, and authorization codes as secrets.
- Do not ask the user to paste long-lived secrets into normal chat unless they explicitly choose to.
- Prefer storing secrets in OpenClaw configuration or secrets management.
- Before sending mail, deleting mail, marking mail read, or moving mail, ask for confirmation unless the user clearly requested it.
- Reading and summarizing inbox contents is allowed after the user provides access.

## Workflow

1. Identify which mailbox the user wants connected.
2. Prefer IMAP access.
3. If credentials are not configured yet, guide the user through enabling IMAP and generating an app password / authorization code.
4. Once access exists, check only the minimum mailbox scope needed for the task.
5. Summarize results in concise Chinese unless the user asks otherwise.
6. For recurring checks, use cron reminders or a future mailbox polling script only after the access method is stable.

## What to collect from the user

Collect only what is necessary:
- Provider: Gmail or 163
- Email address
- Whether IMAP is enabled
- Whether an app password / client authorization code is available
- What kinds of messages matter: verification codes, bills, work mail, shipping notices, all unread, etc.

## Common tasks

### Read unread mail

Report:
- sender
- subject
- received time
- short summary
- whether anything looks urgent

### Find verification codes

Prioritize recent unread messages, and scan subject plus snippet first.

### Inbox summary

Group by:
- important
- needs action
- informational
- low priority

## Provider-specific notes

Read `{baseDir}/references/providers.md` when configuring Gmail or 163.

## Output style

Default to a compact structure:
- 邮箱
- 时间范围
- 重要邮件
- 其他邮件
- 建议动作

## Local script

If the 163 mailbox is configured through OpenClaw skill env, use `{baseDir}/scripts/read-163.js` to fetch recent inbox messages.

Suggested host env names:
- `MAIL_163_ADDRESS`
- `MAIL_163_APP_PASSWORD`
- `MAIL_163_IMAP_HOST`
- `MAIL_163_IMAP_PORT`
- `MAIL_163_IMAP_SECURITY`

## Limits

- Do not invent provider endpoints or auth steps; verify them when needed.
- If mailbox access is not configured yet, switch into setup guidance mode instead of pretending to read mail.
