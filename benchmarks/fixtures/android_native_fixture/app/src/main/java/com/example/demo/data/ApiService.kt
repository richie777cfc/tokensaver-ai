package com.example.demo.data

import retrofit2.http.*

interface ApiService {
    @GET("/api/users")
    suspend fun getUsers(): List<User>

    @POST("/api/users")
    suspend fun createUser(@Body user: User): User

    @GET("/api/users/{id}")
    suspend fun getUser(@Path("id") id: String): User

    @DELETE("/api/users/{id}")
    suspend fun deleteUser(@Path("id") id: String)

    @GET("/api/posts")
    suspend fun getPosts(): List<Post>

    @POST("/api/posts")
    suspend fun createPost(@Body post: Post): Post
}

companion object {
    const val BASE_URL = "https://api.example.com/v1"
}
