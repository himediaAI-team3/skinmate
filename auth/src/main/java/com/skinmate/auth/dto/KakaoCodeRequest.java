package com.skinmate.auth.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

import javax.validation.constraints.NotBlank;

@Getter
@NoArgsConstructor
@AllArgsConstructor
public class KakaoCodeRequest {
    @NotBlank(message = "인가 코드(code)는 필수입니다.")
    private String code;
}


