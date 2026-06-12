package com.example.aichat.Controller;
import com.example.aichat.DTO.AccountDTO;
import com.example.aichat.DTO.ApiResponse;
import com.example.aichat.DTO.EmailVerifDto;
import com.example.aichat.DTO.UserDto;
import com.example.aichat.Services.EmailVerificationService;
import com.example.aichat.Services.ServicesImpl.AuthService;
import com.example.aichat.Services.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executor;

@CrossOrigin(origins = "http://localhost:4200")
@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class Authcontroller {
    private final AuthService authService;
    private final UserService userService;
    private final EmailVerificationService emailVerificationService;
    private final Executor taskExecutor;

    private ResponseEntity<ApiResponse> helperfn(String jwt, String badMsg, String goodMsg) {

        boolean success = jwt != null && !jwt.isBlank();


        ApiResponse response = ApiResponse.builder()
                .success(success)
                .message(success ? goodMsg : badMsg)
                .jwt(success ? jwt : null)
                .build();



        return ResponseEntity
                .status(success ? HttpStatus.OK : HttpStatus.UNAUTHORIZED)
                .body(response);
    }

    @PostMapping("/login")
    public CompletableFuture<ResponseEntity<ApiResponse>>Login(@RequestBody AccountDTO dto){

            return authService.login(dto)
                    .thenApply(jwt -> {

                       return helperfn(jwt, "could not login", "you are login");
                    });






    }
    @PostMapping("/register")
    public CompletableFuture<ResponseEntity<ApiResponse>> Register(@RequestBody UserDto dto){

        return userService.create_user(dto)
                .thenCompose(jwt -> {

                    if(jwt == null || jwt.isEmpty()){
                        return CompletableFuture.completedFuture(
                                helperfn(jwt,"you are not register","you are register")
                        );
                    }

                    return emailVerificationService.create_Verif(dto.getEmail())
                            .thenApply(ev ->
                                    helperfn(jwt,"you are not register","you are register")
                            );
                });
    }

    @PostMapping("/emailverif")
    public CompletableFuture<ResponseEntity<ApiResponse>> verifyEmail(@RequestBody EmailVerifDto dto) {
        System.out.println("Received Email: " + dto.getEmail()); // Is this null?
        System.out.println("Received Code: " + dto.getCode());
        return emailVerificationService.verifycode(dto.getEmail(), dto.getCode())
                .thenApply(jwt -> {
                    if (jwt == null || jwt.isEmpty()) {

                        return ResponseEntity.ok(ApiResponse.builder()
                                .success(false)
                                .message("Invalid verification code")
                                .build());
                    }
                    return helperfn(jwt, "Verification failed", "You are verified!");
                });
    }

    @PostMapping("/resend")
    public CompletableFuture<Void> post(@RequestParam String email) {
        return emailVerificationService.create_Verif(email).thenAccept(vl-> new ResponseEntity<>("send again",HttpStatus.ACCEPTED));
        
    }

    @GetMapping("/test")
    public CompletableFuture<String> get(Authentication authentication, @AuthenticationPrincipal UserDetails userde) {
        System.out.println("Username: " + authentication.getName());
        System.out.println("Authorities: " + authentication.getAuthorities());
        System.out.println(userde.getAuthorities());

        return CompletableFuture.supplyAsync(() -> {
            System.out.println("Username: " + authentication.getName());
            return "ok";
        }, taskExecutor);
    }


}
