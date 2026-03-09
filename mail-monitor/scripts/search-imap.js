const { ImapFlow } = require('imapflow');
const { simpleParser } = require('mailparser');

function htmlToText(html) {
  return String(html || '')
    .replace(/<style[\s\S]*?<\/style>/gi, ' ')
    .replace(/<script[\s\S]*?<\/script>/gi, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/\s+/g, ' ')
    .trim();
}

function trimText(s, max = 320) {
  const text = (s || '').replace(/\s+/g, ' ').trim();
  return text.length > max ? text.slice(0, max) + '…' : text;
}

async function main() {
  const provider = (process.argv[2] || '').toLowerCase();
  const query = process.argv.slice(3).join(' ').trim();
  if (!provider || !query) throw new Error('Usage: node scripts/search-imap.js <gmail|163|163-secondary> <query>');

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
    const uids = await client.search({ or: [{ from: query }, { subject: query }] });
    const target = uids.slice(-3);
    const messages = [];
    for await (const msg of client.fetch(target, { uid: true, envelope: true, flags: true, source: true, internalDate: true })) {
      let text = '', html = '';
      try {
        const parsed = await simpleParser(msg.source);
        text = parsed.text || '';
        html = parsed.html ? String(parsed.html) : '';
      } catch {}
      messages.push({
        uid: msg.uid,
        subject: msg.envelope?.subject || '',
        from: (msg.envelope?.from || []).map(x => x.name ? `${x.name} <${x.address}>` : x.address).join(', '),
        date: msg.internalDate,
        seen: msg.flags?.has('\\Seen') || false,
        snippet: trimText(text || htmlToText(html))
      });
    }
    messages.sort((a, b) => new Date(a.date) - new Date(b.date));
    console.log(JSON.stringify({ provider, mailbox: user, query, count: messages.length, messages }, null, 2));
  } finally {
    await client.logout().catch(() => {});
  }
}

main().catch(err => {
  console.error(err && err.stack ? err.stack : String(err));
  process.exit(1);
});
