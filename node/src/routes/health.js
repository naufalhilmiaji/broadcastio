const express = require("express");
const client = require("../whatsapp/client");

const router = express.Router();

router.get("/", (req, res) => {
  const ready = !!client.info;

  res.json({
    provider: "whatsapp",
    ready,
    timestamp: new Date().toISOString()
  });
});

module.exports = router;
