package com.example.aichat.Services;

import org.springframework.boot.context.properties.ConfigurationProperties;
import java.util.Set;

@ConfigurationProperties(prefix = "app.image-storage")
public record ImagePropperties(
        String basePath,
        Set<String> allowedMimeTypes
) {}
