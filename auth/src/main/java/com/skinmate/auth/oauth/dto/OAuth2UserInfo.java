package com.skinmate.auth.oauth.dto;

// OAuth2 제공자별 사용자 정보 추상화 인터페이스
public interface OAuth2UserInfo {
    
    // OAuth 제공자 (google, kakao)
    String getProvider();
    
    // OAuth ID (소셜 로그인에서 제공하는 고유 ID)
    String getOAuthId();
    
    // 이름
    String getName();
    
    // 이메일
    String getEmail();
}

