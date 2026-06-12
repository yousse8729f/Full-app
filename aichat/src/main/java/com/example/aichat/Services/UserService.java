package com.example.aichat.Services;

import com.example.aichat.model.User;
import com.example.aichat.DTO.UserDto;

import java.util.concurrent.CompletableFuture;

public interface  UserService {
    CompletableFuture<String> create_user(UserDto dto);
    CompletableFuture<User> modify_user(String email,UserDto dto);
    CompletableFuture<User> getuser(Integer id);

    void delete_user(String email);



}
