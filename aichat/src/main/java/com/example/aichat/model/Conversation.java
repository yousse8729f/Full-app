package com.example.aichat.model;

import jakarta.persistence.*;
import lombok.*;
import java.util.List;

@Entity
@Table(name = "conversation")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Conversation {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "conv_id")
    private Integer convId;

    @Column(name = "created_at")
    private String createdAt;

    @Column(name = "name")
    private String name;

    @Column(name = "user_id", nullable = false)
    private Integer userId;

    @OneToMany(mappedBy = "conversation",cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Message> messages;
}
