package com.example.aichat.Services.ServicesImpl;

import com.example.aichat.DTO.UserDto;
import com.example.aichat.Repository.UserRepository;
import com.example.aichat.Services.JwtService;
import com.example.aichat.Services.UserService;
import com.example.aichat.model.Role;
import com.example.aichat.model.User;

import lombok.RequiredArgsConstructor;

import org.springframework.scheduling.annotation.Async;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.CompletableFuture;


@RequiredArgsConstructor
@Service
public class UserServiceImpl implements UserService {
    private final UserRepository userRepository;
    private final JwtService jwtService;
    private final PasswordEncoder passwordEncoder;
    @Override
    @Async
    @Transactional
    public CompletableFuture<String> create_user( UserDto dto) {

       if (userRepository.findByEmail(dto.getEmail()).isPresent()) {
           return CompletableFuture.failedFuture(new IllegalArgumentException("existe"));
       }
        Map<String,Object> claim=new HashMap<>();

        User user = User.builder().lastname(dto.getLastname()).name(dto.getName())
                .email(dto.getEmail())
                .password(passwordEncoder.encode(dto.getPassword()))
                .role(Role.USER)

                .build();

        userRepository.save(user);
        claim.put("role", user.getRole());
        claim.put("id",user.getId());
        claim.put("verified",user.isVerified());
        claim.put("name",user.getName());
        claim.put("lastname",user.getLastname());
        String jwt =jwtService.GenerateToken(claim,user);
        return CompletableFuture.completedFuture(jwt);
    }



    @Override
    @Async
    public CompletableFuture<User> modify_user(String email,UserDto dto) {
        User user = userRepository.findByEmail(email).orElseThrow(()-> new IllegalArgumentException("not found"));
       if(!dto.getPassword().isEmpty())user.setPassword(passwordEncoder.encode(dto.getPassword()));
       if(!dto.getLastname().isEmpty())user.setLastname(dto.getLastname());
       if (!dto.getName().isEmpty())user.setName(dto.getName());
       return CompletableFuture.completedFuture(userRepository.save(user));


    }

    @Override
    @Async
    public CompletableFuture<User> getuser(Integer id) {
        return CompletableFuture.completedFuture(userRepository.findById(id).orElseThrow(()->new IllegalArgumentException("jh")));
    }

    @Override
    @Async
    public void delete_user(String email) {
        User user = userRepository.findByEmail(email).orElseThrow(()-> new IllegalArgumentException("not found"));
        userRepository.delete(user);


    }
}
