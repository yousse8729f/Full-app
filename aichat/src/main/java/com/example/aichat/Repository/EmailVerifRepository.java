package com.example.aichat.Repository;

import com.example.aichat.model.EmailVerification;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.jpa.repository.query.JpqlQueryBuilder;
import org.springframework.data.repository.query.Param;

public interface EmailVerifRepository extends JpaRepository<EmailVerification,Integer> {
  @Query("select e from EmailVerification e where e.userEmail=:email")
  EmailVerification findEmailVerificationByUserEmail(String email);
  @Modifying
  @Query("delete from EmailVerification e where e.userEmail=:email")
  void deleteAllByUserEmail(@Param("email") String userEmail);
}
