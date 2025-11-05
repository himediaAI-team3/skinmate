package com.skinmate.auth.domain;

import lombok.*;

import javax.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "member")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
public class Member {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "member_id")
    private Integer memberId;
    
    @Column(name = "oauth_provider")
    private String oauthProvider;
    
    @Column(name = "oauth_id")
    private String oauthId;
    
    @Column(name = "name")
    private String name;
    
    @Column(name = "email")
    private String email;
    
    @Column(name = "role")
    private String role;
    
    @Column(name = "skin_type")
    private String skinType;
    
    // @Column(name = "min_price")
    // private Integer minPrice;
    
    // @Column(name = "max_price")
    // private Integer maxPrice;
    
    @Column(name = "gender")
    private String gender;
    
    @Column(name = "age_group")
    private Integer ageGroup;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @Column(name = "created_id")
    private Integer createdId;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    @Column(name = "updated_id")
    private Integer updatedId;
}
