package com.example.aichat.Services;

import java.io.IOException;
import java.io.InputStream;

public interface LocalImageStorageService {
    String storeFile(InputStream inputStream , String originalName) throws IOException;
    String getFileExtension(String fileName);

}
