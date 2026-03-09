# mail-monitor

IMAP-based inbox reading and triage for OpenClaw.

## Features

- Read recent inbox messages for Gmail and 163 mail
- Search recent messages by sender or subject keyword
- Mark unread inbox messages as read
- Support one Gmail account, one primary 163 account, and one secondary 163 account

## Requirements

- Node.js
- IMAP enabled on the mailbox provider
- App password / authorization code instead of the normal mailbox password

## Install

Inside the skill directory:

```bash
npm install
```

## Local configuration

Use local OpenClaw config or another local secret store. Do not commit real credentials.

See `examples/env.example.json` for a template.

## Scripts

- `npm run read:gmail`
- `npm run read:163`
- `npm run read:163-secondary`
- `npm run search:gmail -- Hairhood`
- `npm run search:163 -- verification`
- `npm run markread:gmail`
- `npm run markread:163`
- `npm run markread:163-secondary`

## Notes

This skill currently focuses on inbox reading and read-state updates. It does not send, delete, or move mail by default.
