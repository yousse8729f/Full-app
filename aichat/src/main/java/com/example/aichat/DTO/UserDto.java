package com.example.aichat.DTO;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor

public class UserDto {

    private String email;
    private String password;
    @JsonProperty("lastname")
    private String Lastname;
    private String name;


}
