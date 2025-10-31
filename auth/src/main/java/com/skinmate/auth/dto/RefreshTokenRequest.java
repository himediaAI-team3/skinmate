package com.skinmate.auth.dto;

import lombok.Getter;
import lombok.NoArgsConstructor;

import javax.validation.constraints.NotBlank;

@Getter
@NoArgsConstructor
public class RefreshTokenRequest {
    @NotBlank(message = "Refresh Token은 필수입니다.")
    private String refreshToken;
}

