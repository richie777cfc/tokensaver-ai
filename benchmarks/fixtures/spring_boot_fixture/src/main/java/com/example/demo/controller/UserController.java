package com.example.demo.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/users")
public class UserController {

    @Value("${app.jwt.secret}")
    private String jwtSecret;

    @GetMapping
    public List<Object> listUsers() {
        return List.of();
    }

    @PostMapping
    public Object createUser() {
        return new Object();
    }

    @GetMapping("/{id}")
    public Object getUser(@PathVariable Long id) {
        return new Object();
    }

    @PutMapping("/{id}")
    public Object updateUser(@PathVariable Long id) {
        return new Object();
    }

    @DeleteMapping("/{id}")
    public void deleteUser(@PathVariable Long id) {
    }
}
