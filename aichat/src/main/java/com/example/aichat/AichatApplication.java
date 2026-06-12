package com.example.aichat;

import com.example.aichat.Services.ImagePropperties;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.scheduling.annotation.EnableAsync;

@EnableAsync
@SpringBootApplication
@ConfigurationPropertiesScan
@EnableConfigurationProperties(ImagePropperties.class)
public class AichatApplication {

    public static void main(String[] args) {
        SpringApplication.run(AichatApplication.class, args);
    }

}
