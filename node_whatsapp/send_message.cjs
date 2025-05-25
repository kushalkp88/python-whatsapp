// node_whatsapp/send_message.cjs

const { create, ev } = require('@open-wa/wa-automate');
const fs = require('fs');
const path = require('path');

const command = process.argv[2];
const SESSION_PATH = './session';

// Set Chrome/Chromium path: use CHROME_PATH env or default macOS Chrome path
const CHROME_PATH =
  process.env.CHROME_PATH ||
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

// Ensure session directory exists
if (!fs.existsSync(SESSION_PATH)) {
  fs.mkdirSync(SESSION_PATH, { recursive: true });
}

async function startClient() {
  return await create({
    sessionId: 'main-session',
    multiDevice: true,
    sessionDataPath: SESSION_PATH,
    headless: true,
    qrTimeout: 0,
    qrRefreshS: 30,
    useChrome: true,
    executablePath: CHROME_PATH,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });
}


(async () => {
  try {
    if (command === 'send') {
      const phone = process.argv[3];
      const message = process.argv[4] || 'HI';
      const imagePath = process.argv[5] || null;
      if (!phone) {
        console.error('Phone number required');
        process.exit(1);
      }
      const client = await startClient();
      try {
        if (imagePath && fs.existsSync(imagePath)) {
          await client.sendImage(
            `${phone}@c.us`,
            imagePath,
            path.basename(imagePath),
            message
          );
          fs.unlinkSync(imagePath); // Clean up
          console.log('sent:image');
        } else {
          await client.sendText(`${phone}@c.us`, message);
          console.log('sent:text');
        }
      } catch (err) {
        console.error(err.message || err);
        process.exit(1);
      }
      await client.kill();
      process.exit(0);
    }

    if (command === 'qrcode') {
      let qrHandled = false;

      ev.on('qr.**', (qr) => {
        if (!qrHandled) {
          // Output only the raw QR string (no ANSI, no extra text)
          console.log(qr);
          qrHandled = true;
          process.exit(0);
        }
      });

      // Wait for QR code event
      await startClient();

      // If QR not received in 30s, exit with error
      setTimeout(() => {
        if (!qrHandled) {
          console.error('QR code not available');
          process.exit(1);
        }
      }, 30000);
    }

    if (command === 'changesession') {
      const client = await startClient();
      try {
        await client.logout();
        await client.kill();
        console.log('session:reset');
      } catch (err) {
        console.error(err.message || err);
        process.exit(1);
      }
      process.exit(0);
    }

    if (command === 'health') {
      console.log('WhatsApp Node worker running!');
      process.exit(0);
    }

    // Unknown command handler
    if (!['send', 'qrcode', 'changesession', 'health'].includes(command)) {
      console.error('Unknown command');
      process.exit(1);
    }
  } catch (err) {
    console.error('Fatal error:', err.message || err);
    process.exit(1);
  }
})();
