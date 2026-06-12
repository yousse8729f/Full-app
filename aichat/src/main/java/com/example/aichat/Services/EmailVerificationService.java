package com.example.aichat.Services;

import com.example.aichat.model.EmailVerification;

import java.util.concurrent.CompletableFuture;

public interface EmailVerificationService {
    CompletableFuture<EmailVerification> create_Verif(String email);
    String GenerateNumber();
    CompletableFuture<String> verifycode(String email , String code);
}
