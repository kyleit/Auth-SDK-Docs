package middleware

import (
	"context"
	"net/http"
	"strings"

	"github.com/gh-platform/core/auth-sdk/client"

	"github.com/gin-gonic/gin"
)

func GinAuthMiddleware(authClient *client.AuthClient) gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": client.ErrNoAuthHeader.Error()})
			return
		}
		parts := strings.Split(authHeader, " ")
		if len(parts) != 2 || !strings.EqualFold(parts[0], "Bearer") {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": client.ErrInvalidAuthType.Error()})
			return
		}
		token := parts[1]
		info, err := authClient.Introspect(context.Background(), token)
		if err != nil {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
			return
		}
		c.Set("user", info)
		c.Next()
	}
}
