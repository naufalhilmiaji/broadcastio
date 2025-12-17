const express = require("express");
const cors = require("cors");

const sendRoute = require("./routes/send");
const healthRoute = require("./routes/health");

const app = express();
app.use(cors());
app.use(express.json());

app.use("/send", sendRoute);
app.use("/health", healthRoute);

module.exports = app;
