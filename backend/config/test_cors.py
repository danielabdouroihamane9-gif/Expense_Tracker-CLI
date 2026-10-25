from django.conf import settings
from django.test import SimpleTestCase, override_settings


class CorsConfigurationTests(SimpleTestCase):
    origin = "https://frontend.example"

    def test_cors_middleware_precedes_common_middleware(self):
        self.assertLess(
            settings.MIDDLEWARE.index("corsheaders.middleware.CorsMiddleware"),
            settings.MIDDLEWARE.index("django.middleware.common.CommonMiddleware"),
        )

    @override_settings(
        ALLOWED_HOSTS=["testserver"],
        SECURE_SSL_REDIRECT=False,
        CORS_ALLOWED_ORIGINS=[origin],
    )
    def test_preflight_allows_authorization_for_configured_origin(self):
        response = self.client.options(
            "/api/v1/expenses/",
            HTTP_ORIGIN=self.origin,
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS="authorization,content-type",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Access-Control-Allow-Origin"], self.origin)
        allowed_headers = response["Access-Control-Allow-Headers"].lower()
        self.assertIn("authorization", allowed_headers)
        self.assertIn("content-type", allowed_headers)

    @override_settings(
        ALLOWED_HOSTS=["testserver"],
        SECURE_SSL_REDIRECT=False,
        CORS_ALLOWED_ORIGINS=[origin],
    )
    def test_unconfigured_origin_is_not_allowed(self):
        response = self.client.options(
            "/api/v1/expenses/",
            HTTP_ORIGIN="https://untrusted.example",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS="authorization",
        )

        self.assertNotIn("Access-Control-Allow-Origin", response)

    @override_settings(
        ALLOWED_HOSTS=["testserver"],
        SECURE_SSL_REDIRECT=False,
        CORS_ALLOWED_ORIGINS=[origin],
    )
    def test_content_disposition_is_exposed_to_configured_origin(self):
        response = self.client.get(
            "/api/v1/expenses/",
            HTTP_ORIGIN=self.origin,
        )

        self.assertEqual(response["Access-Control-Allow-Origin"], self.origin)
        self.assertEqual(
            response["Access-Control-Expose-Headers"],
            "Content-Disposition",
        )
