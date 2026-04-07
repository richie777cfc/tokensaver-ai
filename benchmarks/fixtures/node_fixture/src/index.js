const express = require("express");
const { router: usersRouter } = require("./routes/users");
const { router: healthRouter } = require("./routes/health");

const app = express();
const PORT = process.env.PORT || 3000;
const NODE_ENV = process.env.NODE_ENV || "development";

app.use(express.json());
app.use("/api/health", healthRouter);
app.use("/api/users", usersRouter);

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT} in ${NODE_ENV} mode`);
});
