package com.skinmate.auth.util;

import org.springframework.stereotype.Component;

import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServletResponse;

@Component
public class CookieUtils {
    
    private static final String ACCESS_TOKEN_COOKIE_NAME = "access_token";
    private static final String REFRESH_TOKEN_COOKIE_NAME = "refresh_token";
    private static final int COOKIE_MAX_AGE = 7 * 24 * 60 * 60; // 7일 (초 단위)
    
    // Access Token을 HttpOnly 쿠키로 설정
    public void setAccessTokenCookie(HttpServletResponse response, String accessToken) {
        Cookie cookie = new Cookie(ACCESS_TOKEN_COOKIE_NAME, accessToken);
        cookie.setHttpOnly(true);
        cookie.setSecure(false); // 개발환경에서는 false, 운영환경에서는 true
        cookie.setPath("/");
        cookie.setMaxAge(COOKIE_MAX_AGE);
        response.addCookie(cookie);
    }
    
    // Refresh Token을 HttpOnly 쿠키로 설정
    public void setRefreshTokenCookie(HttpServletResponse response, String refreshToken) {
        Cookie cookie = new Cookie(REFRESH_TOKEN_COOKIE_NAME, refreshToken);
        cookie.setHttpOnly(true);
        cookie.setSecure(false); // 개발환경에서는 false, 운영환경에서는 true
        cookie.setPath("/");
        cookie.setMaxAge(COOKIE_MAX_AGE);
        response.addCookie(cookie);
    }
}
