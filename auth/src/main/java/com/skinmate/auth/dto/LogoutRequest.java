package com.skinmate.auth.dto;

import lombok.Getter;
import lombok.NoArgsConstructor;

import javax.validation.constraints.NotNull;

@Getter
@NoArgsConstructor
public class LogoutRequest {
    @NotNull(message = "Member ID는 필수입니다.")
    private Long memberId;
}

