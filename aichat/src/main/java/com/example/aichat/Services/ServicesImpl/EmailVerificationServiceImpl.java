package com.example.aichat.Services.ServicesImpl;

import com.example.aichat.Repository.EmailVerifRepository;
import com.example.aichat.Repository.UserRepository;
import com.example.aichat.Services.EmailVerificationService;
import com.example.aichat.Services.JwtService;
import com.example.aichat.model.EmailVerification;
import com.example.aichat.model.User;
import lombok.RequiredArgsConstructor;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;
import java.util.concurrent.CompletableFuture;

@Service
@RequiredArgsConstructor
public class EmailVerificationServiceImpl  implements EmailVerificationService {
    private final JavaMailSender emailSender;
    private final UserRepository userRepo;
    private final EmailVerifRepository emailVerificationRepo;
    private final JwtService jwtService;
    @Override

    @Transactional
    public CompletableFuture<EmailVerification> create_Verif(String email) {
        User user = userRepo.findByEmail(email).orElseThrow(()-> new RuntimeException("no user found"));
        System.out.println("step 1");
        emailVerificationRepo.deleteAllByUserEmail(email);
        long now = new Date().getTime();
        long end = now+1000*60*60;
        String number = GenerateNumber();
        EmailVerification emailverif = EmailVerification.builder().number(number).userEmail(user.getEmail()).createdAt(now).expiresAt(end).build();
        System.out.println("step 1");
        SimpleMailMessage message = new SimpleMailMessage();
        message.setFrom("youssefmasmoudi05@gmail.com");
        message.setTo(email);
        message.setSubject("here is you code");
        message.setText("verify your accoutn = "+number);
        emailSender.send(message);


        return CompletableFuture.completedFuture( emailVerificationRepo.save(emailverif));

    }

    @Override
    public String GenerateNumber() {
        Random generator = new Random();
        int regNo = generator.nextInt(9999);
        return String.format("%04d",regNo);
    }

    @Override
    @Transactional
    public CompletableFuture<String> verifycode(String email, String code) {
        // We must fetch EVERYTHING inside the same block before returning the future
        User user = userRepo.findByEmail(email.trim())
                .orElseThrow(() -> new RuntimeException("no user found"));

        EmailVerification emailUser = emailVerificationRepo.findEmailVerificationByUserEmail(user.getEmail());

        if (emailUser != null && emailUser.getNumber().equals(code.trim())) {
            user.setVerified(true);
            userRepo.save(user);
            emailVerificationRepo.deleteAllByUserEmail(user.getEmail());

            Map<String, Object> claim = new HashMap<>();
            claim.put("verified", true);
            claim.put("role", user.getRole());
            claim.put("id", user.getId());
            claim.put("name",user.getName());
            claim.put("lastname",user.getLastname());

            return CompletableFuture.completedFuture(jwtService.GenerateToken(claim, user));
        }

        // If we get here, it means emailUser was null or code didn't match
        System.out.println("Verification Failed for: " + email);
        return CompletableFuture.completedFuture("");
    }
}
