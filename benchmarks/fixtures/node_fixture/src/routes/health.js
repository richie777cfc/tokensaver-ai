const express = require("express");
const router = express.Router();

router.get("/", (req, res) => {
  res.json({ status: "ok", uptime: process.uptime() });
});

router.get("/ready", (req, res) => {
  const dbReady = process.env.DATABASE_URL ? true : false;
  res.json({ ready: dbReady });
});

module.exports = { router };
