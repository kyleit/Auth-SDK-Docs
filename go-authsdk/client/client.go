package client

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

type AuthClient struct {
	BaseURL        string
	LoginPath      string
	RefreshPath    string
	IntrospectPath string
	HTTPClient     *http.Client
}

func NewAuthClient(baseURL string) *AuthClient {
	return &AuthClient{
		BaseURL:        baseURL,
		LoginPath:      "/api/v1/auth/login",
		RefreshPath:    "/api/v1/auth/refresh",
		IntrospectPath: "/api/v1/auth/introspect",
		HTTPClient:     &http.Client{Timeout: 10 * time.Second},
	}
}

// Login via REST API
func (c *AuthClient) Login(ctx context.Context, username string, password string, totp *string) (*LoginResponse, error) {
	body := map[string]string{
		"username": username,
		"password": password,
	}
	if totp != nil {
		body["totp"] = *totp
	}

	data, _ := json.Marshal(body)
	req, _ := http.NewRequestWithContext(ctx, "POST", c.BaseURL+c.LoginPath, bytes.NewReader(data))
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("%w: %s", ErrLoginFailed, resp.Status)
	}

	var out LoginResponse
	if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
		return nil, err
	}
	return &out, nil
}

// Refresh token
func (c *AuthClient) Refresh(ctx context.Context, refreshToken string) (*LoginResponse, error) {
	body := map[string]string{"refresh_token": refreshToken}
	data, _ := json.Marshal(body)
	req, _ := http.NewRequestWithContext(ctx, "POST", c.BaseURL+c.RefreshPath, bytes.NewReader(data))
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("%w: %s", ErrRefreshFailed, resp.Status)
	}

	var out LoginResponse
	if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
		return nil, err
	}
	return &out, nil
}

// Introspect token validity
func (c *AuthClient) Introspect(ctx context.Context, token string) (*IntrospectResponse, error) {
	body := map[string]string{"token": token}
	data, _ := json.Marshal(body)
	req, _ := http.NewRequestWithContext(ctx, "POST", c.BaseURL+c.IntrospectPath, bytes.NewReader(data))
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("%w: %s", ErrTokenInvalid, resp.Status)
	}

	var out IntrospectResponse
	if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
		return nil, err
	}

	if !out.Active {
		return nil, ErrTokenInactive
	}

	return &out, nil
}
