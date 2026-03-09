const { ImapFlow } = require('imapflow');

async function main() {
  const provider = (process.argv[2] || '').toLowerCase();
  if (!provider) throw new Error('Usage: node scripts/mark-read-imap.js <gmail|163|163-secondary>');

  const prefix = provider === 'gmail'
    ? 'MAIL_GMAIL'
    : provider === '163'
      ? 'MAIL_163'
      : provider === '163-secondary'
        ? 'MAIL_163_SECONDARY'
        : null;

  if (!prefix) throw new Error(`Unsupported provider: ${provider}`);

  const host = process.env[`${prefix}_IMAP_HOST`];
  const port = Number(process.env[`${prefix}_IMAP_PORT`] || 993);
  const secure = (process.env[`${prefix}_IMAP_SECURITY`] || 'ssl').toLowerCase() !== 'none';
  const user = process.env[`${prefix}_ADDRESS`];
  const pass = process.env[`${prefix}_APP_PASSWORD`];

  if (!user || !pass || !host) throw new Error(`Missing config for ${provider}`);

  const client = new ImapFlow({ host, port, secure, auth: { user, pass }, logger: false });
  await client.connect();
  try {
    await client.mailboxOpen('INBOX');
    const unseen = await client.search({ seen: false });
    if (unseen.length > 0) {
      await client.messageFlagsAdd(unseen, ['\\Seen']);
    }
    console.log(JSON.stringify({ provider, mailbox: user, markedRead: unseen.length }, null, 2));
  } finally {
    await client.logout().catch(() => {});
  }
}

main().catch(err => {
  console.error(err && err.stack ? err.stack : String(err));
  process.exit(1);
});
