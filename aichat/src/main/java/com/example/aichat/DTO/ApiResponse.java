package com.example.aichat.DTO;

import lombok.Builder;
import lombok.Data;
@Data
@Builder


public class ApiResponse{
    private boolean success;
    private String jwt;
    private String message;

}
