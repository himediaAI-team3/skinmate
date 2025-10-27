package com.skinmate.auth.oauth.service;

import com.skinmate.auth.domain.Member;
import com.skinmate.auth.oauth.dto.GoogleOAuth2UserInfo;
import com.skinmate.auth.oauth.dto.KakaoOAuth2UserInfo;
import com.skinmate.auth.oauth.dto.OAuth2UserInfo;
import com.skinmate.auth.repository.MemberRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.oauth2.client.userinfo.DefaultOAuth2UserService;
import org.springframework.security.oauth2.client.userinfo.OAuth2UserRequest;
import org.springframework.security.oauth2.core.OAuth2AuthenticationException;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.stereotype.Service;

import java.util.Collections;
import java.util.Map;
import java.util.Optional;

// OAuth2 로그인 처리 서비스
@Service
@RequiredArgsConstructor
public class CustomOAuth2UserService extends DefaultOAuth2UserService {
    
    private final MemberRepository memberRepository;
    
    @Override
    public OAuth2User loadUser(OAuth2UserRequest userRequest) throws OAuth2AuthenticationException {
        // 부모 클래스에서 OAuth2 사용자 정보 가져오기
        OAuth2User oAuth2User = super.loadUser(userRequest);
        
        // OAuth2 제공자 이름 (google, kakao)
        String registrationId = userRequest.getClientRegistration().getRegistrationId();
        
        // OAuth2User 정보를 Map으로 변환
        Map<String, Object> attributes = oAuth2User.getAttributes();
        
        // 제공자별로 사용자 정보 추출
        OAuth2UserInfo userInfo = getOAuth2UserInfo(registrationId, attributes);
        
        // Member 조회 또는 생성
        Member member = findOrCreateMember(userInfo);
        
        // Spring Security OAuth2User 반환
        return new org.springframework.security.oauth2.core.user.DefaultOAuth2User(
            Collections.singleton(new SimpleGrantedAuthority("ROLE_" + member.getRole())),
            attributes,
            "sub" // name attribute key (Google)
        );
    }
    
    // OAuth2 제공자별로 UserInfo 객체 생성
    private OAuth2UserInfo getOAuth2UserInfo(String registrationId, Map<String, Object> attributes) {
        if ("google".equals(registrationId)) {
            return new GoogleOAuth2UserInfo(attributes);
        } else if ("kakao".equals(registrationId)) {
            return new KakaoOAuth2UserInfo(attributes);
        } else {
            throw new OAuth2AuthenticationException("Unsupported provider: " + registrationId);
        }
    }
    
    // Member 조회 또는 생성
    private Member findOrCreateMember(OAuth2UserInfo userInfo) {
        // 이미 존재하는 회원인지 확인
        Optional<Member> memberOpt = memberRepository.findByOauthProviderAndOauthId(
            userInfo.getProvider(),
            userInfo.getOAuthId()
        );
        
        if (memberOpt.isPresent()) {
            // 기존 회원 반환
            return memberOpt.get();
        } else {
            // 신규 회원 생성
            Member newMember = Member.builder()
                .oauthProvider(userInfo.getProvider())
                .oauthId(userInfo.getOAuthId())
                .name(userInfo.getName())
                .email(userInfo.getEmail())
                .role("USER")
                .build();
            
            return memberRepository.save(newMember);
        }
    }
}

