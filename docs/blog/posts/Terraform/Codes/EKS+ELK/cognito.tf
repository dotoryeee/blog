resource "aws_cognito_user_pool" "main" {
  name = "opensearch-user-pool"
}

resource "aws_cognito_user_pool_domain" "main" {
  domain       = "myopensearch-domain"
  user_pool_id = aws_cognito_user_pool.main.id
}

resource "aws_cognito_identity_pool" "main" {
  identity_pool_name               = "opensearch-identity-pool"
  allow_unauthenticated_identities = false

  cognito_identity_providers {
    client_id               = aws_cognito_user_pool_client.main.id
    provider_name           = aws_cognito_user_pool.main.endpoint
    server_side_token_check = false
  }
}

resource "aws_cognito_user_pool_client" "main" {
  name            = "opensearch-client"
  user_pool_id    = aws_cognito_user_pool.main.id
  generate_secret = false
}
