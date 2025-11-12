package middleware

import (
	"context"
	"strings"

	"github.com/gh-platform/core/auth-sdk/client"

	"github.com/gofiber/fiber/v2"
)

func FiberAuthMiddleware(authClient *client.AuthClient) fiber.Handler {
	return func(c *fiber.Ctx) error {
		authHeader := c.Get("Authorization")
		if authHeader == "" {
			return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{"error": client.ErrNoAuthHeader.Error()})
		}
		parts := strings.Split(authHeader, " ")
		if len(parts) != 2 || !strings.EqualFold(parts[0], "Bearer") {
			return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{"error": client.ErrInvalidAuthType.Error()})
		}
		token := parts[1]
		info, err := authClient.Introspect(context.Background(), token)
		if err != nil {
			return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{"error": err.Error()})
		}
		c.Locals("user", info)
		return c.Next()
	}
}
