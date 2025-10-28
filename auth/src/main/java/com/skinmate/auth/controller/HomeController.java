package com.skinmate.auth.controller;

import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

// 홈 컨트롤러 (테스트용)
@RestController
public class HomeController {
    
    @GetMapping("/")
    public String home(@AuthenticationPrincipal OAuth2User principal) {
        if (principal != null) {
            String name = principal.getAttribute("name");
            return "Welcome, " + name + "! Login successful.";
        }
        return "Welcome to Auth Server. Please <a href='/oauth2/authorization/google'>Login with Google</a> or <a href='/oauth2/authorization/kakao'>Login with Kakao</a>";
    }
    
    @GetMapping("/user")
    public Map<String, Object> user(@AuthenticationPrincipal OAuth2User principal) {
        return principal.getAttributes();
    }
}

