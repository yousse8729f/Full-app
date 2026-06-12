package com.example.aichat.DTO;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class EmailVerifDto {
    @JsonProperty("email")
    private String email;
    @JsonProperty("code")
    private String code;
}
