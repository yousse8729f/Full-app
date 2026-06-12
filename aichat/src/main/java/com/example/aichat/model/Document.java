package com.example.aichat.model;

import jakarta.activation.MimeType;
import jakarta.persistence.*;
import lombok.*;

@Entity
@Table
@Data
@NoArgsConstructor
@Builder
@AllArgsConstructor
public class Document {
    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE)
    private Integer id;
    private String mimeType;
    private Long size;
    private String path;
    @ManyToOne
    @JoinColumn(name = "user_id")   // foreign key lives here
    private User user;


}
