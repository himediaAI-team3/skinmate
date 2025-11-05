package com.skinmate.auth.repository;

import com.skinmate.auth.domain.Member;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface MemberRepository extends JpaRepository<Member, Integer> {
    
    /**
     * OAuth Provider와 OAuth ID로 회원 조회
     * @param oauthProvider OAuth 제공자 (google, kakao)
     * @param oauthId OAuth ID
     * @return 회원 정보
     */
    Optional<Member> findByOauthProviderAndOauthId(String oauthProvider, String oauthId);
    
    /**
     * 이메일로 회원 조회
     * @param email 이메일
     * @return 회원 정보
     */
    Optional<Member> findByEmail(String email);
    
    /**
     * ID로 회원 조회
     * @param memberId 회원 ID
     * @return 회원 정보
     */
    Optional<Member> findById(Integer memberId);
}
