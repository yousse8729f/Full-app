package com.example.aichat.Services;

import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;
import java.util.concurrent.CompletableFuture;

public interface ImageService {
    void validateFile(MultipartFile file);
    //    Document getFileData(long id);
    CompletableFuture<String> uploadFile(MultipartFile file , String email)throws IOException;
    CompletableFuture<List<String>> uploadFiles(List<MultipartFile> files, String email) throws IOException;
}
