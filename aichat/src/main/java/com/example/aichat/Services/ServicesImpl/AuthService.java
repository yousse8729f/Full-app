package com.example.aichat.Services.ServicesImpl;

import com.example.aichat.DTO.AccountDTO;
import com.example.aichat.Repository.UserRepository;
import com.example.aichat.Services.JwtService;
import com.example.aichat.model.User;
import lombok.RequiredArgsConstructor;
import org.springframework.scheduling.annotation.Async;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

@Service
@RequiredArgsConstructor
public class AuthService {
    private final UserRepository userRepository;
    private final JwtService jwtService;
    private final AuthenticationManager authenticationManager;
    @Async
    @Transactional
    public CompletableFuture<String> login(AccountDTO dto) {
        Map<String,Object> claims = new HashMap<>();
        authenticationManager.authenticate(new UsernamePasswordAuthenticationToken(dto.getEmail(), dto.getPassword()));
        User user = userRepository.findByEmail(dto.getEmail()).orElseThrow(()-> new IllegalArgumentException("not found"));
        claims.put("role", user.getRole());
        claims.put("id",user.getId());
        claims.put("verified",user.isVerified());
        claims.put("name",user.getName());
        claims.put("lastname",user.getLastname());
        return CompletableFuture.completedFuture(jwtService.GenerateToken(claims,user));

    }
}
