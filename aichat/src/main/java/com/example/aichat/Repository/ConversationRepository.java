package com.example.aichat.Repository;

import com.example.aichat.model.Conversation;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ConversationRepository extends JpaRepository<Conversation,Integer> {
    List<Conversation> findAllByUserId(Integer userId);

    List<Conversation> findAllByNameContainingIgnoreCase(String name);
//    void deleteByIdAndUserId(Integer id, Integer userId);
}
