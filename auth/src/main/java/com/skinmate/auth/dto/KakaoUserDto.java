package com.skinmate.auth.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class KakaoUserDto {
    private final long id;
    private final String nickname;
}


