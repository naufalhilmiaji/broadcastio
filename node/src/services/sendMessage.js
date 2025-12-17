const fs = require("fs");
const path = require("path");
const { MessageMedia } = require("whatsapp-web.js");
const client = require("../whatsapp/client");


async function sendMessage(to, text, attachment = null) {
  if (!client.info) {
    throw new Error("WhatsApp client not ready");
  }

  const chatId = to.includes("@c.us") ? to : `${to}@c.us`;
  if (attachment) {
    const filePath = attachment.path;
    console.log(`File path: ${filePath}`)

    if (!fs.existsSync(filePath)) {
      throw new Error(`Attachment not found: ${filePath}`);
    }

    const media = MessageMedia.fromFilePath(filePath);

    const options = {};
    if (text) {
      options.caption = text;
    }

    const result = await client.sendMessage(chatId, media, options);
    return {
      message_id: result.id.id
    };
  }

  const result = await client.sendMessage(chatId, text);

  return {
    message_id: result.id.id
  };
}

module.exports = sendMessage;
