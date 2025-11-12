package client

import "time"

type LoginResponse struct {
	AccessToken  string    `json:"access_token"`
	TokenType    string    `json:"token_type"`
	ExpiresIn    int64     `json:"expires_in"`
	RefreshToken string    `json:"refresh_token"`
	RefreshExp   time.Time `json:"refresh_expires_at"`
}

type IntrospectResponse struct {
	Active   bool                   `json:"active"`
	Username string                 `json:"username"`
	Exp      int64                  `json:"exp"`
	Iat      int64                  `json:"iat"`
	Sub      string                 `json:"sub"`
	Aud      string                 `json:"aud"`
	Scope    string                 `json:"scope"`
	Roles    []string               `json:"roles"`
	Extra    map[string]interface{} `json:"extra,omitempty"`
}
