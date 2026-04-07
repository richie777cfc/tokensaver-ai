const express = require("express");
const router = express.Router();

const API_SECRET = process.env.API_SECRET;

const users = [];

router.get("/", (req, res) => {
  res.json({ users });
});

router.get("/:id", (req, res) => {
  const user = users.find((u) => u.id === req.params.id);
  if (!user) {
    return res.status(404).json({ error: "User not found" });
  }
  res.json(user);
});

router.post("/", (req, res) => {
  const { name, email } = req.body;
  const newUser = { id: String(users.length + 1), name, email };
  users.push(newUser);
  res.status(201).json(newUser);
});

router.put("/:id", (req, res) => {
  const user = users.find((u) => u.id === req.params.id);
  if (!user) {
    return res.status(404).json({ error: "User not found" });
  }
  Object.assign(user, req.body);
  res.json(user);
});

router.delete("/:id", (req, res) => {
  const index = users.findIndex((u) => u.id === req.params.id);
  if (index === -1) {
    return res.status(404).json({ error: "User not found" });
  }
  users.splice(index, 1);
  res.status(204).send();
});

module.exports = { router };
