package com.example.demo.controller;

import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/posts")
public class PostController {

    @GetMapping
    public List<Object> listPosts() {
        return List.of();
    }

    @PostMapping
    public Object createPost() {
        return new Object();
    }

    @GetMapping("/{id}")
    public Object getPost(@PathVariable Long id) {
        return new Object();
    }

    @DeleteMapping("/{id}")
    public void deletePost(@PathVariable Long id) {
    }
}
