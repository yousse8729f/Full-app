package com.example.aichat.DTO;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class AddConvDto {
    @JsonProperty("user_id")
    private Long user_id;
    private String name;
}
