package com.example.aichat.Services.ServicesImpl;

import com.example.aichat.Repository.DocumentRepository;
import com.example.aichat.Repository.UserRepository;
import com.example.aichat.Services.ImagePropperties;
import com.example.aichat.Services.ImageService;
import com.example.aichat.Services.LocalImageStorageService;
import com.example.aichat.model.Document;
import com.example.aichat.model.User;
import lombok.RequiredArgsConstructor;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.concurrent.CompletableFuture;

@Service
@RequiredArgsConstructor
public class ImageServiceImpl implements ImageService {
    private final ImagePropperties propperties;
    private final LocalImageStorageService localImage;
    private final DocumentRepository documentRepo;
    private final UserRepository userRepo;


    @Override
    public void validateFile(MultipartFile file) {

        if(file.isEmpty()){
            return;
        }
        String mimeType = file.getContentType();
        if(mimeType==null||!propperties.allowedMimeTypes().contains(mimeType)){
            throw new IllegalArgumentException("Invalid mime type.");
        }


    }

//    @Override
//    public Document getFileData(long id) {
//        return null;
//    }
    @Async
    @Override
    public CompletableFuture<String> uploadFile(MultipartFile file, String email) throws IOException {
        if (file == null || file.isEmpty()) {
            return CompletableFuture.completedFuture(null);
        }
        validateFile(file);
        String storagePath;
        try(InputStream inputStream = file.getInputStream()) {
            storagePath = localImage.storeFile(inputStream,file.getOriginalFilename());

        }
        User user = userRepo.findByEmail(email).orElseThrow(()->new IllegalArgumentException("errur happen"));
        Document document = Document.builder()
                .mimeType(file.getContentType())
                .path(storagePath)
                .size(file.getSize())
                .user(user)
                .build();

        documentRepo.save(document);
        return CompletableFuture.completedFuture(storagePath) ;

  }
  @Override

  public CompletableFuture<List<String>> uploadFiles(List<MultipartFile> files, String email) throws IOException {
      if (files == null || files.isEmpty()) {
          return CompletableFuture.completedFuture(new ArrayList<>());
      }
      List<CompletableFuture<String>> futures = files.stream()
              .map(file ->{
                  try{
                      return uploadFile(file,email);
                  } catch (IOException e) {
                      throw new RuntimeException(e);
                  }
              })

              .toList();

        return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
                .thenApply(v->futures.stream().map(CompletableFuture::join)
                        .filter(Objects::nonNull)
                        .toList());

  }




}
