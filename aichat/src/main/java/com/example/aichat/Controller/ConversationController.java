package com.example.aichat.Controller;

import com.example.aichat.Repository.ConversationRepository;
import com.example.aichat.model.Conversation;
import lombok.RequiredArgsConstructor;
import org.springframework.graphql.data.method.annotation.Argument;
import org.springframework.graphql.data.method.annotation.MutationMapping;
import org.springframework.graphql.data.method.annotation.QueryMapping;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.CrossOrigin;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@CrossOrigin(origins = "http://localhost:4200")
@Controller
@RequiredArgsConstructor
public class ConversationController {
    private final ConversationRepository conversationRepository;

    @QueryMapping
    public List<Conversation> allConvsByUserId( @Argument Integer user_id){
        return conversationRepository.findAllByUserId(user_id);
    }
    @QueryMapping
    public Conversation ConvById( @Argument Integer conv_id){
        return conversationRepository.findById(conv_id).orElseThrow(()->new IllegalArgumentException("conv not found"));
    }


    @MutationMapping
    public Conversation createconv(@Argument String name , @Argument Integer user_id){
        Conversation conv = Conversation.builder()
                .createdAt(LocalDateTime.now().toString())
                .name(name)
                .userId(user_id)
                .messages(new ArrayList<>())
                .build();

        return conversationRepository.save(conv);
    }
    @MutationMapping
    public Boolean deleteconv(@Argument Integer conv_id) {
        if (conversationRepository.existsById(conv_id)) {
            conversationRepository.deleteById(conv_id);
            return true;
        }
        return false;
    }

}
