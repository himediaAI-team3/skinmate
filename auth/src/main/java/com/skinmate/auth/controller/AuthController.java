package com.skinmate.auth.controller;

import com.skinmate.auth.dto.ApiResponse;
import com.skinmate.auth.dto.RefreshTokenRequest;
import com.skinmate.auth.dto.KakaoCodeRequest;
import com.skinmate.auth.dto.TokenResponse;
import com.skinmate.auth.domain.ResponseCode;
import com.skinmate.auth.jwt.JwtTokenProvider;
import com.skinmate.auth.service.AuthService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.validation.Valid;

@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
@Slf4j
public class AuthController {
    
    private final AuthService authService;
    private final JwtTokenProvider jwtTokenProvider;

    @PostMapping("/kakao-login")
    public ResponseEntity<ApiResponse<TokenResponse>> kakaoLogin(@Valid @RequestBody KakaoCodeRequest request) {
        TokenResponse tokenResponse = authService.loginWithKakaoCode(request.getCode());
        
        return ResponseEntity.ok(
                ApiResponse.success(
                        ResponseCode.SUCCESS.getCode(),
                        "카카오 로그인 성공",
                        tokenResponse
                )
        );
    }
    
    @PostMapping("/refresh")
    public ResponseEntity<ApiResponse<TokenResponse>> refreshToken(@Valid @RequestBody RefreshTokenRequest request) {
        TokenResponse tokenResponse = authService.refreshAccessToken(request.getRefreshToken());
        
        return ResponseEntity.ok(
                ApiResponse.success(
                        ResponseCode.SUCCESS.getCode(),
                        "토큰 갱신 성공",
                        tokenResponse
                )
        );
    }

    @PostMapping("/logout")
    public ResponseEntity<ApiResponse<Void>> logout(@RequestHeader("Authorization") String authorizationHeader) {
        // Bearer Token에서 memberId 추출
        String token = authorizationHeader.substring(7); // "Bearer " 제거
        Integer memberId = jwtTokenProvider.getMemberIdFromToken(token);
        authService.logout(memberId);
        
        return ResponseEntity.ok(
                ApiResponse.success(
                        ResponseCode.SUCCESS.getCode(),
                        "로그아웃 성공"
                )
        );
    }
}
