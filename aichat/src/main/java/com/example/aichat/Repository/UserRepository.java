package com.example.aichat.Repository;

import com.example.aichat.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.Optional;

public interface UserRepository extends JpaRepository<User,Integer> {
  
  Optional<User> findByEmail(@Param("email") String email);
}
