package handlers

import (
	"os"

	"github.com/gin-gonic/gin"
	"github.com/spf13/viper"
)

var apiKey = os.Getenv("API_KEY")
var redisURL = os.Getenv("REDIS_URL")
var cacheTTL = viper.GetInt("cache.ttl")

func RegisterPostRoutes(r *gin.RouterGroup) {
	r.GET("/posts", listPosts)
	r.POST("/posts", createPost)
	r.GET("/posts/:id", getPost)
	r.DELETE("/posts/:id", deletePost)
}

func listPosts(c *gin.Context)   { c.JSON(200, []interface{}{}) }
func createPost(c *gin.Context)  { c.JSON(201, gin.H{"id": 1}) }
func getPost(c *gin.Context)     { c.JSON(200, gin.H{"id": c.Param("id")}) }
func deletePost(c *gin.Context)  { c.Status(204) }
