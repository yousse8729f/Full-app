package com.example.aichat.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.core.task.AsyncTaskExecutor;
import org.springframework.web.servlet.config.annotation.AsyncSupportConfigurer;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.util.concurrent.Executor;

@Configuration
public class WebConfig implements WebMvcConfigurer {

    private final Executor taskExecutor;

    public WebConfig(Executor taskExecutor) {
        this.taskExecutor = taskExecutor;
    }

    @Override
    public void configureAsyncSupport(AsyncSupportConfigurer configurer) {
      
        configurer.setTaskExecutor((AsyncTaskExecutor) taskExecutor);
        configurer.setDefaultTimeout(360000); // Set a generous timeout (6 mins)
    }
}
