package com.skinmate.auth.oauth.dto;

import java.util.Map;

//  Kakao OAuth2 사용자 정보
public class KakaoOAuth2UserInfo implements OAuth2UserInfo {
    
    private final Map<String, Object> attributes;
    private final Map<String, Object> kakaoAccount;
    
    public KakaoOAuth2UserInfo(Map<String, Object> attributes) {
        this.attributes = attributes;
        this.kakaoAccount = (Map<String, Object>) attributes.get("kakao_account");
    }
    
    @Override
    public String getProvider() {
        return "kakao";
    }
    
    @Override
    public String getOAuthId() {
        return attributes.get("id").toString();
    }
    
    @Override
    public String getName() {
        Map<String, Object> profile = (Map<String, Object>) kakaoAccount.get("profile");
        return (String) profile.get("nickname");
    }
    
    @Override
    public String getEmail() {
        return (String) kakaoAccount.get("email");
    }
}

