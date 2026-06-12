package com.example.aichat.Services.ServicesImpl;


import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Function;

import javax.crypto.SecretKey;

import org.aspectj.lang.annotation.Before;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Service;

import com.example.aichat.Services.JwtService;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.io.Decoders;
import io.jsonwebtoken.security.Keys;

@Service
public class JwtServiceImpl implements JwtService {
    private static final String SECRET_KEY = "c5367224729045ea5bb6ae4b76ea8b9db85f02470fdcde71f43226019a73be63";

    @Override
    public Claims ExtractAllclaim(String token) {

        return Jwts.parserBuilder()
                .setSigningKey(Signkey())
                .build()
                .parseClaimsJws(token)
                .getBody();

    }

    @Override
    public <T> T extractClaim(String token, Function<Claims, T> claimResolver) {
        final Claims claims = ExtractAllclaim(token);
        return claimResolver.apply(claims);
    }

    @Override
    public String ExtractUsername(String token) {
        return extractClaim(token, Claims::getSubject);


    }
    @Override
    public String ExtractRole(String token){
        return extractClaim(token,(e)->e.get("role", String.class));
    }

    @Override
    public String GenerateToken(Map<String,Object> extraClaims,UserDetails userdetails) {
        Date now =new Date();
        Date expriresDate = new Date(now.getTime()+1000L*60*60*24);
        return Jwts.builder()
                .setClaims(extraClaims)
                .setSubject(userdetails.getUsername())
                .setIssuedAt(now)

                .setExpiration(expriresDate)
                .signWith(Signkey(),SignatureAlgorithm.HS256)
                .compact();
    }

    @Override
    public SecretKey Signkey() {
        byte[]keybyte = Decoders.BASE64.decode(SECRET_KEY);
        return Keys.hmacShaKeyFor(keybyte);
    }

    @Override
    public String GenerateTokenKey(UserDetails userDetails) {
        Map<String, Object> claims = new HashMap<>();


        String role = userDetails.getAuthorities().stream()
                .map(GrantedAuthority::getAuthority)
                .findFirst()
                .orElse("ROLE_USER")
                .replace("ROLE_", "");

        claims.put("role", role);
        return GenerateToken(claims, userDetails);
    }


    @Override
    public boolean isTokenexpired(String Token) {
        return extractClaim(Token, Claims::getExpiration).before(new Date());

    }

    @Override
    public boolean isTokenValid(String token, UserDetails userDetails) {
        final String email = ExtractUsername(token);
        return email.equals(userDetails.getUsername())&&!isTokenexpired((token));
    }

}
