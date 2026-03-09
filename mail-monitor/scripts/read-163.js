const { ImapFlow } = require('imapflow');
const { simpleParser } = require('mailparser');

function decodeMimeWord(str) {
  if (!str) return '';
  return str.replace(/=\?([^?]+)\?([BQbq])\?([^?]*)\?=/g, (_, charset, enc, text) => {
    try {
      if (enc.toUpperCase() === 'B') {
        return Buffer.from(text, 'base64').toString(charset);
      }
      const qp = text.replace(/_/g, ' ').replace(/=([0-9A-F]{2})/gi, (m, h) => String.fromCharCode(parseInt(h, 16)));
      return Buffer.from(qp, 'binary').toString(charset);
    } catch {
      return text;
    }
  });
}

function htmlToText(html) {
  return html
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

function trimText(s, max = 220) {
  const text = (s || '').replace(/\s+/g, ' ').trim();
  return text.length > max ? text.slice(0, max) + '…' : text;
}

async function main() {
  const host = process.env.MAIL_163_IMAP_HOST || 'imap.163.com';
  const port = Number(process.env.MAIL_163_IMAP_PORT || 993);
  const secure = (process.env.MAIL_163_IMAP_SECURITY || 'ssl').toLowerCase() !== 'none';
  const user = process.env.MAIL_163_ADDRESS;
  const pass = process.env.MAIL_163_APP_PASSWORD;
  const limit = Number(process.env.MAIL_163_FETCH_LIMIT || 5);

  if (!user || !pass) {
    throw new Error('Missing MAIL_163_ADDRESS or MAIL_163_APP_PASSWORD');
  }

  const client = new ImapFlow({
    host,
    port,
    secure,
    auth: { user, pass },
    logger: false
  });

  await client.connect();
  try {
    await client.mailboxOpen('INBOX');
    const total = client.mailbox.exists || 0;
    const start = Math.max(1, total - limit + 1);
    const messages = [];

    for await (const msg of client.fetch(`${start}:*`, {
      uid: true,
      envelope: true,
      flags: true,
      source: true,
      internalDate: true,
      bodyStructure: true
    })) {
      let text = '';
      let html = '';
      try {
        const parsed = await simpleParser(msg.source);
        text = parsed.text || '';
        html = parsed.html ? String(parsed.html) : '';
      } catch {}

      const subject = decodeMimeWord(msg.envelope?.subject || '');
      const from = (msg.envelope?.from || []).map(x => x.name ? `${x.name} <${x.address}>` : x.address).join(', ');
      const body = trimText(text || htmlToText(html));

      messages.push({
        seq: messages.length + 1,
        uid: msg.uid,
        subject,
        from,
        date: msg.internalDate,
        seen: msg.flags?.has('\\Seen') || false,
        answered: msg.flags?.has('\\Answered') || false,
        draft: msg.flags?.has('\\Draft') || false,
        snippet: body
      });
    }

    console.log(JSON.stringify({
      mailbox: user,
      total,
      returned: messages.length,
      messages
    }, null, 2));
  } finally {
    await client.logout().catch(() => {});
  }
}

main().catch(err => {
  console.error(err && err.stack ? err.stack : String(err));
  process.exit(1);
});
