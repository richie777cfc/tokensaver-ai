package main

import (
	"fmt"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/spf13/viper"
)

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	dbHost := viper.GetString("database.host")
	_ = dbHost

	r := gin.Default()

	api := r.Group("/api")
	{
		api.GET("/health", healthHandler)
		api.GET("/users", listUsersHandler)
		api.POST("/users", createUserHandler)
		api.GET("/users/:id", getUserHandler)
		api.PUT("/users/:id", updateUserHandler)
		api.DELETE("/users/:id", deleteUserHandler)
	}

	r.Run(fmt.Sprintf(":%s", port))
}

func healthHandler(c *gin.Context)      { c.JSON(200, gin.H{"status": "ok"}) }
func listUsersHandler(c *gin.Context)    { c.JSON(200, []interface{}{}) }
func createUserHandler(c *gin.Context)   { c.JSON(201, gin.H{"id": 1}) }
func getUserHandler(c *gin.Context)      { c.JSON(200, gin.H{"id": c.Param("id")}) }
func updateUserHandler(c *gin.Context)   { c.JSON(200, gin.H{"id": c.Param("id")}) }
func deleteUserHandler(c *gin.Context)   { c.Status(204) }
