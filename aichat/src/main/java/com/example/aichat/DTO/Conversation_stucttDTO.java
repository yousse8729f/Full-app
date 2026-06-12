package com.example.aichat.DTO;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

import java.util.List;

@Data
public class Conversation_stucttDTO {
    @JsonProperty("conv_id")
    private int conv_id;
    @JsonProperty("conversation_messages")
    private List<?> conversation_messages;
}
