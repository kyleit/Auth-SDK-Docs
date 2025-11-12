package client

import "errors"

var (
	ErrLoginFailed     = errors.New("login failed")
	ErrRefreshFailed   = errors.New("refresh failed")
	ErrTokenInvalid    = errors.New("invalid token")
	ErrTokenInactive   = errors.New("token inactive")
	ErrNoAuthHeader    = errors.New("authorization header missing")
	ErrInvalidAuthType = errors.New("invalid authorization header type")
)
