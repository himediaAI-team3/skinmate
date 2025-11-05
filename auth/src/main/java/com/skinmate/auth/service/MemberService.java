package com.skinmate.auth.service;

import com.skinmate.auth.domain.Member;
import com.skinmate.auth.domain.ResponseCode;
import com.skinmate.auth.exception.CustomException;
import com.skinmate.auth.repository.MemberRepository;
import com.skinmate.auth.dto.KakaoSignupRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.Optional;

@Service
@RequiredArgsConstructor
@Slf4j
@Transactional
public class MemberService {

    private final MemberRepository memberRepository;

    @Transactional(readOnly = true)
    public Optional<Member> findByOauth(String provider, String oauthId) {
        return memberRepository.findByOauthProviderAndOauthId(provider, oauthId);
    }

    public Member createKakaoMember(KakaoSignupRequest request) {
        return memberRepository.save(
                Member.builder()
                        .oauthProvider("kakao")
                        .oauthId(request.getOauthId())
                        .name(request.getNickname())
                        .role("USER")
                        .createdAt(LocalDateTime.now())
                        .createdId(null)
                        .build()
        );
    }

    public Member getOrCreateKakaoMember(KakaoSignupRequest request) {
        return findByOauth("kakao", request.getOauthId())
                .orElseGet(() -> createKakaoMember(request));
    }

    @Transactional(readOnly = true)
    public Member getById(Integer memberId) {
        return memberRepository.findById(memberId)
                .orElseThrow(() -> new CustomException(ResponseCode.MEMBER_NOT_FOUND));
    }
}


