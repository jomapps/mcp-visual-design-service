"""Provider factory for managing image generation providers."""

import asyncio
from typing import Any, Dict, List, Optional

from ..config import Settings
from ..providers import BaseProvider, FalProvider, OpenRouterProvider


class ProviderFactory:
    """Factory for creating and managing image generation providers."""

    def __init__(self, settings: Settings) -> None:
        """Initialize provider factory.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self._providers: Dict[str, BaseProvider] = {}
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """Initialize available providers based on configuration."""
        # Initialize FAL provider if API key is available
        if self.settings.fal_api_key:
            self._providers["fal"] = FalProvider(
                api_key=self.settings.fal_api_key,
                default_model=self.settings.fal_text_to_image_model,
                timeout=60,
            )

        # Initialize OpenRouter provider if API key is available
        if self.settings.openrouter_api_key:
            self._providers["openrouter"] = OpenRouterProvider(
                api_key=self.settings.openrouter_api_key,
                default_model=self.settings.openrouter_default_model,
                backup_model=self.settings.openrouter_backup_model,
                timeout=60,
            )

    def get_provider(self, name: Optional[str] = None) -> BaseProvider:
        """Get a provider by name or return the best available.

        Args:
            name: Provider name ("fal" or "openrouter")

        Returns:
            Provider instance

        Raises:
            ValueError: If no providers are available or named provider not found
        """
        if not self._providers:
            raise ValueError("No image generation providers are configured")

        # Return specific provider if requested
        if name:
            if name not in self._providers:
                raise ValueError(f"Provider '{name}' not available")
            return self._providers[name]

        # Return best available provider (prefer FAL, fallback to OpenRouter)
        if "fal" in self._providers:
            return self._providers["fal"]
        elif "openrouter" in self._providers:
            return self._providers["openrouter"]
        else:
            # Return first available provider
            return next(iter(self._providers.values()))

    def get_available_providers(self) -> List[str]:
        """Get list of available provider names.

        Returns:
            List of provider names
        """
        return list(self._providers.keys())

    async def health_check(self) -> Dict[str, str]:
        """Check health of all providers.

        Returns:
            Dictionary mapping provider names to health status
        """
        health_status = {}
        
        # Run health checks in parallel
        health_tasks = [
            self._check_provider_health(name, provider)
            for name, provider in self._providers.items()
        ]
        
        if health_tasks:
            results = await asyncio.gather(*health_tasks, return_exceptions=True)
            
            for (name, _), result in zip(self._providers.items(), results):
                if isinstance(result, Exception):
                    health_status[name] = "error"
                else:
                    health_status[name] = result.status.value
        
        return health_status

    async def _check_provider_health(self, name: str, provider: BaseProvider) -> Any:
        """Check health of a single provider.

        Args:
            name: Provider name
            provider: Provider instance

        Returns:
            Provider health status
        """
        try:
            return await provider.check_health()
        except Exception:
            # Return unhealthy status on exception
            from ..providers.base import ProviderHealth, ProviderStatus
            from datetime import datetime
            
            return ProviderHealth(
                status=ProviderStatus.UNHEALTHY,
                message=f"Health check failed for {name}",
                response_time=None,
                last_check=datetime.utcnow().isoformat(),
                metadata={"provider": name},
            )

    def get_supported_models(self, provider_name: Optional[str] = None) -> List[str]:
        """Get supported models for a provider or all providers.

        Args:
            provider_name: Optional provider name

        Returns:
            List of supported models
        """
        if provider_name:
            if provider_name not in self._providers:
                return []
            return self._providers[provider_name].get_supported_models()
        
        # Return models from all providers
        all_models = []
        for provider in self._providers.values():
            all_models.extend(provider.get_supported_models())
        
        # Remove duplicates while preserving order
        seen = set()
        unique_models = []
        for model in all_models:
            if model not in seen:
                seen.add(model)
                unique_models.append(model)
        
        return unique_models

    def get_supported_styles(self, provider_name: Optional[str] = None) -> List[str]:
        """Get supported styles for a provider or all providers.

        Args:
            provider_name: Optional provider name

        Returns:
            List of supported styles
        """
        if provider_name:
            if provider_name not in self._providers:
                return []
            return self._providers[provider_name].get_supported_styles()
        
        # Return styles from all providers
        all_styles = []
        for provider in self._providers.values():
            all_styles.extend(provider.get_supported_styles())
        
        # Remove duplicates while preserving order
        seen = set()
        unique_styles = []
        for style in all_styles:
            if style not in seen:
                seen.add(style)
                unique_styles.append(style)
        
        return unique_styles