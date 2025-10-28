package com.skinmate.auth.config;

import com.skinmate.auth.oauth.service.CustomOAuth2UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;

// Spring Security 설정
@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfig {
    
    private final CustomOAuth2UserService customOAuth2UserService;
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            // CSRF 비활성화
            .csrf().disable()
            
            // 요청 권한 설정
            .authorizeRequests()
                .antMatchers("/oauth2/**", "/login/oauth2/code/**").permitAll()  // OAuth2 엔드포인트 허용
                .anyRequest().authenticated()  // 나머지는 인증 필요
            
            .and()
            
            // OAuth2 로그인 설정
            .oauth2Login()
                .userInfoEndpoint()
                    .userService(customOAuth2UserService);  // 커스텀 OAuth2 서비스 사용
        
        return http.build();
    }
}

