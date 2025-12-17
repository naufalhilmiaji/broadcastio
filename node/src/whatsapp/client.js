const { Client, LocalAuth } = require("whatsapp-web.js");
const qrcode = require("qrcode");
const logger = require("../utils/logger");

const filepath = "./wa_authentication.png"

const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage'
        ]
    },
    takeoverOnConflict: true,
    takeoverTimeoutMs: 0,
});

client.on('qr', qrData => {
    console.log('QR event fired - QR code generated (scan now)');
    qrcode.toFile(filepath, qrData, (err) => {
        if (err) return console.error('Failed to save QR image:', err);
        console.log('QR image saved to', filepath);
    });
});

client.on("ready", () => {
  logger.info("✅ WhatsApp client initialized successfully.");
});

client.on("auth_failure", (msg) => {
  logger.error("Auth failure", { msg });
});

client.on("disconnected", (reason) => {
  logger.warn("WhatsApp disconnected", { reason });
});

module.exports = client;
