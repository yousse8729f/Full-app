package com.example.aichat.config;



import jakarta.servlet.DispatcherType;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.authentication.AuthenticationProvider;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfigurationSource;

import lombok.RequiredArgsConstructor;



@Configuration
@RequiredArgsConstructor
@EnableWebSecurity
public class HttpSecurityConfig {
    private final CorsConfigurationSource corsConfiguartionSource;
    private final JwtSecurityFilter jwtSecurityFilter;
    private final AuthenticationProvider authenticationProvider;

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception{
        http
                .csrf(AbstractHttpConfigurer::disable)
                .cors(cors->cors.configurationSource(corsConfiguartionSource))
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers(HttpMethod.OPTIONS, "/**").permitAll()
                        .dispatcherTypeMatchers(DispatcherType.ASYNC).permitAll()
                    
                        .requestMatchers("/api/login", "/api/register", "/api/emailverif", "/api/resend").permitAll()
                        .requestMatchers("/graphql/**").permitAll()
                        .requestMatchers("/graphiql/**").permitAll()
                       
                        .requestMatchers("/api/test/**").hasAuthority("ROLE_USER")
                        .requestMatchers("/api/message/**").hasAuthority("ROLE_USER")
                        .requestMatchers("/api/upload/**").hasAuthority("ROLE_USER")
                        .requestMatchers("/api/add_conversation/**").hasAuthority("ROLE_USER")
                        .requestMatchers("/api/get_conv/**").hasAuthority("ROLE_USER")
                        .requestMatchers("/api/get_conversations/**").hasAuthority("ROLE_USER")

                        .anyRequest().authenticated()
                )
                .sessionManagement(session->session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .authenticationProvider(authenticationProvider)
                .addFilterBefore(jwtSecurityFilter,UsernamePasswordAuthenticationFilter.class)
                .httpBasic(AbstractHttpConfigurer::disable)
                .formLogin(AbstractHttpConfigurer::disable);
        return http.build();


    }

}
