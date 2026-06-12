package com.example.aichat.Services;

import java.util.Map;
import java.util.function.Function;

import javax.crypto.SecretKey;

import org.springframework.security.core.userdetails.UserDetails;

import io.jsonwebtoken.Claims;

public interface JwtService {
    static final String SECRET_KEY =  "c5367224729045ea5bb6ae4b76ea8b9db85f02470fdcde71f43226019a73be63";
    Claims ExtractAllclaim(String token);
    <T>T extractClaim(String token,Function<Claims,T>claimResolver);
    String  ExtractUsername(String token);
    String GenerateToken(Map<String,Object> extraClaims , UserDetails userDetails);
    SecretKey Signkey();
    String GenerateTokenKey(UserDetails userDetails);
    boolean isTokenexpired(String Token);
    boolean isTokenValid(String token,UserDetails userDetails);
    String ExtractRole(String token);


}
