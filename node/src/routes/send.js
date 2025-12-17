const express = require("express");
const sendMessage = require("../services/sendMessage");
const logger = require("../utils/logger");

const router = express.Router();

router.post("/", async (req, res) => {
  if (req.body.metadata?.reference_id === "FORCE_LOGICAL_FAIL") {
    return res.json({
      success: false,
      error: {
        code: "WHATSAPP_REJECTED",
        message: "Forced logical failure for testing"
      }
    });
  }

  const { recipient, content, attachment } = req.body;

  if (!recipient || !content) {
    return res.status(400).json({
      success: false,
      error: "recipient and content are required"
    });
  }

  if (attachment && typeof attachment.path !== "string") {
    return res.status(400).json({
      success: false,
      error: {
        code: "INVALID_ATTACHMENT",
        message: "attachment.path is required"
      }
    });
  }


  try {
    const result = await sendMessage(recipient, content, attachment);
    return res.json({
      success: true,
      provider: "whatsapp",
      ...result
    });
  } catch (err) {
    logger.error("Send failed", { error: err.message });
    return res.status(500).json({
      success: false,
      error: err.message
    });
  }
});

module.exports = router;
