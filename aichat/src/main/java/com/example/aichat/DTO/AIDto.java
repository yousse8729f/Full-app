package com.example.aichat.DTO;


import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Builder;
import lombok.Data;
import org.springframework.web.multipart.MultipartFile;

import java.util.ArrayList;
import java.util.List;

@Data
public class AIDto {
    @JsonProperty("files")
    private List<String> files = new ArrayList<>();;
    private String text;
    private int conv_id;
    private Long user_id;
}
