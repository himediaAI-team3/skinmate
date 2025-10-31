package com.skinmate.auth.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

import javax.validation.constraints.NotBlank;

@Getter
@NoArgsConstructor
@AllArgsConstructor
public class KakaoSignupRequest {
    @NotBlank(message = "oauthId는 필수입니다.")
    private String oauthId;
    private String nickname;
}


