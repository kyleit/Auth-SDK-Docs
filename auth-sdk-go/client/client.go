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
	Tenant         string
	BaseURL        string
	LoginPath      string
	RefreshPath    string
	IntrospectPath string
	HTTPClient     *http.Client
}

// NewAuthClient("demo", "https://auth.example.com")
func NewAuthClient(tenant string, baseURL string) *AuthClient {
	prefix := fmt.Sprintf("/api/v1/%s/auth", tenant)

	return &AuthClient{
		Tenant:         tenant,
		BaseURL:        baseURL,
		LoginPath:      prefix + "/login",
		RefreshPath:    prefix + "/refresh",
		IntrospectPath: prefix + "/introspect",
		HTTPClient:     &http.Client{Timeout: 10 * time.Second},
	}
}

// LoginRequest – đúng chuẩn backend mới
type LoginRequest struct {
	Identifier string  `json:"identifier"`
	ClientID   string  `json:"client_id"`
	Password   string  `json:"password"`
	Totp       *string `json:"totp,omitempty"`
}

func (c *AuthClient) Login(ctx context.Context, body LoginRequest) (*LoginResponse, error) {
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
