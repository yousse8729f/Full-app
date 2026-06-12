package com.example.aichat.Services.ServicesImpl;

import com.example.aichat.Services.ImagePropperties;
import com.example.aichat.Services.LocalImageStorageService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.util.StreamUtils;

import javax.imageio.stream.FileCacheImageOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.time.LocalDate;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class LocalImageStorageServiceImpl implements LocalImageStorageService {
    private final ImagePropperties propperties;

    private Path rootPath() {
        return Path.of(propperties.basePath());
    }


    @Override
    public String storeFile(InputStream inputStream, String originalName) throws IOException {
        LocalDate today = LocalDate.now();
        Path dateDirectory  = rootPath().resolve(
                today.getYear()+ File.separator+
                        String.format("%02d",today.getMonthValue())+File.separator+
                        String.format("%02d",today.getDayOfMonth())

        );

        Files.createDirectories(dateDirectory); //create the folder

        String ext = getFileExtension(originalName);
        String StoredName = UUID.randomUUID()+(ext.isEmpty()?"":"."+ext);
        Path filepath = dateDirectory.resolve(StoredName);
        try(OutputStream outputStream = Files.newOutputStream(filepath, StandardOpenOption.CREATE_NEW)) {
            StreamUtils.copy(inputStream,outputStream);

        }



        return rootPath().relativize(filepath).toString();
    }

    @Override
    public String getFileExtension(String fileName) {
        int lastdot = fileName.lastIndexOf(".");
        return lastdot==-1?"":fileName.substring(lastdot+1);
    }
}
