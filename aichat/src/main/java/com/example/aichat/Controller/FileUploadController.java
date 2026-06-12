package com.example.aichat.Controller;


import com.example.aichat.DTO.AIDto;
import com.example.aichat.DTO.AddConvDto;
import com.example.aichat.Services.ImageService;

import com.example.aichat.Services.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;



@RequiredArgsConstructor
@RestController
@RequestMapping("/api")
public class FileUploadController {
    private final ImageService imageService;

    private final UserService user;


        @PostMapping("/upload")
    public CompletableFuture<ResponseEntity<List<String>>>  uploadfiletoai(@RequestParam List<MultipartFile> value,String email) throws IOException {

      return imageService.uploadFiles(value,email)
              .thenApply(filenames-> new ResponseEntity<>(filenames,HttpStatus.ACCEPTED))
              .exceptionally(ex-> new ResponseEntity<>(HttpStatus.NOT_ACCEPTABLE));

}


}
