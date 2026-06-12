package com.example.aichat.config;



import java.io.IOException;
import java.util.List;

import jakarta.servlet.DispatcherType;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;

import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;

import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import com.example.aichat.Services.JwtService;
import com.example.aichat.Services.ServicesImpl.CustomUserDetailsService;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;

@Component
@RequiredArgsConstructor
public class JwtSecurityFilter extends OncePerRequestFilter {

    private final CustomUserDetailsService customUserDetailsService;
    private final JwtService jwtService;



    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {

        return request.getDispatcherType() == DispatcherType.ASYNC;
    }
    @Override
    @SuppressWarnings("UnnecessaryReturnStatement")
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        String path = request.getRequestURI();
        if (request.getMethod().equals("OPTIONS")) {
            filterChain.doFilter(request, response);
            return;
        }
        if (path.equals("/api/register") ||
                path.equals("/api/login") ||
                path.equals("/api/emailverif") ||


                path.equals("/api/resend")) {
            filterChain.doFilter(request, response);
            return;
        }

        final String username;
        final String jwt;
        final String AuthHeader = request.getHeader("Authorization");
        if(AuthHeader==null || !AuthHeader.startsWith("Bearer ")){
            filterChain.doFilter(request, response);
            return;

        }
        jwt = AuthHeader.substring(7);
        username = jwtService.ExtractUsername(jwt);
        if(username!=null && SecurityContextHolder.getContext().getAuthentication()==null){
            UserDetails userDetails = customUserDetailsService.loadUserByUsername(username);
            if(jwtService.isTokenValid(jwt, userDetails)){
                System.out.println("TOKEN IS VALID FOR: " + username);


                UsernamePasswordAuthenticationToken auth = new UsernamePasswordAuthenticationToken(userDetails,null,userDetails.getAuthorities());
                System.out.println("User Authorities: " + userDetails.getAuthorities());
                auth.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
                SecurityContextHolder.getContext().setAuthentication(auth);
            }
            else {
                System.out.println("TOKEN IS INVALID OR EXPIRED!");
            }
        }

      filterChain.doFilter(request, response);
    }


}
