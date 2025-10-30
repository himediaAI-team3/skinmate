package com.skinmate.auth.config;

import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;

// Spring Security 설정 (SPA code->token 교환 방식)
@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            // CSRF 비활성화
            .csrf().disable()

            // Stateless 설정 (세션 사용 x)
            .sessionManagement()
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)

            .and()

            // 기본 로그인폼/기본 인증 비활성화
            .formLogin().disable()
            .httpBasic().disable()

            // 요청 권한 설정
            .authorizeRequests()
                .antMatchers("/auth/**").permitAll()  // 인증 API 허용
                .anyRequest().authenticated();  // 나머지는 인증 필요

        return http.build();
    }
}

